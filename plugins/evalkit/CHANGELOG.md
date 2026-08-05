# Changelog

## 0.1.0 - 2026-08-04

- Added the `evalkit` router skill dispatching to six behaviors.
- Added static skills: `review-skill` and `compare-skills`, backed by a bundled,
  host-agnostic `skill-reviewer` agent (`agents/skill-reviewer.md`) — no external
  `plugin-dev` dependency.
- Added dynamic worktree harnesses: `evaluate-skill`, `benchmark-skills`, and
  `compare-models`. They are **host-adaptive**: `scripts/resolve-host.sh` detects
  the current host and each harness reads only the resolved reference
  (`references/host-claude.md` or `references/host-copilot.md`) for the headless
  invocation, review subprocess, telemetry parsing, and report metric names.
- Added the `remove-worktrees` cleanup skill with a dirty-work confirmation gate.
- Targets `claude-code` and `github-copilot` (not Codex).
- Added positive, failure, and unsafe acceptance scenarios.
