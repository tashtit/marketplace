# Changelog

## 0.2.0 - 2026-08-05

- Lead every skill's description with a `Usage:` signature so required
  arguments are visible at a glance in the skill list.
- Simplified the dynamic skills (`compare-models`, `evaluate-skill`,
  `benchmark-skills`): removed the optional `runs`, `base`, `layers`, `keep`,
  and `model` flags from the argument surface and hardcoded the previous
  defaults (current HEAD, single run per arm, always keep worktrees, each
  skill's existing layer set, session model). An explicit user override is
  still honored.
- Cross-referenced the static and dynamic skills so a coding-task run is not
  routed to a read-only review (`compare-skills` ↔ `benchmark-skills`,
  `review-skill` ↔ `evaluate-skill`), and added a "do not trigger on casual
  mention" guard to the two static skills.

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
