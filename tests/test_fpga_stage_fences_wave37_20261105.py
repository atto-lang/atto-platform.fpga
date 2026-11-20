"""Host-only FPGA stage admission controls; not a synthesis or board-run receipt."""
import copy
import unittest

from tools.validate_fpga_evidence import Rejected, validate

BASE = {
    "schema_version": 1,
    "stage": "SYNTH_ONLY",
    "device": "iCE40 synthetic fixture",
    "rtl_sha256": "a" * 64,
    "toolchain": "Yosys host reference",
    "clock_period_ns": 10,
    "seed": 0,
    "resources": {"lut": 3, "ff": 2, "bram": 0, "dsp": 0},
    "fmax_hz": None,
    "synth_log_sha256": "b" * 64,
    "pnr_log_sha256": "",
    "board_log_sha256": "",
}


class StageEvidenceFences(unittest.TestCase):
    def test_synthesis_cannot_claim_route_or_board_evidence(self):
        self.assertEqual(validate(copy.deepcopy(BASE))["stage"], "SYNTH_ONLY")
        for changes in (
            {"fmax_hz": 1},
            {"pnr_log_sha256": "c" * 64},
            {"board_log_sha256": "d" * 64},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(Rejected):
                    validate({**BASE, **changes})

    def test_routed_proof_needs_finite_frequency_and_pinned_log(self):
        routed = {**BASE, "stage": "PLACED_ROUTED",
                  "pnr_log_sha256": "c" * 64, "fmax_hz": 100_000_000}
        self.assertEqual(validate(routed)["stage"], "PLACED_ROUTED")
        for changes in (
            {"pnr_log_sha256": ""},
            {"fmax_hz": float("inf")},
            {"fmax_hz": 0},
            {"board_log_sha256": "d" * 64},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(Rejected):
                    validate({**routed, **changes})

    def test_noncanonical_digest_and_boolean_seed_are_rejected(self):
        for changes in (
            {"rtl_sha256": "A" * 64},
            {"synth_log_sha256": "b" * 63},
            {"seed": True},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(Rejected):
                    validate({**BASE, **changes})


if __name__ == "__main__":
    unittest.main()
