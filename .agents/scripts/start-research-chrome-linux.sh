#!/usr/bin/env bash
set -euo pipefail

port=9222
chrome_path=""

usage() {
  cat <<'EOF'
Usage: .agents/scripts/start-research-chrome-linux.sh [--port PORT] [--chrome-path PATH]

Starts Google Chrome or Chromium with a task-only profile and Chrome DevTools
Protocol enabled. Supply --chrome-path when the browser is installed somewhere
nonstandard.
EOF
}

while (($#)); do
  case "$1" in
    --port)
      [[ $# -ge 2 ]] || { echo "Missing value for --port." >&2; exit 2; }
      port="$2"
      shift 2
      ;;
    --chrome-path)
      [[ $# -ge 2 ]] || { echo "Missing value for --chrome-path." >&2; exit 2; }
      chrome_path="$2"
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

if ! [[ "$port" =~ ^[0-9]+$ ]] || ((port < 1 || port > 65535)); then
  echo "Port must be an integer from 1 through 65535." >&2
  exit 2
fi

if [[ -n "$chrome_path" && ! -x "$chrome_path" ]]; then
  echo "The browser executable supplied with --chrome-path is not executable: $chrome_path" >&2
  exit 1
fi

if [[ -z "$chrome_path" ]]; then
  for candidate in google-chrome google-chrome-stable chromium chromium-browser; do
    if command -v "$candidate" >/dev/null 2>&1; then
      chrome_path="$(command -v "$candidate")"
      break
    fi
  done
fi

if [[ -z "$chrome_path" ]]; then
  cat >&2 <<'EOF'
Google Chrome or Chromium could not be found automatically.

Install a supported browser, or tell your coding assistant where it is
installed by providing the full path to its executable. For example:
  bash .agents/scripts/start-research-chrome-linux.sh --chrome-path /usr/bin/google-chrome

If a chatbot app called this script, paste this error and that executable path
into the chat. Do not provide a browser profile, login, password, or other
private data.
EOF
  exit 1
fi

# This profile is task-only. It never opens or changes the user's normal
# Chrome profile. Keep the port synchronized with .codex/config.toml.
profile_dir="${TMPDIR:-/tmp}/codex-research-chrome-${port}"
mkdir -p "$profile_dir"

nohup "$chrome_path" \
  "--remote-debugging-port=${port}" \
  "--user-data-dir=${profile_dir}" \
  --no-first-run \
  --no-default-browser-check \
  >/dev/null 2>&1 &

echo "Started isolated research browser on CDP port ${port}."
