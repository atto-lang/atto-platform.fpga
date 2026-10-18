"""Adversarial CLI tests: repeated JSON evidence keys must fail closed."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools/validate_fpga_evidence.py"

class DuplicateEvidenceKeysTests(unittest.TestCase):
    def assert_rejected(self, data, field):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            path.write_text(data, encoding="utf8")
            done = subprocess.run([sys.executable, str(VALIDATOR), str(path)],
                                  text=True, capture_output=True, check=False)
        self.assertEqual(done.returncode, 65, done.stdout + done.stderr)
        self.assertIn("duplicate JSON field: " + field, done.stderr)

    def test_duplicate_top_level_authority(self):
        self.assert_rejected('{"stage":"SYNTH_ONLY","stage":"BOARD_VERIFIED"}', "stage")

    def test_duplicate_nested_resource_field(self):
        self.assert_rejected('{"resources":{"lut":1,"lut":2}}', "lut")

if __name__ == "__main__":
    unittest.main()
