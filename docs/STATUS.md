# FPGA readiness
This repo contains an **independent RTL example** and a guarded, iCE40-focused Yosys synthesis flow, not actual Oreslang-generated RTL or a board-level bitstream.
The declared hx8k target has NO board, package, pin constraints, timing target or physical run evidence.
Next: choose actual board and toolchain; add pinned constraints, nextpnr P&R and timing, bitstream, device programming and genuine board output verification.
Do not promote synthesis-only passes as FPGA deployment evidence. Reference: https://github.com/ores-truffle-oreslang/oreslang-common-source/pull/65
