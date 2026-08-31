#!/usr/bin/env bash
# Resolve the concept library's read path and its writable path — they differ.
#
# The bundled library ships inside the installed plugin, which is a managed
# directory with no version history: a reinstall or upgrade replaces it, so an
# extraction run that wrote there would silently lose its work. Reading the
# bundled copy is correct; writing to it is not.
#
# Usage:
#   library-path.sh read    absolute path of the bundled library (always exists)
#   library-path.sh write   absolute path safe to write, or exit 3 with a reason
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
bundled="$here/references/system-design-concerns"

mode="${1:-read}"

case "$mode" in
read)
  if [ ! -d "$bundled" ]; then
    echo "ERROR: bundled library missing at $bundled; the plugin install is incomplete." >&2
    exit 1
  fi
  echo "$bundled"
  ;;
write)
  # A checkout of the plugin's own source repository is the only versioned home
  # for new claims. Prefer it whenever the working directory sits inside one.
  if root="$(git rev-parse --show-toplevel 2>/dev/null)" &&
    [ -d "$root/plugins/interview-kit/references/system-design-concerns" ]; then
    echo "$root/plugins/interview-kit/references/system-design-concerns"
    exit 0
  fi
  # A repository-local library is the other legitimate target: it is tracked by
  # whatever repository the user is working in.
  if [ -n "${root:-}" ] && [ -d "$root/references/system-design-concerns" ]; then
    echo "$root/references/system-design-concerns"
    exit 0
  fi
  echo "ERROR: no writable library found. The bundled copy at" >&2
  echo "  $bundled" >&2
  echo "is read-only: it lives in a managed install directory with no version" >&2
  echo "history, so a reinstall would discard anything written there. Ask the" >&2
  echo "user where the library should live — a checkout of the plugin's source" >&2
  echo "repository, or 'references/system-design-concerns/' in the current one." >&2
  exit 3
  ;;
*)
  echo "ERROR: unknown mode '$mode'; expected 'read' or 'write'." >&2
  exit 2
  ;;
esac
