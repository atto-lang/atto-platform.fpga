# Oreslang FPGA platform — H0 smoke, not board readiness

This repository consumes RTL under the proposed
[hardware contract](https://github.com/ores-truffle-oreslang/oreslang-common-source/pull/65).
It **does not implement** the Oreslang compiler.

Implemented: self-contained representative \`add8\` RTL fixture, exhaustive
65,536-vector Icarus simulation, generic Yosys synthesis and CI evidence.
\`bash scripts/smoke.sh\` requires actual tools (no fake success).
The fixture does not automatically attest the exact HDL compiler head; the
compiler's own gate must execute separately and match the fixture by digest.

No board, pin file, clock constraint, nextpnr route, timing closure, bitstream,
or device measurements are included. \`scripts/board_gate.sh\` intentionally
fails without a reviewed board-specific recipe. A generic synthesis PASS
must never be described as an FPGA implementation.

Next: choose a named supported FPGA/part/package, legal constraints and
timing budget; implement nextpnr/P&R for that family; attest bitstream hash
and independently exercise real board I/O, with golden-vector comparison.
