"""Independent FPGA synth/route/board digest-stage oracle, host-only.

Enumerates all 3 stages x 8 provenance-presence combinations. No synthesis or
board hardware occurs; this checks that evidence cannot be promoted by a
mismatched combination of stage name and reported log hashes.
"""
from itertools import product
import copy
import unittest

from tools.validate_fpga_evidence import Rejected, validate
from test_fpga_evidence import BASE


class StageReceiptMatrixWave243(unittest.TestCase):
    def test_stage_and_log_presence_cross_product(self):
        stages = ("SYNTH_ONLY", "PLACED_ROUTED", "BOARD_VERIFIED")
        expected = {
            "SYNTH_ONLY": (True, False, False),
            "PLACED_ROUTED": (True, True, False),
            "BOARD_VERIFIED": (True, True, True),
        }
        exercised = 0
        accepted = 0
        for stage in stages:
            for synth, route, board in product((False, True), repeat=3):
                candidate = copy.deepcopy(BASE)
                candidate["stage"] = stage
                candidate["synth_log_sha256"] = "a" * 64 if synth else ""
                candidate["pnr_log_sha256"] = "b" * 64 if route else ""
                candidate["board_log_sha256"] = "c" * 64 if board else ""
                candidate["fmax_hz"] = None if stage == "SYNTH_ONLY" else 25_000_000
                should_accept = (synth, route, board) == expected[stage]
                with self.subTest(stage=stage, synth=synth, route=route, board=board):
                    if should_accept:
                        result = validate(candidate)
                        self.assertTrue(result["admitted_shape"])
                        self.assertEqual(result["stage"], stage)
                        self.assertIn("independent artifact verification", result["note"])
                        accepted += 1
                    else:
                        with self.assertRaises(Rejected):
                            validate(candidate)
                exercised += 1
        self.assertEqual(exercised, 24)
        self.assertEqual(accepted, 3)

    def test_route_and_board_stage_require_positive_fmax_not_generic_zero(self):
        for stage in ("PLACED_ROUTED", "BOARD_VERIFIED"):
            record = copy.deepcopy(BASE)
            record["stage"] = stage
            record["pnr_log_sha256"] = "b" * 64
            record["board_log_sha256"] = "c" * 64 if stage == "BOARD_VERIFIED" else ""
            for rejected in (None, 0, -0.1, True, float("inf")):
                record["fmax_hz"] = rejected
                with self.subTest(stage=stage, fmax=repr(rejected)), self.assertRaises(Rejected):
                    validate(record)


if __name__ == "__main__":
    unittest.main()
