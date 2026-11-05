"""FPGA stage schema tests only; no synthesis, board run or trusted provenance."""
import copy
import math
import unittest
from tools.validate_fpga_evidence import Rejected, validate

SHA = lambda char: char * 64


def base():
    return dict(
        schema_version=1, stage="SYNTH_ONLY", device="iCE40-candidate",
        rtl_sha256=SHA("a"), toolchain="Yosys/nextpnr test",
        clock_period_ns=10, seed=0,
        resources=dict(lut=3, ff=4, bram=0, dsp=0),
        fmax_hz=None, synth_log_sha256=SHA("b"),
        pnr_log_sha256="", board_log_sha256="")


class StageEvidenceBoundaries(unittest.TestCase):
    def test_stage_is_never_inferred_from_an_early_report(self):
        report = base()
        self.assertEqual(validate(report)["stage"], "SYNTH_ONLY")
        for field, value in (
                ("fmax_hz", 1.0),
                ("pnr_log_sha256", SHA("c")),
                ("board_log_sha256", SHA("d"))):
            with self.subTest(field=field), self.assertRaises(Rejected):
                validate({**report, field: value})

    def test_board_proof_requires_both_route_and_board_receipts(self):
        route = {**base(), "stage": "PLACED_ROUTED",
                 "fmax_hz": 1.0, "pnr_log_sha256": SHA("c")}
        self.assertEqual(validate(route)["stage"], "PLACED_ROUTED")
        board = {**route, "stage": "BOARD_VERIFIED",
                 "board_log_sha256": SHA("d")}
        self.assertEqual(validate(board)["stage"], "BOARD_VERIFIED")
        for changed in (
                {**board, "board_log_sha256": ""},
                {**board, "pnr_log_sha256": ""},
                {**route, "board_log_sha256": SHA("d")},
                {**route, "fmax_hz": None}):
            with self.subTest(changed=changed), self.assertRaises(Rejected):
                validate(changed)

    def test_seed_and_each_resource_have_exclusive_unsigned_32bit_bounds(self):
        maximum = (1 << 32) - 1
        candidate = base()
        candidate["seed"] = maximum
        candidate["resources"] = dict.fromkeys(("lut", "ff", "bram", "dsp"), maximum)
        self.assertTrue(validate(candidate)["admitted_shape"])
        for wrong in (True, -1, maximum + 1, 1.5, "12"):
            with self.subTest(seed=wrong), self.assertRaises(Rejected):
                validate({**base(), "seed": wrong})
            for field in ("lut", "ff", "bram", "dsp"):
                mutation = base()
                mutation["resources"][field] = wrong
                with self.subTest(field=field, value=wrong), self.assertRaises(Rejected):
                    validate(mutation)

    def test_nonfinite_and_nonpositive_clock_and_frequency_fail_closed(self):
        for wrong in (0, -1, False, float("nan"), float("inf"), -float("inf")):
            with self.subTest(clock=wrong), self.assertRaises(Rejected):
                validate({**base(), "clock_period_ns": wrong})
            routed = {**base(), "stage": "PLACED_ROUTED",
                      "pnr_log_sha256": SHA("c"), "fmax_hz": wrong}
            with self.subTest(frequency=wrong), self.assertRaises(Rejected):
                validate(routed)

    def test_printable_labels_and_canonical_hashes_are_required(self):
        for key in ("toolchain", "device"):
            for bad in ("", " ", "test\nspoof", "x" * 257):
                with self.subTest(field=key, bad=bad), self.assertRaises(Rejected):
                    validate({**base(), key: bad})
        for bad in ("A" * 64, "a" * 63, "f" * 65, True):
            with self.subTest(digest=bad), self.assertRaises(Rejected):
                validate({**base(), "rtl_sha256": bad})


if __name__ == "__main__":
    unittest.main()
