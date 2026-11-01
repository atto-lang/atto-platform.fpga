#!/usr/bin/env bash
set -euo pipefail
for x in iverilog vvp yosys sha256sum; do
  command -v "$x" >/dev/null || { echo "REQUIRED_TOOL_MISSING: $x" >&2; exit 2; }
done
mkdir -p build
iverilog -g2012 -s add8_tb -o build/sim fixtures/add8.v fixtures/add8_tb.sv
vvp build/sim | tee build/simulation.log
grep -q "PASS: FPGA platform fixture 65536 simulation vectors" build/simulation.log
yosys -Q -T -l build/synthesis.log -p 'read_verilog fixtures/add8.v; synth -top add8; check -assert; stat; write_verilog -noattr build/add8_generic.v'
test -s build/add8_generic.v
# Capture formal gate stdout and its error text without masking a failure.
bash scripts/equivalence_gate.sh fixtures/add8.v build/add8_generic.v 2>&1 | tee build/equivalence-positive.log
test -s build/equivalence-positive.log
bash scripts/test_equivalence_gate.sh
sha256sum fixtures/add8.v build/add8_generic.v > build/fixture-sha256.txt
printf '%s\n' 'PASS: generic technology-neutral FPGA synthesis only (no mapped device, timing or bitstream)'
