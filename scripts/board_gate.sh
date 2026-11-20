#!/usr/bin/env bash
# Explicit fail-closed gate for a board-specific build; never claim a bitstream
# merely because generic Yosys synthesis succeeded.
set -euo pipefail
: "$BOARD_ID" "$BOARD_CONSTRAINTS" "$BOARD_FAMILY" "$NEXT_PNR_BIN"
test -s "$BOARD_CONSTRAINTS" || { echo "Missing board constraints" >&2; exit 2; }
command -v "$NEXT_PNR_BIN" >/dev/null || { echo "Missing nextpnr tool" >&2; exit 2; }
echo "Board target $BOARD_ID ($BOARD_FAMILY) must supply a reviewed architecture-specific build recipe." >&2
exit 2
