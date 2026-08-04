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

## Reviewer sub-agent

The static skills use the bundled `skill-reviewer` agent (`agents/skill-reviewer.md`);
it is host-agnostic and ships with this plugin.
