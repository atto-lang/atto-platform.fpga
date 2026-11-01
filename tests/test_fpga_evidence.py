import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from tools.validate_fpga_evidence import validate, read_report, Rejected

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



 def test_resource_counters_are_bounded_for_downstream_consumers(self):
  maximum=(1<<32)-1
  good=copy.deepcopy(BASE)
  good["resources"]["lut"]=maximum
  self.assertTrue(validate(good)["admitted_shape"])
  for field in ("lut","ff","bram","dsp"):
   invalid=copy.deepcopy(BASE["resources"])
   invalid[field]=maximum+1
   self.reject(resources=invalid)
   invalid[field]=10**1000
   self.reject(resources=invalid)

 def test_device_and_toolchain_provenance_labels_are_bounded(self):
  for field in ("device","toolchain"):
   self.reject(**{field:"X"*257})
   self.reject(**{field:"trusted\nmalicious"})
   self.reject(**{field:"trusted\x00malicious"})
   self.reject(**{field:" \t "})

 def test_oversized_integer_rejects_cleanly(self):
  self.reject(clock_period_ns=10**1000)

 def test_bounded_file_reader_rejects_mutation_between_stat_calls(self):
  with tempfile.TemporaryDirectory() as directory:
   path=Path(directory)/"proof.json"
   path.write_text(json.dumps(BASE),encoding="utf-8")
   original=os.fstat
   calls=[0]
   def mutate_stat(fd):
    st=original(fd)
    calls[0]+=1
    if calls[0]!=2:
     return st
    return SimpleNamespace(st_dev=st.st_dev,st_ino=st.st_ino,
      st_size=st.st_size,st_mtime_ns=st.st_mtime_ns+1,
      st_ctime_ns=st.st_ctime_ns)
   with patch("tools.validate_fpga_evidence.os.fstat",side_effect=mutate_stat):
    with self.assertRaisesRegex(Rejected,"changed during bounded read"):
     read_report(path)
   self.assertEqual(calls[0],2)

 def test_duplicate_json_evidence_members_rejected_before_shape_admission(self):
  with tempfile.TemporaryDirectory() as directory:
   path=Path(directory)/"duplicate.json"
   raw=json.dumps(BASE)
   path.write_text(raw.replace('"stage": "SYNTH_ONLY"',
        '"stage": "BOARD_VERIFIED", "stage": "SYNTH_ONLY"'),encoding="utf-8")
   with self.assertRaisesRegex(Rejected,"duplicate JSON member"):
    read_report(path)

 def test_file_reader_refuses_invalid_utf8_and_nonstandard_numbers(self):
  with tempfile.TemporaryDirectory() as directory:
   path=Path(directory)/"invalid.json"
   raw=json.dumps(BASE).encode("utf-8").replace(b"iCE40",b"\\xffCE40")
   path.write_bytes(raw)
   with self.assertRaises(UnicodeError):
    read_report(path)
   path.write_text(json.dumps(BASE).replace('"seed": 0','"seed": NaN'),encoding="utf-8")
   with self.assertRaisesRegex(Rejected,"nonstandard JSON constant"):
    read_report(path)


if __name__=="__main__":
 unittest.main()
