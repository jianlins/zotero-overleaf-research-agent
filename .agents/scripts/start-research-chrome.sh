#!/bin/zsh
set -euo pipefail

# Creates a task-only profile; it never opens or changes the user's normal
# Chrome profile. When changing the port, make the same change in the local
# .codex/config.toml.
PORT=9222

usage() {
  cat <<'EOF'
Usage: .agents/scripts/start-research-chrome.sh [--port PORT]

Starts Google Chrome with a task-only profile and Chrome DevTools Protocol
enabled.
EOF
}

while (( $# )); do
  case "$1" in
    --port)
      [[ $# -ge 2 ]] || { echo "Missing value for --port." >&2; exit 2; }
      PORT="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! [[ "$PORT" =~ '^[0-9]+$' ]] || (( PORT < 1 || PORT > 65535 )); then
  echo "Port must be an integer from 1 through 65535." >&2
  exit 2
fi

PROFILE_DIR="${TMPDIR:-/tmp}/codex-research-chrome-${PORT}"
mkdir -p "$PROFILE_DIR"
open -na "Google Chrome" --args \
  "--remote-debugging-port=${PORT}" \
  --user-data-dir="$PROFILE_DIR" \
  --no-first-run \
  --no-default-browser-check

