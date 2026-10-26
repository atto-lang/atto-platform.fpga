#!/usr/bin/env bash
set -euo pipefail
# Synthesis-only. Does not place/route, generate bitstream or prove board execution.
if [[ $# -ne 3 ]]; then echo 'Usage: synth-ice40.sh INPUT.sv TOP OUTPUT.json' >&2; exit 2; fi
rtl=$1; top=$2; out=$3
# Yosys -p parses commands. Keep both source and generated output inside
# the checked-out repository and reject symlink components before invocation.
repo_root="$(pwd -P)"
command -v realpath >/dev/null || { echo 'MISSING_TOOL: realpath' >&2; exit 3; }
validate_relative_path() {
  local path="$1" part cursor=""
  [[ "$path" =~ ^[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*$ ]] || { echo 'Unsafe path' >&2; exit 2; }
  IFS='/' read -r -a parts <<<"$path"
  for part in "${parts[@]}"; do
    [[ "$part" != "." && "$part" != ".." ]] || { echo 'Unsafe path' >&2; exit 2; }
    cursor="${cursor:+$cursor/}$part"
    [[ ! -L "$cursor" ]] || { echo 'Symlink path rejected' >&2; exit 2; }
  done
}
validate_relative_path "$rtl"
validate_relative_path "$out"
if [[ ! "$top" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then echo 'Unsafe module name' >&2; exit 2; fi
if [[ ! -f "$rtl" || -L "$rtl" ]]; then echo 'Missing RTL file' >&2; exit 2; fi
rtl_real="$(realpath -- "$rtl")"
[[ "$rtl_real" == "$repo_root/"* ]] || { echo 'RTL escaped repository root' >&2; exit 2; }
out_parent="$(dirname -- "$out")"
test -d "$out_parent" || { echo 'Missing output directory' >&2; exit 2; }
out_parent_real="$(cd "$out_parent" && pwd -P)"
[[ "$out_parent_real" == "$repo_root" || "$out_parent_real" == "$repo_root/"* ]] ||
  { echo 'Output escaped repository root' >&2; exit 2; }
if ! command -v yosys >/dev/null 2>&1; then echo 'MISSING_TOOL: yosys' >&2; exit 3; fi
if [[ -e "$out" || -L "$out" ]]; then echo 'Refusing overwrite' >&2; exit 2; fi
yosys -Q -T -p "read_verilog -sv $rtl; hierarchy -check -top $top; proc; opt; check -assert; synth_ice40 -top $top -json $out; check -assert; stat"
[[ -s "$out" ]] || { echo 'Missing synthesized netlist' >&2; exit 1; }
echo 'FPGA_SYNTH_ONLY_PASS'
