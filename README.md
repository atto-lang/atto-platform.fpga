# Oreslang FPGA platform — verified gates, not board-ready

This platform consumes **the byte-exact golden RTL fixture** from [oreslang-source.hdl](https://github.com/ores-truffle-oreslang/oreslang-source.hdl/pull/1) and verifies both source and emitted RTL SHA-256 values. Its own `examples/add8.sv` is an independently authored toolchain smoke and is **not** compiler evidence.

## Automated prototype gates
1. `node tests/check-provenance.mjs` verifies that `generated/add8.ores` and `generated/add8.generated.sv` match the pinned hashes.
2. Icarus executes all 65,536 input combinations against the **pinned compiler-generated HDL artifact**.
3. Yosys maps the same artifact to iCE40 primitive cells.
4. nextpnr places/routes a virtual iCE40 HX8K CT256 design with unconstrained IO; `icepack` emits a **virtual/unprogrammed** bitstream. Successful tools do **not** establish board-safe pin mappings, electrical integrity, timing signoff, or real board execution.

End-to-end provenance additionally requires independently executed upstream compiler evidence matching these digests. This repository does not run the compiler; pinned artifact hashes alone do not establish that the current compiler emits this RTL.

## Commands
```sh
node tests/check-provenance.mjs
bash tests/wrapper-smoke.sh
mkdir -p outputs
bash scripts/synth-ice40.sh generated/add8.generated.sv ores_add8 outputs/add8.json
nextpnr-ice40 --hx8k --package ct256 --json outputs/add8.json --asc outputs/add8.asc --pcf-allow-unconstrained --freq 12
icepack outputs/add8.asc outputs/add8.bin
```

**Next hardware finish line:** pick an actual board/package, commit its manufacturer-verified PCF constraints and a clock/frequency requirement, run timing; flash through a supported programmer and capture pin-level measurements/serial tests. Without those, status is only virtual implementation.

## Existing generic smoke gate


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


## Two-stage RTL composition host regression

A Rust 2021 runner (`tools/add8_pipeline_gate.rs`) drives Icarus to simulate **two real `ores_add8` modules in sequence** for all 65,536 combinations of the first two input bytes, with a deterministic third byte. It checks both stages against independently computed 8-bit modular arithmetic and fails unless the simulator exits successfully and emits an exact marker. The Rust unit test checks the host oracle. CI installs Icarus and executes both tests. This is simulation of the pinned reference RTL, **not** fresh compiler generation, ASIC timing/signoff, FPGA board validation, or silicon measurement.
