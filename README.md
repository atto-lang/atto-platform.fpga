# atto-platform.fpga

Experimental FPGA compilation and acceleration infrastructure for AttoLang.

## Naming migration and language authority

This repository is maintained at [atto-lang/atto-platform.fpga](https://github.com/atto-lang/atto-platform.fpga); use `https://github.com/atto-lang/atto-platform.fpga.git` for Git remotes and canonical `.atto` source examples. The normative language contract is [atto-spec](https://github.com/atto-lang/atto-spec), with executable guest evidence tracked by [atto-platform-conformance](https://github.com/atto-lang/atto-platform-conformance). Follow current ownership, borrowing, effects, actor, and syntax rules there; do not infer implemented features from a README or unexecuted CI.

## Scope

FPGA-target compilation experiments, host interfaces, and hardware validation.

## Portability contract

The AttoLang language contract must remain separate from target-specific capabilities. Document supported toolchains, devices, platform APIs, memory limits, runtime constraints, and unsupported features explicitly.

## Verification

Where feasible, use real devices or representative emulators in addition to host-side tests. Record toolchain versions, target profiles, exact commit SHAs, and execution evidence. A successful build alone is not proof of runtime semantics.

## Development status

This is a statement of intended project responsibilities. Consult source files and CI for verified implementation or release status; do not assume all targets are supported.

## Related projects

- [AttoLang](https://github.com/atto-lang)
- [Target profiles](https://github.com/atto-lang/atto-target-profiles)
- [Platform conformance](https://github.com/atto-lang/atto-platform-conformance)

## Repository ownership and contribution routing

**Belongs here:** FPGA-specific synthesis flow, board profiles, bitstream/host bridging and hardware-in-the-loop validation.

**Belongs elsewhere:** AttoLang HDL syntax/lowering in atto-source.hdl; ASIC-oriented gates in atto-platform.asic; backend-neutral targets in atto-target-profiles.

**Security and portability boundary:** Explicitly bound synthesizable feature set, clock/memory constraints and unsupported concurrency; real board/simulator receipts are distinct from host-only tests.

AttoLang is the canonical project name; new source, examples and documentation use `.atto` and the `atto-lang` repository organization. This README defines scope, not feature readiness.

**Acceptance:** name exact source SHA/tree, runtime/toolchain, positive and negative checks and execution receipt before claiming support. Host-only tests and empty CI steps do not prove guest execution.
