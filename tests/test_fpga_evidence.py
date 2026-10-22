import copy
import unittest
from tools.validate_fpga_evidence import validate, Rejected

BASE = dict(schema_version=1,stage="SYNTH_ONLY",device="iCE40-class target",
 rtl_sha256="a"*64,toolchain="Yosys + nextpnr (illustrative version)",
 clock_period_ns=10,seed=0,resources=dict(lut=123,ff=34,bram=0,dsp=0),
 fmax_hz=None,synth_log_sha256="b"*64,pnr_log_sha256="",board_log_sha256="")


class EvidenceTest(unittest.TestCase):
 def reject(self, **patch):
  candidate={**copy.deepcopy(BASE),**patch}
  with self.assertRaises(Rejected):
   validate(candidate)

 def test_synthesis_does_not_imply_timing(self):
  self.assertEqual(validate(copy.deepcopy(BASE))["stage"],"SYNTH_ONLY")
  self.reject(fmax_hz=100000000)
  self.reject(board_log_sha256="c"*64)
  self.reject(synth_log_sha256="")

 def test_route_needs_tool_provenance_and_clock(self):
  self.reject(stage="PLACED_ROUTED")
  good={**BASE,"stage":"PLACED_ROUTED","pnr_log_sha256":"c"*64,
        "fmax_hz":98000000}
  self.assertEqual(validate(good)["stage"],"PLACED_ROUTED")
  self.reject(**{**good,"clock_period_ns":0})
  self.reject(**{**good,"fmax_hz":float("nan")})

 def test_board_is_separate_stage(self):
  good={**BASE,"stage":"BOARD_VERIFIED","pnr_log_sha256":"c"*64,
        "board_log_sha256":"d"*64,"fmax_hz":98000000}
  self.assertEqual(validate(good)["stage"],"BOARD_VERIFIED")
  self.reject(**{**good,"board_log_sha256":""})

 def test_no_boolean_or_fake_resource_data(self):
  self.reject(seed=True)
  self.reject(resources={"lut":True,"ff":0,"bram":0,"dsp":0})
  self.reject(rtl_sha256="main")


 def test_oversized_integer_rejects_cleanly(self):
  self.reject(clock_period_ns=10**1000)

if __name__=="__main__":
 unittest.main()
