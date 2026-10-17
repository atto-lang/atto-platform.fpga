# Oreslang FPGA platform — synthesis-only bootstrap

This repository owns **FPGA implementation and testing**, not the Oreslang compiler. Its `examples/add8.sv` is an independently authored toolchain smoke fixture; **not** proof that Oreslang emitted it.

The initial `ice40-hx8k-synth-only` target has no named board/package or pin constraints. The guarded `scripts/synth-ice40.sh` uses Yosys to produce a netlist and explicitly does not perform place/route or produce a bitstream.

Run `bash tests/wrapper-smoke.sh` locally. With Yosys installed: `mkdir -p outputs && bash scripts/synth-ice40.sh examples/add8.sv ores_add8 outputs/add8.json`.

Required follow-ons: board selection, toolchain pinning, nextpnr, timing, programming a real device, and measured output comparison. A green synthesis-only CI is not physical FPGA evidence.

RFC: https://github.com/ores-truffle-oreslang/oreslang-common-source/pull/65
