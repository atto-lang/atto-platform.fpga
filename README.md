# Oreslang FPGA platform — verified gates, not board-ready

This platform consumes **the byte-exact golden RTL fixture** from [oreslang-source.hdl](https://github.com/ores-truffle-oreslang/oreslang-source.hdl/pull/1) and verifies both source and emitted RTL SHA-256 values. Its own `examples/add8.sv` is an independently authored toolchain smoke and is **not** compiler evidence.

## Automated prototype gates
1. `node tests/check-provenance.mjs` verifies that `generated/add8.ores` and `generated/add8.generated.sv` match the pinned hashes.
2. Icarus executes all 65,536 input combinations against the **pinned compiler-generated HDL artifact**.
3. Yosys maps the same artifact to iCE40 primitive cells.
4. nextpnr places/routes a virtual iCE40 HX8K CT256 design with unconstrained IO; `icepack` emits a **virtual/unprogrammed** bitstream. Successful tools do **not** establish board-safe pin mappings, electrical integrity, timing signoff, or real board execution.

The upstream compiler's GitHub CI separately proves the pinned RTL was generated from Oreslang input. Both CI results should be checked before asserting end-to-end evidence; this repository itself does not run the compiler.

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
