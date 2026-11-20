"""Host-only FPGA bounded evidence reader: regular-file admission."""
import json
import os
from pathlib import Path
import tempfile
import unittest

from test_fpga_evidence import BASE
from tools.validate_fpga_evidence import Rejected, read_report, validate


class FpgaFileTypeAdmissionWave244(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "proof.json"

    def test_regular_file_accepts_valid_shape_without_board_claim(self):
        self.path.write_text(json.dumps(BASE), encoding="utf-8")
        self.assertEqual(validate(read_report(self.path))["stage"], "SYNTH_ONLY")

    @unittest.skipUnless(os.name == "posix" and hasattr(os, "O_NOFOLLOW"),
                         "requires POSIX no-follow")
    def test_final_component_symlink_denied(self):
        real = Path(self.temp.name) / "real.json"
        real.write_text(json.dumps(BASE), encoding="utf-8")
        self.path.symlink_to(real)
        with self.assertRaises(OSError):
            read_report(self.path)

    @unittest.skipUnless(hasattr(os, "mkfifo") and hasattr(os, "O_NONBLOCK"),
                         "requires POSIX nonblocking FIFO")
    def test_fifo_denied_without_writer(self):
        os.mkfifo(self.path)
        with self.assertRaisesRegex(Rejected, "regular file"):
            read_report(self.path)

    def test_directory_is_not_report_file(self):
        self.path.mkdir()
        with self.assertRaises((Rejected, OSError)):
            read_report(self.path)

    def test_empty_regular_file_is_not_evidence(self):
        self.path.write_bytes(b"")
        with self.assertRaises(ValueError):
            read_report(self.path)


if __name__ == "__main__":
    unittest.main()
