# Host profile: GitHub Copilot CLI

Loaded **only** when the current host is Copilot CLI (`COPILOT_CLI=1`). Do not read
the Claude profile. Every host-specific detail the dynamic skills need is defined
below under a stable heading the skill refers to by name.

## Headless invocation

One headless session per arm. Substitute `<task>`, `<model>`, and `<out>`
(the arm's JSONL capture path):

```
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

```
copilot -p "<review instructions + the diff>" \
        --agent code-review \
        --allow-all-tools \
        --no-ask-user \
        --output-format json \
        --log-level none
```

Never pass the arm label (or, for `compare-models`, the model name) to the
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

```
output_tokens     | ...k                    | ...k
premium_reqs      | ...                     | ...
ai_units (AIU)    | ...                     | ...
```

`ai_units (AIU)` is per-model-priced — the relevant cost dimension for `compare-models`.

## Reviewer sub-agent

The static skills use the bundled `skill-reviewer` agent (`agents/skill-reviewer.md`);
it is host-agnostic and ships with this plugin.
