#!/bin/zsh
set -euo pipefail

# Creates a task-only profile; it never opens or changes the user's normal
# Chrome profile. Change the port only if 9222 is already occupied, and then
# make the same change in .codex/config.toml.
PROFILE_DIR="${TMPDIR:-/tmp}/codex-research-chrome-9222"
mkdir -p "$PROFILE_DIR"
open -na "Google Chrome" --args \
  --remote-debugging-port=9222 \
  --user-data-dir="$PROFILE_DIR" \
  --no-first-run \
  --no-default-browser-check

