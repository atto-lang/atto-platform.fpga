#!/usr/bin/env bash
set -euo pipefail
# Synthesis-only. Does not place/route, generate bitstream or prove board execution.
if [[ $# -ne 3 ]]; then echo 'Usage: synth-ice40.sh INPUT.sv TOP OUTPUT.json' >&2; exit 2; fi
rtl=$1; top=$2; out=$3
# Yosys -p parses commands. Reject potential command and path injection.
for p in "$rtl" "$out"; do
 if [[ ! "$p" =~ ^[A-Za-z0-9_./][A-Za-z0-9_./-]*$ ]] || [[ "$p" == *..* ]]; then echo 'Unsafe path' >&2; exit 2; fi
done
if [[ ! "$top" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then echo 'Unsafe module name' >&2; exit 2; fi
if [[ ! -f "$rtl" ]]; then echo 'Missing RTL file' >&2; exit 2; fi
if ! command -v yosys >/dev/null 2>&1; then echo 'MISSING_TOOL: yosys' >&2; exit 3; fi
if [[ -e "$out" ]]; then echo 'Refusing overwrite' >&2; exit 2; fi
yosys -Q -T -p "read_verilog -sv $rtl; hierarchy -check -top $top; proc; opt; check -assert; synth_ice40 -top $top -json $out; check -assert; stat"
[[ -s "$out" ]] || { echo 'Missing synthesized netlist' >&2; exit 1; }
echo 'FPGA_SYNTH_ONLY_PASS'
