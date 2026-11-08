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

## Repository ownership and migration (2026-11-08)

**Current home:** `ores-truffle-oreslang/oreslang-platform.fpga`, in the Oreslang legacy organization. The public language name is **AttoLang**. Existing repo/CLI/package identifiers and supported `.ores` sources remain compatibility contracts pending separately tested migration.

- **Belongs here:** FPGA target ABI, synthesis-oriented experiments and hardware-specific receipts.
- **Out of scope:** production silicon claims without independent hardware evidence.
- **Organizational split:** [atto-lang](https://github.com/atto-lang) governs the language/compiler/runtime/target/parity ecosystem; [atto-co](https://github.com/atto-co) governs separately owned production cloud infrastructure, tenant management, billing, identity and deployment. Related `atto-*` repositories created independently must not be mistaken for a Git transfer.
- **Proposed initial transfer:** preserve this repository's GitHub numeric ID, original name/history and exact tree in a gated move to `atto-lang/oreslang-platform.fpga`; no first-stage direct `atto-co` move is approved. Later product carve-outs require a new security and owner decision.

**Maintainer procedure:** coordinate in [migration issue #26](https://github.com/ores-truffle-oreslang/.github/issues/26) and consult [migration runbook draft #25](https://github.com/ores-truffle-oreslang/.github/pull/25). Identify source and target administrators, independent security reviewer, exact source commit SHA/tree and numeric repo ID; review branch protections, target permissions, open PRs/issues, tags/releases, workflows/runners, secrets/environments, packages, webhooks/Apps, Pages, submodules and consumers. Never mirror private source as a transfer shortcut. Perform an authorized GitHub ownership transfer, verify unchanged ID/tree/history and restored security, then update dependencies and run exact-head CI with **nonzero executed job steps**. `steps=[]`/`null` is `NOT_EXECUTED`; source-only/host-only runs do not establish compiler-backed AttoLang execution or target certification.
