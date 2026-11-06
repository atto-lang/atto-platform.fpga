"""FPGA report parser adversarial byte-boundary and nested-JSON regression.

Only host-side schema admission. These cases are not P&R or FPGA board proof.
"""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import validate_fpga_evidence as gate
from test_fpga_evidence import BASE


class FpgaBoundedReportInvariants(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.report = Path(self.temp.name) / "fpga.json"

    def test_nested_duplicate_resource_key_rejected_before_shape_check(self):
        raw = json.dumps(BASE)
        self.assertIn('"lut": 123', raw)
        self.report.write_text(raw.replace('"lut": 123',
            '"lut": 123, "lut": 4294967295', 1), encoding="utf-8")
        with self.assertRaisesRegex(gate.Rejected, "duplicate JSON member"):
            gate.read_report(self.report)

    def test_exact_max_report_bytes_admitted_and_one_extra_rejected(self):
        raw = json.dumps(BASE).encode("utf-8")
        self.assertLess(len(raw), gate.MAX_REPORT_BYTES)
        self.report.write_bytes(raw + b" " * (gate.MAX_REPORT_BYTES - len(raw)))
        parsed = gate.read_report(self.report)
        self.assertTrue(gate.validate(parsed)["admitted_shape"])
        with self.report.open("ab") as stream:
            stream.write(b" ")
        with self.assertRaisesRegex(gate.Rejected, "exceeds 64 KiB"):
            gate.read_report(self.report)

    def test_short_read_refuses_apparently_clean_valid_json_file(self):
        self.report.write_text(json.dumps(BASE), encoding="utf-8")
        with patch.object(gate.os, "read", return_value=b""):
            with self.assertRaisesRegex(gate.Rejected, "changed during bounded read"):
                gate.read_report(self.report)

    def test_nested_nonstandard_json_constant_cannot_appear_as_receipt(self):
        raw = json.dumps(BASE)
        self.assertIn('"lut": 123', raw)
        self.report.write_text(raw.replace('"lut": 123', '"lut": NaN', 1),
                               encoding="utf-8")
        with self.assertRaisesRegex(gate.Rejected, "nonstandard JSON constant"):
            gate.read_report(self.report)


if __name__ == "__main__":
    unittest.main()
