#!/usr/bin/env bash
# Deterministically resolve the current agent host to its reference file.
# Fail closed: if the host cannot be identified, stop rather than guess a CLI.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ "${COPILOT_CLI:-}" = "1" ]; then
  echo "$here/references/host-copilot.md"
elif [ "${CLAUDECODE:-}" = "1" ] || [ -n "${CLAUDE_CODE_ENTRYPOINT:-}" ]; then
  echo "$here/references/host-claude.md"
else
  echo "ERROR: unknown host (neither COPILOT_CLI nor CLAUDECODE set); stop and ask the user." >&2
  exit 1
fi
