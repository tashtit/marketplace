# Changelog

## 0.3.0 - 2026-08-06

- Added a **fired-check** to `evaluate-skill` and `benchmark-skills`: the task is
  still run exactly as written (no forced invocation), but each arm's telemetry is
  now scanned to confirm the skill under test was actually invoked. A skill that
  never triggered is reported **inconclusive** instead of "no effect," and a
  control arm where an excluded skill leaked in is reported **invalid**. Added a
  `skill_fired` row to both report tables and a `Skill-invocation detection`
  section to `host-copilot.md` and `host-claude.md`.
- Handled **plugin / globally installed** skills, which a worktree file-delete
  cannot isolate: both dynamic skills now classify the skill source and, for
  plugin/global skills, isolate the arm via the host reference's new `Skill
  isolation` procedure (a per-arm `HOME` copy with the plugin removed) or stop
  rather than run an invalid control. The fired-check verifies the isolation held.

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
