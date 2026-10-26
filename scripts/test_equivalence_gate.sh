#!/usr/bin/env bash
# Mutate a known truth table entry: formal checker must fail, not just simulate.
set -euo pipefail
mkdir -p build
bad=build/add8_mutant.v
cat > "$bad" <<'EOV'
module add8 (input wire [7:0] a, input wire [7:0] b, output wire [7:0] result);
  assign result = a ^ b;
endmodule
EOV
if bash scripts/equivalence_gate.sh fixtures/add8.v "$bad" > build/equiv-negative.log 2>&1; then
  echo "ERROR: incorrect XOR mutant passed functional equivalence" >&2
  exit 1
fi
grep -Eq 'Unproven|unproven|ERROR|error' build/equiv-negative.log || {
  echo "ERROR: negative gate failed without identifiable equivalence rejection" >&2
  exit 1
}
outside="$(mktemp)"
trap 'rm -f "$outside" build/escape.v' EXIT
cp fixtures/add8.v "$outside"
ln -s "$outside" build/escape.v
if bash scripts/equivalence_gate.sh fixtures/add8.v build/escape.v > build/equiv-symlink.log 2>&1; then
  echo "ERROR: symlinked RTL input escaped admission" >&2
  exit 1
fi
grep -Fq 'symlink RTL path rejected' build/equiv-symlink.log
echo "PASS: mutant and symlink escape rejected by formal gate"
