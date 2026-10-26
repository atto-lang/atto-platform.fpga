#!/usr/bin/env bash
set -euo pipefail
f=$(mktemp); trap 'rm -f "$f"' EXIT
if bash scripts/synth-ice40.sh 'examples/add8.sv;evil' ores_add8 out.json >"$f" 2>&1; then echo 'injection accepted' >&2; exit 1; fi
grep -q 'Unsafe path' "$f"
if bash scripts/synth-ice40.sh examples/add8.sv 'top;evil' out.json >"$f" 2>&1; then echo 'top injection accepted' >&2; exit 1; fi
grep -q 'Unsafe module' "$f"
if bash scripts/synth-ice40.sh missing.sv ores_add8 out.json >"$f" 2>&1; then echo 'missing input accepted' >&2; exit 1; fi
grep -q 'Missing RTL' "$f"
outside="$(mktemp)"
ln -s "$outside" build-escape.sv
trap 'rm -f "$f" "$outside" build-escape.sv' EXIT
if bash scripts/synth-ice40.sh build-escape.sv ores_add8 out.json >"$f" 2>&1; then echo 'symlink input accepted' >&2; exit 1; fi
grep -q 'Symlink path rejected' "$f"
outside_dir="$(mktemp -d)"
ln -s "$outside_dir" build-escape-dir
trap 'rm -f "$f" "$outside" build-escape.sv build-escape-dir; rm -rf "$outside_dir"' EXIT
if bash scripts/synth-ice40.sh examples/add8.sv ores_add8 build-escape-dir/out.json >"$f" 2>&1; then
  echo 'symlink output parent accepted' >&2
  exit 1
fi
grep -q 'Symlink path rejected' "$f"
echo 'FPGA_WRAPPER_GUARD_PASS'
