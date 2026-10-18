# FPGA optimization measurement stages — draft

Tracks [issue #4](https://github.com/ores-truffle-oreslang/oreslang-platform.fpga/issues/4),
[HDL optimization issues](https://github.com/ores-truffle-oreslang/oreslang-source.hdl/issues)
and [org performance epic](https://github.com/ores-truffle-oreslang/.github/issues/5).

```sh
python3 tools/validate_fpga_evidence.py examples/synth-only.example.json
python3 -m unittest discover -s tests -p 'test_*.py'
```

This **only validates the shape of supplied evidence**: RTL hash, target device,
toolchain label, clock constraint, seed, LUT/FF/BRAM/DSP utilization, and stage
specific log hashes. `SYNTH_ONLY` must not report placed/routed Fmax or board
verification. `PLACED_ROUTED` requires a P&R log hash and achieved Fmax.
`BOARD_VERIFIED` further requires a board log hash.

The sample contains **fabricated placeholder data for schema documentation**,
not real synthesis evidence; do not publish it as a benchmark. Real reviewers
must recompute hashes, check design constraints, assess timing slack and use
independent RTL simulation plus P&R. An FPGA board result requires actually
running that board, not a simulator, Yosys synthesis or nextpnr output alone.

Next: integrate this gate into the existing synthesis/simulation PRs; record
pipeline II, latency and backpressure; repeat across unroll/width/banking
configurations, seeds and device families. Do not infer ASIC area or silicon
power from FPGA LUTs.
