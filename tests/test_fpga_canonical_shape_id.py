"""Shape ID is deterministic, field-sensitive and explicitly not provenance proof."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "validate_fpga_evidence.py"
spec = importlib.util.spec_from_file_location("shape_id_validator", TOOL)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
BASE = {
    "schema_version": 1,
    "stage": "SYNTH_ONLY",
    "device": "iCE40 HX",
    "rtl_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
    "toolchain": "yosys-test",
    "clock_period_ns": 10,
    "seed": 1,
    "resources": {
        "lut": 0,
        "ff": 0,
        "bram": 0,
        "dsp": 0
    },
    "fmax_hz": None,
    "synth_log_sha256": "1111111111111111111111111111111111111111111111111111111111111111",
    "pnr_log_sha256": "",
    "board_log_sha256": ""
}


class CanonicalShapeIdTest(unittest.TestCase):
    def test_id_is_stable_across_member_order(self):
        original = copy.deepcopy(BASE)
        reversed_members = dict(reversed(list(BASE.items())))
        self.assertEqual(module.canonical_shape_sha256(original),
                         module.canonical_shape_sha256(reversed_members))
        self.assertEqual(len(module.canonical_shape_sha256(original)), 64)

    def test_changed_shape_changes_id(self):
        changed = copy.deepcopy(BASE)
        changed["toolchain"] = "different-toolchain"
        self.assertNotEqual(module.canonical_shape_sha256(BASE),
                            module.canonical_shape_sha256(changed))

    def test_rejects_invalid_before_hashing(self):
        changed = copy.deepcopy(BASE)
        changed["rtl_sha256"] = "not-a-sha"
        with self.assertRaises(module.Rejected):
            module.canonical_shape_sha256(changed)

    def test_cli_is_opt_in_and_backward_compatible(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "report.json"
            path.write_text(json.dumps(BASE), encoding="utf-8")
            base = subprocess.run([sys.executable, str(TOOL), str(path)],
                                  capture_output=True, text=True, check=True)
            extended = subprocess.run([sys.executable, str(TOOL), "--with-shape-id", str(path)],
                                      capture_output=True, text=True, check=True)
            first, second = json.loads(base.stdout), json.loads(extended.stdout)
            self.assertNotIn("shape_sha256", first)
            self.assertEqual(second.pop("shape_sha256"), module.canonical_shape_sha256(BASE))
            self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
