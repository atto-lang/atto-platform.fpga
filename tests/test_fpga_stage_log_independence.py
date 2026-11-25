"""Distinct stage-log identities; shape admission is not hardware proof."""
import copy
import unittest
from tools.validate_fpga_evidence import Rejected, validate

A = "a" * 64
B = "b" * 64
C = "c" * 64
D = "d" * 64
BASE = dict(schema_version=1, stage="SYNTH_ONLY", device="iCE40",
            rtl_sha256=A, toolchain="Yosys + nextpnr",
            clock_period_ns=10, seed=42,
            resources=dict(lut=2, ff=1, bram=0, dsp=0),
            fmax_hz=None, synth_log_sha256=B,
            pnr_log_sha256="", board_log_sha256="")

class StageReportIdentityTests(unittest.TestCase):
    def test_route_requires_distinct_tool_report_digests(self):
        routed = {**copy.deepcopy(BASE), "stage": "PLACED_ROUTED",
                  "fmax_hz": 98_000_000, "pnr_log_sha256": C}
        self.assertEqual(validate(routed)["stage"], "PLACED_ROUTED")
        with self.assertRaisesRegex(Rejected, "distinct"):
            validate({**routed, "pnr_log_sha256": B})

    def test_board_requires_third_distinct_report_digest(self):
        board = {**copy.deepcopy(BASE), "stage": "BOARD_VERIFIED",
                 "fmax_hz": 98_000_000,
                 "pnr_log_sha256": C, "board_log_sha256": D}
        self.assertEqual(validate(board)["stage"], "BOARD_VERIFIED")
        for reused in (B, C):
            with self.subTest(reused=reused):
                with self.assertRaisesRegex(Rejected, "distinct"):
                    validate({**board, "board_log_sha256": reused})

    def test_stage_claims_not_authenticated_by_distinct_digests(self):
        board = {**BASE, "stage": "BOARD_VERIFIED", "fmax_hz": 98_000_000,
                 "pnr_log_sha256": C, "board_log_sha256": D}
        result = validate(board)
        self.assertIn("independent artifact verification", result["note"])

if __name__ == "__main__":
    unittest.main()
