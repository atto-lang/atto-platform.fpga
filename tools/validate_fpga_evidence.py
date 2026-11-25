#!/usr/bin/env python3
"""Fail-closed evidence vocabulary for FPGA synth/P&R/board stages.

Valid shape is not independently verified proof of any reported tool run.
"""
import json
import hashlib
import os
import stat
import unicodedata
import math
import re
import sys
from pathlib import Path

HEX = re.compile(r"^[0-9a-f]{64}$")
FIELDS = {"schema_version", "stage", "device", "rtl_sha256", "toolchain",
          "clock_period_ns", "seed", "resources", "fmax_hz",
          "synth_log_sha256", "pnr_log_sha256", "board_log_sha256"}
RESOURCE_KEYS = {"lut", "ff", "bram", "dsp"}
MAX_RESOURCE_COUNT = (1 << 32) - 1


class Rejected(ValueError):
    pass


def check(test, error):
    if not test:
        raise Rejected(error)


def sha_or_empty(value):
    return type(value) is str and (not value or HEX.fullmatch(value))


def finite_positive(value):
    return type(value) in (float, int) and 0 < value <= sys.float_info.max and math.isfinite(value)


def safe_label(value):
    # Reject decomposed aliases; isprintable already rejects format controls.
    return (type(value) is str and 0 < len(value) <= 256 and
            bool(value.strip()) and value.isprintable() and
            unicodedata.normalize("NFC", value) == value)


def validate(record):
    check(isinstance(record, dict) and set(record) == FIELDS,
          "unexpected/missing FPGA evidence fields")
    check(type(record["schema_version"]) is int and record["schema_version"] == 1,
          "unknown schema")
    stage = record["stage"]
    check(type(stage) is str and stage in {"SYNTH_ONLY", "PLACED_ROUTED", "BOARD_VERIFIED"}, "unknown stage")
    check(safe_label(record["device"]),
          "bounded printable target device required")
    check(type(record["rtl_sha256"]) is str and HEX.fullmatch(record["rtl_sha256"]),
          "hash exact RTL input")
    toolchain = record["toolchain"]
    check(safe_label(toolchain),
          "bounded printable synthesis and placement toolchain required")
    check(finite_positive(record["clock_period_ns"]), "positive clock constraint required")
    check(type(record["seed"]) is int and 0 <= record["seed"] <= 2**32-1,
          "explicit bounded P&R seed required")
    resources = record["resources"]
    check(isinstance(resources, dict) and set(resources) == RESOURCE_KEYS and
          all(type(v) is int and 0 <= v <= MAX_RESOURCE_COUNT for v in resources.values()),
          "explicit bounded nonnegative FPGA utilization required")
    for key in ("synth_log_sha256", "pnr_log_sha256", "board_log_sha256"):
        check(sha_or_empty(record[key]), f"invalid {key}")
    check(bool(record["synth_log_sha256"]), "synthesis evidence mandatory")
    if stage == "SYNTH_ONLY":
        check(record["fmax_hz"] is None, "generic synthesis cannot claim routed Fmax")
        check(not record["pnr_log_sha256"] and not record["board_log_sha256"],
              "stage conflates synthesis with P&R or board results")
    else:
        check(finite_positive(record["fmax_hz"]), "measured P&R Fmax required")
        check(bool(record["pnr_log_sha256"]), "P&R needs log hash")
        if stage == "BOARD_VERIFIED":
            check(bool(record["board_log_sha256"]), "board verification requires actual board log")
        else:
            check(not record["board_log_sha256"], "board data requires BOARD_VERIFIED stage")
    return {"admitted_shape": True, "stage": stage, "note": "claims still require independent artifact verification"}



MAX_REPORT_BYTES = 65536


def _unique_json_members(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Rejected(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def _reject_non_json_constant(value):
    raise Rejected(f"nonstandard JSON constant: {value}")


def read_report(path):
    """Read only a bounded regular file through one no-follow descriptor.

    Reject FIFO/device reads, final-component symlinks, ambiguous duplicate
    JSON members and nonstandard NaN/Infinity. This is shape admission, not
    provenance authentication or a secure filesystem sandbox.
    """
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_NONBLOCK"):
        raise Rejected("safe regular-file admission unsupported on this host")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode):
            raise Rejected("report must be a regular file")
        if metadata.st_nlink != 1:
            raise Rejected("report must be single-linked")
        if not 0 <= metadata.st_size <= MAX_REPORT_BYTES:
            raise Rejected("report exceeds 64 KiB")
        chunks = []
        remaining = MAX_REPORT_BYTES + 1
        while remaining:
            block = os.read(fd, min(16384, remaining))
            if not block:
                break
            chunks.append(block)
            remaining -= len(block)
        if remaining == 0:
            raise Rejected("report exceeds 64 KiB")
        # Detect concurrent truncation/growth/rewrite during the bounded read.
        # This does not authenticate the producer or defeat every concurrent
        # same-size rewrite, but must not admit a visibly moving file.
        after = os.fstat(fd)
        if (after.st_dev != metadata.st_dev or
                after.st_ino != metadata.st_ino or
                after.st_size != metadata.st_size or
                after.st_nlink != metadata.st_nlink or
                after.st_mode != metadata.st_mode or
                after.st_mtime_ns != metadata.st_mtime_ns or
                after.st_ctime_ns != metadata.st_ctime_ns or
                sum(map(len, chunks)) != metadata.st_size):
            raise Rejected("report changed during bounded read")
    finally:
        os.close(fd)
    return json.loads(b"".join(chunks).decode("utf-8"),
                      object_pairs_hook=_unique_json_members,
                      parse_constant=_reject_non_json_constant)


def canonical_shape_sha256(record):
    """Deterministic ID for a *validated report shape*, NOT authenticated proof.

    Dict member ordering and JSON whitespace cannot change this identity.
    Numeric representation and individual field values are intentionally
    significant. It does not attest to RTL, P&R, silicon or board execution.
    """
    # Hash *only* the serialized snapshot that was actually validated. A
    # mutable dict subclass or concurrent caller may alter record after an
    # initial validate(record); validation-before-serialization can then hash
    # unvalidated content. CLI reports are independent parsed JSON objects.
    try:
        canonical = json.dumps(record, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=True, allow_nan=False).encode("ascii")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise Rejected("non-JSON evidence shape") from exc
    frozen = json.loads(canonical, object_pairs_hook=_unique_json_members,
                        parse_constant=_reject_non_json_constant)
    validate(frozen)
    return hashlib.sha256(canonical).hexdigest()


def main(argv):
    with_shape_id = len(argv) == 3 and argv[1] == "--with-shape-id"
    if len(argv) != 2 and not with_shape_id:
        print("usage: validate_fpga_evidence.py [--with-shape-id] evidence.json", file=sys.stderr)
        return 64
    try:
        path = Path(argv[2] if with_shape_id else argv[1])
        record = read_report(path)
        result = validate(record)
        if with_shape_id:
            result["shape_sha256"] = canonical_shape_sha256(record)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, ValueError, UnicodeError, RecursionError) as exc:
        print(f"REJECTED: {exc}", file=sys.stderr)
        return 65


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
