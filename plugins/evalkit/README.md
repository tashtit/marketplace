# Evalkit

Evalkit measures skill and model quality two ways: static authoring review that
reads a skill's files without running anything, and dynamic harnesses that run
the same coding task under isolated git worktrees while varying exactly one
factor, so any difference in the result is attributable to that factor.

## Maturity

**Experimental — 0.1.0.** Behavioral compatibility still requires review on the
target agent.

## Skills

`skills/evalkit/SKILL.md` is a router that dispatches to six behaviors:

| Skill | Kind | Cost | What it does |
| --- | --- | --- | --- |
| `review-skill` | Static | Cheap | Reviews one skill's authoring quality by reading its files. |
| `compare-skills` | Static | Cheap | Reviews two skills and synthesizes a difference summary. |
| `evaluate-skill` | Dynamic | Expensive | Runs a task with a skill present and with it deleted, then diffs the outcomes. |
| `benchmark-skills` | Dynamic | Expensive | Runs a task under each of two skills, one per arm, then diffs the outcomes. |
| `compare-models` | Dynamic | Expensive | Runs a task under each of two models, one per arm, with an arm- and model-blind reviewer. |
| `remove-worktrees` | Utility | Cheap | Lists and removes worktrees and branches left by the dynamic harnesses. |

Static skills read files only. Dynamic skills spawn two headless sessions and
create two git worktrees.

## Defaults

- Worktrees are **kept** after every dynamic run; nothing is removed implicitly.
- Dynamic harnesses confirm before spawning headless sessions when the request is
  at all ambiguous, and never guess a task — a missing task or skill is asked for,
  not inferred.
- `remove-worktrees` defaults to **list only**; it removes nothing without an
  explicit target, prefix, or `all`, and confirms individually before removing any
  worktree that holds uncommitted or unpushed work.
- Reviewers and judges are **arm-blind** (and **model-blind** for `compare-models`)
  so the label cannot bias the finding.

## Prerequisites

- The `plugin-dev:skill-reviewer` agent (from the `plugin-dev` plugin) backs
  `review-skill` and `compare-skills`. Install it with `/plugin`, then
  `/reload-plugins`. The two skills report the missing agent and stop rather than
  degrading silently.
- The dynamic harnesses require git worktree support and the `claude` CLI on
  `PATH`.

## Portability

Evalkit is a **Claude Code** plugin. The dynamic harnesses invoke the Claude Code
CLI (`claude -p ... --output-format stream-json`) and parse its stream-json
telemetry, so their behavior is reviewed on `claude-code` only; other platforms
are out of scope for this version. The static skills are read-only and portable in
principle, but are likewise reviewed only on `claude-code` here.

## Threat model

| Threat | Control |
| --- | --- |
| Loss of uncommitted or unpushed work during cleanup | `remove-worktrees` defaults to listing, excludes the main worktree, and confirms individually before removing any dirty worktree |
| Runaway cost from headless sessions on the wrong task | Dynamic harnesses confirm ambiguous requests and never guess a missing task or skill |
| Biased review or judgement | Reviewer and judge receive the diff and project context only, never the arm label or model name |
| Ambiguous destructive request treated as authorization | "Clean up my worktrees" defaults toward listing and never force-removes dirty work without explicit confirmation |
| Invalid control arm | `evaluate-skill` checks that the skill is absent from all load paths in the `without` arm and warns if a globally installed copy would defeat the control |

See [CHANGELOG.md](CHANGELOG.md). Maintainer-only evaluation material lives outside
the distributed plugin in the
[repository test suite](../../tests/plugins/evalkit/).
