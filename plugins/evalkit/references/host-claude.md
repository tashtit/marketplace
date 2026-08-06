# Host profile: Claude Code

Loaded **only** when the current host is Claude Code (`CLAUDECODE=1`). Do not read
the Copilot profile. Every host-specific detail the dynamic skills need is defined
below under a stable heading the skill refers to by name.

## Headless invocation

One headless session per arm. Substitute `<task>`, `<model>`, and `<out>`
(the arm's JSONL capture path):

```
claude -p "<task>" \
       --model <model> \
       --permission-mode bypassPermissions \
       --output-format stream-json \
       > <out>
```

- Omit `--model` to use the session default / auto.
- `<out>` is `runs/<arm>-<run-id>.jsonl`.

## Review-layer subprocess

Run the arm-blind code review as a headless `claude -p` subprocess **inside the
arm's worktree** so it inherits `CLAUDE.md` and the project's skills:

```
claude -p "<review instructions + the diff>" \
       --permission-mode bypassPermissions \
       --output-format stream-json
```

Never pass the arm label (or, for `compare-models`, the model name) to the
reviewer or judge.

## Telemetry parsing

Parse `runs/<arm>-<run-id>.jsonl` — Claude Code stream-json:

- Final `result` event: `total_cost_usd`, `usage.input_tokens`, `usage.output_tokens`,
  `usage.cache_read_input_tokens`, `usage.cache_creation_input_tokens`, `duration_ms`, `turns`, `session_id`.
- Tool profile: count `tool_use` events grouped by `name`.
- Tool errors: count `tool_result` events where `is_error` is `true`.

## Report metric rows

Substitute these host-specific rows into the skill's report table (in place of the
generic cost/token rows):

```
tokens (in/out)   | ...k/...k               | ...k/...k
cost (USD)        | $...                    | $...
```

## Skill-invocation detection

Determine whether a given skill actually **fired** in an arm by scanning its
`runs/<arm>-<run-id>.jsonl` for a signal that names the skill under test (match on
the skill's `name` front-matter value, not its directory):

- A `tool_use` event with `name` == `Skill` whose `input.command` / `input.name`
  names the skill, **or**
- A `tool_use` `Read` of a path ending in that skill's `SKILL.md`.

Presence of either ⇒ `skill_fired = yes`; absence of both ⇒ `skill_fired = no`.

## Skill isolation

Skills reach a session from two places: **repo-local** load paths inside the worktree
(`.claude/skills/`, `.github/skills/`, `src/skills/`, …), and **plugins** installed
under the user config dir (`$HOME/.claude/`), which every worktree and session shares.

- **Repo-local** — isolate by deleting the skill's file/directory inside the arm's
  worktree. Fully isolated; no shared state is touched.
- **Plugin / global** — a worktree delete does not remove it. Isolate the arm by
  running its headless `claude` session with `HOME` pointed at a **per-arm copy** of
  the real home (so the copied `$HOME/.claude/` keeps its auth) in which the plugin
  under test is removed for the arm that must lack the skill and left in place for the
  arm that must have it. Never uninstall or edit the shared `$HOME/.claude/` in place —
  that would corrupt other sessions and the parallel arm.

Always verify isolation with **Skill-invocation detection**: the arm that must lack the
skill must show `skill_fired = no`. If it fired anyway, isolation leaked — treat the
run as invalid.

## Reviewer sub-agent

The static skills use the bundled `skill-reviewer` agent (`agents/skill-reviewer.md`);
it is host-agnostic and ships with this plugin.
