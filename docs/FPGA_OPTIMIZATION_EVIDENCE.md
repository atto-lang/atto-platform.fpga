# FPGA optimization evidence: pipeline, banking, widths and unrolling

Status: **draft evidence contract**; no FPGA board verification, bitstream validation or speedup is asserted. The current codebase is an experimental platform and existing PRs #1/#2 already address guarded iCE40 synthesis and RTL simulation; do not bypass their fail-closed gates.

## Provenance
Every report must include Oreslang HDL compiler SHA, input .ores/RTL SHA-256, target-profile revision, test fixture, FPGA part/package/speed grade, Yosys/nextpnr versions, liberty/device database if applicable, constraint file SHA, clock input requirements, seed(s), source state and exact build command.

## Verification stages — never collapse into one PASS
1. `RTL_SIMULATION`: reset/backpressure, input-output data and cycle equivalence.
2. `FORMAL_BOUNDED` if available: no missing/duplicated transactions, illegal bank collisions or unsafe unrolling.
3. `GENERIC_SYNTHESIS`: generic cell/LUT estimate only; cannot claim board-ready timing.
4. `TECHNOLOGY_MAP`: device-specific LUT/FF/BRAM/DSP counts.
5. `PLACEMENT_ROUTE`: actual timing report, critical path, achieved Fmax, setup slack, congestion, and constrained clock.
6. `BITSTREAM_GENERATED`, `BOARD_PROGRAMMED`, `BOARD_MEASURED`: separate statuses with actual hardware artifacts and test equipment metadata.

## Benchmark matrix
For each eligible deterministic fixture compare factor-1 baseline, II target (1 vs achievable), bank count (1/2/4), unroll factor (1/2/4) and exact-width vs deliberately wider reference. Capture compile/synthesis/P&R times, resource counts, II, pipeline latency, bytes or elements/cycle, Fmax and estimated steady-state throughput. Use area and Fmax together: II=1 alone is not a speedup if Fmax falls or memory ports conflict.

## Fail-closed conditions
- Unsupported loop/effect/clock/reset or missing/invalid proof => `REJECTED`.
- Missing FPGA toolchain or device file => `UNAVAILABLE`, not PASS.
- Timing failure, design overflow or tool timeout => explicit fail with raw logs; do not promote generic synthesis success.
- Do not publish private HDL/PDK artifacts to public carrier repos; all artifacts require authorized provenance and disclosure policy.

## Delivery
- [ ] Machine-readable reports with normalized units and independent raw artifacts
- [ ] Positive and negative RTL examples, including stall/reset/collision scenarios
- [ ] True device P&R with tool/seed variance and resource budgets
- [ ] No actual board claim absent physical test execution

Tracking: https://github.com/ores-truffle-oreslang/oreslang-platform.fpga/issues/4
