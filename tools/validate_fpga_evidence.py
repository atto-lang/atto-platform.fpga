#!/usr/bin/env python3
"""Fail-closed evidence vocabulary for FPGA synth/P&R/board stages.

Valid shape is not independently verified proof of any reported tool run.
"""
import json
import math
import re
import sys
from pathlib import Path

HEX = re.compile(r"^[0-9a-f]{64}$")
FIELDS = {"schema_version", "stage", "device", "rtl_sha256", "toolchain",
          "clock_period_ns", "seed", "resources", "fmax_hz",
          "synth_log_sha256", "pnr_log_sha256", "board_log_sha256"}
RESOURCE_KEYS = {"lut", "ff", "bram", "dsp"}


class Rejected(ValueError):
    pass


def check(test, error):
    if not test:
        raise Rejected(error)


def sha_or_empty(value):
    return type(value) is str and (not value or HEX.fullmatch(value))


def finite_positive(value):
    return type(value) in (float, int) and math.isfinite(value) and value > 0


def validate(record):
    check(isinstance(record, dict) and set(record) == FIELDS,
          "unexpected/missing FPGA evidence fields")
    check(type(record["schema_version"]) is int and record["schema_version"] == 1,
          "unknown schema")
    stage = record["stage"]
    check(stage in {"SYNTH_ONLY", "PLACED_ROUTED", "BOARD_VERIFIED"}, "unknown stage")
    check(isinstance(record["device"], str) and record["device"].strip(),
          "target device required")
    check(type(record["rtl_sha256"]) is str and HEX.fullmatch(record["rtl_sha256"]),
          "hash exact RTL input")
    toolchain = record["toolchain"]
    check(isinstance(toolchain, str) and 0 < len(toolchain) <= 256,
          "pinned synthesis and placement toolchain required")
    check(finite_positive(record["clock_period_ns"]), "positive clock constraint required")
    check(type(record["seed"]) is int and 0 <= record["seed"] <= 2**32-1,
          "explicit bounded P&R seed required")
    resources = record["resources"]
    check(isinstance(resources, dict) and set(resources) == RESOURCE_KEYS and
          all(type(v) is int and v >= 0 for v in resources.values()),
          "explicit nonnegative FPGA utilization required")
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


def main(argv):
    if len(argv) != 2:
        print("usage: validate_fpga_evidence.py evidence.json", file=sys.stderr)
        return 64
    try:
        path = Path(argv[1])
        if path.stat().st_size > 65536:
            raise Rejected("too large")
        data = json.loads(path.read_text(encoding="utf8"))
        print(json.dumps(validate(data), sort_keys=True))
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"REJECTED: {exc}", file=sys.stderr)
        return 65


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
