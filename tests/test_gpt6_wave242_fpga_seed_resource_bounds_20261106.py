"""Host-only FPGA resource/seed numeric admission, not synthesis or board proof."""
import copy
import math
import unittest

from tools.validate_fpga_evidence import Rejected, validate
from test_fpga_evidence import BASE

MAX_U32 = (1 << 32) - 1


class FpgaSeedResourceBoundsWave242(unittest.TestCase):
    def rejects(self, candidate):
        with self.assertRaises(Rejected):
            validate(candidate)

    def test_seed_exact_limits_and_reject_noninteger(self):
        for seed in (0, MAX_U32):
            self.assertTrue(validate(dict(copy.deepcopy(BASE), seed=seed))["admitted_shape"])
        for seed in (True, False, -1, MAX_U32 + 1, 1.0, "1", 10 ** 1000):
            with self.subTest(seed=repr(seed)):
                self.rejects(dict(copy.deepcopy(BASE), seed=seed))

    def test_every_resource_counter_is_exact_uint32(self):
        for name in ("lut", "ff", "bram", "dsp"):
            good = copy.deepcopy(BASE)
            good["resources"][name] = MAX_U32
            self.assertTrue(validate(good)["admitted_shape"])
            for value in (-1, MAX_U32 + 1, True, 1.0, "1", 10 ** 1000):
                bad = copy.deepcopy(BASE)
                bad["resources"][name] = value
                with self.subTest(name=name, value=repr(value)):
                    self.rejects(bad)

    def test_clock_requires_finite_positive_number(self):
        for clock in (0, -1, True, False, math.nan, math.inf, -math.inf, 10 ** 1000):
            with self.subTest(clock=repr(clock)):
                self.rejects(dict(copy.deepcopy(BASE), clock_period_ns=clock))
        self.assertTrue(validate(dict(copy.deepcopy(BASE), clock_period_ns=0.001))["admitted_shape"])

    def test_routed_fmax_cannot_be_nonfinite(self):
        good = dict(copy.deepcopy(BASE), stage="PLACED_ROUTED",
                    pnr_log_sha256="c" * 64, fmax_hz=50000000)
        self.assertEqual(validate(good)["stage"], "PLACED_ROUTED")
        for value in (0, True, False, math.nan, math.inf, -math.inf):
            with self.subTest(fmax=repr(value)):
                self.rejects(dict(good, fmax_hz=value))


if __name__ == "__main__":
    unittest.main()
