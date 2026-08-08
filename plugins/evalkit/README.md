# Evalkit

Evalkit measures skill and model quality two ways: static authoring review that
reads a skill's files without running anything, and dynamic harnesses that run
the same coding task under isolated git worktrees while varying exactly one
factor, so any difference in the result is attributable to that factor.

## Installation

```bash
# Claude Code
claude plugin marketplace add tashtit/marketplace
claude plugin install evalkit@tashtit

# GitHub Copilot CLI
copilot plugin marketplace add tashtit/marketplace
copilot plugin install evalkit@tashtit
```

Evalkit is not published to the Codex catalog; it supports Claude Code and
GitHub Copilot CLI only.

## Maturity

**Experimental — 0.3.0.** Behavioral compatibility still requires review on the
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

- The bundled `skill-reviewer` agent (`agents/skill-reviewer.md`) backs
  `review-skill` and `compare-skills`. It ships with this plugin and is
  host-agnostic — no external `plugin-dev` dependency. Install evalkit with
  `/plugin`, then `/reload-plugins`. The two skills report the missing agent and
  stop rather than degrading silently.
- The dynamic harnesses require git worktree support and the host's CLI on `PATH`
  (`claude` on Claude Code, `copilot` on GitHub Copilot CLI).

## Portability

Evalkit is **host-adaptive** across Claude Code and GitHub Copilot CLI. The dynamic
harnesses run `scripts/resolve-host.sh` first, which deterministically detects the
current host (`CLAUDECODE` vs `COPILOT_CLI`) and prints the matching reference under
`references/` — `host-claude.md` or `host-copilot.md`. Each skill reads **only** that
file, which defines the exact headless invocation, review-subprocess, telemetry
parsing, and report metric names for the host (e.g. `claude -p … stream-json` with
USD/token metrics, or `copilot -p … --output-format json` JSONL with AI-unit/premium
metrics). The resolver **fails closed**: on an unknown host it stops rather than
guessing a CLI. The static skills and the bundled reviewer agent are host-agnostic.
This plugin does not target Codex.

## Threat model

| Threat | Control |
| --- | --- |
| Loss of uncommitted or unpushed work during cleanup | `remove-worktrees` defaults to listing, excludes the main worktree, and confirms individually before removing any dirty worktree |
| Runaway cost from headless sessions on the wrong task | Dynamic harnesses confirm ambiguous requests and never guess a missing task or skill |
| Biased review or judgement | Reviewer and judge receive the diff and project context only, never the arm label or model name |
| Ambiguous destructive request treated as authorization | "Clean up my worktrees" defaults toward listing and never force-removes dirty work without explicit confirmation |
| Invalid control arm | `evaluate-skill` checks that the skill is absent from all load paths in the `without` arm, isolates plugin/global skills via the host's **Skill isolation** procedure (or stops), and a per-arm **fired-check** confirms the skill actually fired where present and not where absent — a run that never triggered the skill is reported inconclusive, not "no effect" |

See [CHANGELOG.md](CHANGELOG.md). Maintainer-only evaluation material lives outside
the distributed plugin in the
[repository test suite](../../tests/plugins/evalkit/).
