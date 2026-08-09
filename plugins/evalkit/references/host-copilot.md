# Host profile: GitHub Copilot CLI

Loaded **only** when the current host is Copilot CLI (`COPILOT_CLI=1`). Do not read
the Claude profile. Every host-specific detail the dynamic skills need is defined
below under a stable heading the skill refers to by name.

## Headless invocation

One headless session per arm. Substitute `<task>`, `<model>`, and `<out>`
(the arm's JSONL capture path):

```bash
copilot -p "<task>" \
        --model <model> \
        --allow-all-tools \
        --no-ask-user \
        --output-format json \
        --log-level none \
        > <out>
```

- Omit `--model` to use the session default / auto.
- `<out>` is `runs/<arm>-<run-id>.jsonl`.

## Review-layer subprocess

Run the arm-blind code review as a headless `copilot -p` subprocess **inside the
arm's worktree** so it inherits `AGENTS.md` / `.github/copilot-instructions.md`
and the project's skills:

```bash
copilot -p "<review instructions + the diff>" \
        --agent code-review \
        --allow-all-tools \
        --no-ask-user \
        --output-format json \
        --log-level none
```

Never pass the arm label (or, for `tashtit-compare-models`, the model name) to the
reviewer or judge.

## Telemetry parsing

Parse `runs/<arm>-<run-id>.jsonl` — Copilot CLI JSONL, one JSON object per line,
discriminated by `type`:

- `result` event: `sessionId`, `usage.sessionDurationMs`, `usage.totalApiDurationMs`,
  `usage.premiumRequests`, `usage.codeChanges.filesModified` (array) / `linesAdded` / `linesRemoved`.
- Output tokens: sum `data.outputTokens` across `assistant.message` events (input tokens are NOT emitted).
- AI-unit cost: the last `session.usage_checkpoint` event's `data.totalNanoAiu` (÷ 1e9 = AIU) and `data.totalPremiumRequests`.
- Turns: count `assistant.turn_start` events.
- Tool profile: count `tool.execution_start` events grouped by `data.toolName`.
- Tool errors: count `tool.execution_complete` events where `data.success` is `false`.

> Copilot CLI does not emit input-token counts or a USD cost in JSONL. Report cost
> in premium requests / AI units (nano AIU), and report output tokens only.

## Report metric rows

Substitute these host-specific rows into the skill's report table (in place of the
generic cost/token rows):

```text
output_tokens     | ...k                    | ...k
premium_reqs      | ...                     | ...
ai_units (AIU)    | ...                     | ...
```

`ai_units (AIU)` is per-model-priced — the relevant cost dimension for `tashtit-compare-models`.

## Skill-invocation detection

Determine whether a given skill actually **fired** in an arm by scanning its
`runs/<arm>-<run-id>.jsonl` for a signal that names the skill under test (match on
the skill's `name` front-matter value, not its directory):

- A `tool.execution_start` event for the skill-invocation tool (`data.toolName` is
  the `skill` tool) whose `data.arguments` / `data.input` names the skill, **or**
- A `tool.execution_start` for a file read whose path ends in that skill's
  `SKILL.md`, **or**
- Any event whose payload otherwise references the skill's `name`.

Presence of any of these ⇒ `skill_fired = yes`; absence of all ⇒ `skill_fired = no`.

## Skill isolation

Skills reach a session from two places: **repo-local** load paths inside the worktree
(`.github/skills/`, `.claude/skills/`, `src/skills/`, …), and **plugins** installed
under the user config dir (`$HOME/.copilot/`), which every worktree and session shares.

- **Repo-local** — isolate by deleting the skill's file/directory inside the arm's
  worktree. Fully isolated; no shared state is touched.
- **Plugin / global** — a worktree delete does not remove it. Isolate the arm by
  running its headless `copilot` session with `HOME` pointed at a **per-arm copy** of
  the real home (so the copied `$HOME/.copilot/` keeps its auth/token) in which the
  plugin under test is removed for the arm that must lack the skill and left in place
  for the arm that must have it. Never uninstall or edit the shared `$HOME/.copilot/`
  in place — that would corrupt other sessions and the parallel arm.

Always verify isolation with **Skill-invocation detection**: the arm that must lack the
skill must show `skill_fired = no`. If it fired anyway, isolation leaked — treat the
run as invalid.

## Reviewer sub-agent

The static skills use the bundled `skill-reviewer` agent (`agents/skill-reviewer.md`);
it is host-agnostic and ships with this plugin.
