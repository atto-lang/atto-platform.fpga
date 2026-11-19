> **AI agent instructions (organization-wide):** Before working on code, issues, or pull requests, read and follow the [organization `AGENTS.md`](https://github.com/ores-truffle-oreslang/.github/blob/main/AGENTS.md), including its **merge-first stealth-development policy**. Honor any repository-local `AGENTS.md`, explicit holds, and GitHub-enforced rules.

# Oreslang FPGA platform — verified gates, not board-ready

## Oreslang → AttoLang project migration (2026-11-18)

The public language name is **AttoLang** (formerly **Oreslang**). This is the legacy `ores-truffle-oreslang/oreslang-platform.fpga` repository. New corresponding AttoLang work belongs in **[atto-lang/atto-platform.fpga](https://github.com/atto-lang/atto-platform.fpga)**. Do not infer identical Git histories, issues, PRs, execution evidence or completed ownership transfer from matching project names. Board/synthesis descriptions are not evidence of real target execution; require explicit hardware provenance.

The **canonical language specification** is [atto-lang/atto-spec](https://github.com/atto-lang/atto-spec), not an older Oreslang README or historical specification copy. [atto-platform-conformance](https://github.com/atto-lang/atto-platform-conformance) owns portable executed guest tests, [atto-compilers-parity-testing](https://github.com/atto-lang/atto-compilers-parity-testing) owns differential checks, and [atto-common-source](https://github.com/atto-lang/atto-common-source) owns portable `.atto` libraries. Current design targets include `snake_case` names, `borrow!`/`take!`/`copy!`/`copy!!`/`share!`, [implicit borrowing](https://github.com/atto-lang/atto-spec/blob/main/language/implicit-argument-borrow-v1.md), [file/module constants including one-time non-throwing `os.read_env`](https://github.com/atto-lang/atto-spec/blob/main/language/file-module-const-v1.md), and [`<<<`/`>>>`/`ashr` shifts distinct from stream `<<`/`>>`](https://github.com/atto-lang/atto-spec/blob/main/language/bitwise-and-stream-operators-v1.md). These are normative/proposed targets; unsupported syntax must fail closed.

Preserve legacy `.ores` fixtures, historical CLI/package names and ABI/wire contracts until replacements are verified. Do not use Python for new AttoLang scripts/tests/CI; prefer Rust for support tooling. Report exact SHA/tree, toolchain, positive/negative compiled guest runs and explicit failed/unsupported/not-executed states; host-only tests and zero executed Actions steps do not prove guest parity.

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
