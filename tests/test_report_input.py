"""Adversarial CLI/JSON file admission for FPGA evidence reports.

These tests verify input safety and format only, not physical measurements.
"""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

from test_fpga_evidence import BASE
from tools.validate_fpga_evidence import Rejected, main, read_report, validate


class ReportInputTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "report.json"

    def write(self, text):
        self.path.write_bytes(text if isinstance(text, bytes) else text.encode("utf-8"))
        return self.path

    def test_valid_regular_file_and_cli(self):
        self.write(json.dumps(BASE))
        self.assertTrue(validate(read_report(self.path))["admitted_shape"])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(["validator", str(self.path)]), 0)
        self.assertTrue(json.loads(output.getvalue())["admitted_shape"])

    def test_duplicate_top_level_and_nested_members_fail(self):
        report = json.dumps(BASE)
        self.write(report.replace('"schema_version": 1',
                                  '"schema_version": 1, "schema_version": 1', 1))
        with self.assertRaisesRegex(Rejected, "duplicate JSON member"):
            read_report(self.path)
        self.write('{"extra": {"key": 1, "key": 2}}')
        with self.assertRaisesRegex(Rejected, "duplicate JSON member"):
            read_report(self.path)

    def test_nonstandard_json_constant_fails_before_shape_validation(self):
        report = json.dumps(BASE)
        self.assertIn('"clock_period_ns": 10', report)
        self.write(report.replace('"clock_period_ns": 10', '"clock_period_ns": NaN', 1))
        with self.assertRaisesRegex(Rejected, "nonstandard JSON constant"):
            read_report(self.path)

    def test_symlink_refused_without_following(self):
        self.write(json.dumps(BASE))
        alias = self.path.parent / "alias.json"
        alias.symlink_to(self.path)
        with self.assertRaises((OSError, Rejected)):
            read_report(alias)

    def test_nonregular_inputs_fail_without_blocking(self):
        with self.assertRaises(Rejected):
            read_report(self.path.parent)
        if hasattr(os, "mkfifo"):
            os.mkfifo(self.path)
            with self.assertRaises(Rejected):
                read_report(self.path)

    def test_size_and_invalid_utf8_fail(self):
        self.write(b" " * 65537)
        with self.assertRaisesRegex(Rejected, "exceeds 64 KiB"):
            read_report(self.path)
        self.write(b"\\xff")
        with self.assertRaises(UnicodeError):
            read_report(self.path)

    def test_deep_json_fails_with_rejection_exit_not_traceback(self):
        self.write("[" * 2000 + "0" + "]" * 2000)
        with contextlib.redirect_stderr(io.StringIO()) as error:
            self.assertEqual(main(["validator", str(self.path)]), 65)
        self.assertIn("REJECTED:", error.getvalue())

    def test_cli_duplicate_member_denied(self):
        self.write('{"schema_version": 1, "schema_version": 1}')
        with contextlib.redirect_stderr(io.StringIO()) as error:
            self.assertEqual(main(["validator", str(self.path)]), 65)
        self.assertIn("duplicate JSON member", error.getvalue())


if __name__ == "__main__":
    unittest.main()
