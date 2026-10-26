#!/usr/bin/env bash
# Functional formal equivalence of two 8-bit combinational add8 modules.
# This is NOT technology-mapped timing, placement, hardware, or compiler proof.
set -euo pipefail
gold="${1:?golden RTL file required}"
gate="${2:?synthesized netlist file required}"
repo_root="$(pwd -P)"
command -v realpath >/dev/null || { echo "REQUIRED_TOOL_MISSING: realpath" >&2; exit 2; }
validate_rtl_path() {
  local file="$1" part cursor="" resolved
  [[ "$file" =~ ^[a-zA-Z0-9._-]+(/[a-zA-Z0-9._-]+)*$ ]] ||
    { echo "unsafe RTL path" >&2; exit 2; }
  IFS='/' read -r -a parts <<<"$file"
  for part in "${parts[@]}"; do
    [[ "$part" != "." && "$part" != ".." ]] ||
      { echo "path traversal" >&2; exit 2; }
    cursor="${cursor:+$cursor/}$part"
    [[ ! -L "$cursor" ]] || { echo "symlink RTL path rejected" >&2; exit 2; }
  done
  test -f "$file" && test -s "$file" ||
    { echo "missing RTL input: $file" >&2; exit 2; }
  resolved="$(realpath -- "$file")"
  [[ "$resolved" == "$repo_root/"* ]] ||
    { echo "RTL path escaped repository root" >&2; exit 2; }
}
validate_rtl_path "$gold"
validate_rtl_path "$gate"
command -v yosys >/dev/null || { echo "REQUIRED_TOOL_MISSING: yosys" >&2; exit 2; }
mkdir -p build
temp="$(mktemp -d)"
trap 'rm -rf "$temp"' EXIT
cat > "$temp/equiv.ys" <<EOT
read_verilog $gold
prep -top add8
design -stash gold
read_verilog $gate
prep -top add8
design -stash gate
design -copy-from gold -as gold add8
design -copy-from gate -as gate add8
equiv_make gold gate equiv
prep -top equiv
equiv_simple
equiv_status -assert
EOT
yosys -Q -T -l build/equivalence.log -s "$temp/equiv.ys"
echo "PASS: Yosys 8-bit combinational functional equivalence (no physical evidence)"
