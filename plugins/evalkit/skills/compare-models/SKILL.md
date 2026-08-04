---
name: compare-models
description: Compare two models on the same coding task by running each in an isolated git worktree and diffing cost, tokens, gates, and review findings. Models are chosen from the session's available list via picker. Expensive and side-effecting; spawns two headless agent sessions and leaves worktrees on disk. Invoke only on an explicit request to benchmark two models against a specific task. Do not trigger on general questions about which model to use.
---

# Compare Models

Compare two models on the **same coding task** by running it under two isolated arms — one per model — and comparing efficiency, behavior, and output-quality metrics.

The only difference between arms is `--model`. Prompt, base commit, skill state, and every quality layer are identical by construction, so any delta is attributable to the model.

> **Cost warning.** This spawns two headless `claude -p` sessions and creates two git worktrees that are kept after the run. Confirm the user wants this before starting if the request was at all ambiguous.

## Arguments

| Param          | Required | Default              | Notes |
|----------------|----------|----------------------|-------|
| `task`         | ✅       | —                    | The identical prompt passed to both arms. |
| `runs`         | ⬜       | `1`                  | N per arm. >1 adds a seed loop and distribution reporting; cost scales linearly. |
| `base`         | ⬜       | `HEAD`               | Commit both worktrees branch from. |
| `layers`       | ⬜       | `gates,review,judge` | Which quality layers run: `gates` / `review` / `judge`. |
| `keep`         | ⬜       | `true`               | Keep worktrees after the run. |
| `review-skill` | ⬜       | —                    | Explicit skill for the review layer. If omitted, the subprocess loads whatever review skills are available in the arm's worktree. |

The two models are **not** arguments — they are selected via picker after the task is known, so they can never be typos or unresolvable IDs.

When invoked as `/compare-models <task…>`, parse `task` from `$ARGUMENTS` as all positional text; named params use `--` prefixes. When triggered from a natural-language request, take the task from the user's message. **If no task is given, ask for it — never guess one.**

## Steps

1. Determine `task` as described above. If missing, ask and stop.

2. Query the session for the available models list.

3. Present a picker — **"Select model for Arm A"** — with the available models as options. Store as `modelA`.

4. Present a picker — **"Select model for Arm B"** — with the available models as options. Store as `modelB`.

   If `modelA == modelB`, re-prompt: "Models must differ — pick a different model for Arm B." Do not error out cold.

5. Resolve `base`:
   ```
   base = <--base value, or: git rev-parse HEAD>
   ```

6. Generate a `run-id` from the current timestamp (e.g. `20260803-143021`).

7. Run both arms **in parallel** (isolated worktrees):

   **Arm A** — runs with `modelA`:
   ```
   git worktree add -b mcmp/A-<run-id> mcmp/A-<run-id> <base>
   cd mcmp/A-<run-id>
   claude -p "<task>" \
          --model <modelA> \
          --permission-mode bypassPermissions \
          --output-format stream-json \
          > runs/A-<run-id>.jsonl
   ```

   **Arm B** — runs with `modelB`:
   ```
   git worktree add -b mcmp/B-<run-id> mcmp/B-<run-id> <base>
   cd mcmp/B-<run-id>
   claude -p "<task>" \
          --model <modelB> \
          --permission-mode bypassPermissions \
          --output-format stream-json \
          > runs/B-<run-id>.jsonl
   ```

8. For each arm, run the quality layers in the worktree, before any teardown:

   **`gates`** (if in `layers`) — run deterministic checks (tests / build / lint) → pass/fail per gate.

   **Commit the result:**
   ```
   git add -A && git commit -m "mcmp: <arm> arm result"
   git diff <base> > runs/<arm>-<run-id>.diff
   ```

   **`review`** (if in `layers`) — code-review the diff inside the arm's worktree so it inherits CLAUDE.md and project skills. Do **not** pass the arm label **or the model name** to the reviewer. → findings by severity.

   **`judge`** (if in `layers`) — judge the diff against the task for **task-correctness only**. Also arm- and model-blind.

   **Telemetry** — parse `runs/<arm>-<run-id>.jsonl`:
   - Final `result` event: `total_cost_usd`, `usage.input_tokens`, `usage.output_tokens`, `usage.cache_read_input_tokens`, `usage.cache_creation_input_tokens`, `duration_ms`, `turns`, `session_id`
   - Tool profile: count `tool_use` events grouped by `name`
   - Tool errors: count `tool_result` events where `is_error` is `true`

9. Worktrees are **kept** unless `keep` is false. Never auto-remove — use `remove-worktrees` to clean up later.

10. Emit the report:

```
metric            | A (<modelA>)       | B (<modelB>)
------------------|--------------------|-------------------
gates_passed      | ...                | ...
judge_completed   | ...                | ...
review_findings   | 0c 1h 2m           | 0c 0h 1m
tokens (in/out)   | ...k/...k          | ...k/...k
cost (USD)        | $...               | $...
duration          | ...                | ...
turns             | ...                | ...
tool_calls        | ...                | ...
files_changed     | ...                | ...
worktree          | mcmp/A-<run-id>    | mcmp/B-<run-id>

### Recommendation
<which model to use for this task and the tradeoff — e.g. "B produces slightly
cleaner code (1 fewer review finding) but costs 2.1× and takes 1.5× as long;
A is the better default unless the review delta matters for this codebase.">
```

## Validity guardrails

1. Identical **prompt**, **base commit**, **skill state**, and **review config** across arms. The model is the sole intentional variable.
2. **Distinct models required** — identical selections are re-prompted, not accepted.
3. **Arm- and model-blind reviewer and judge.** Model reputation is a strong prior; revealing it would bias findings toward the expected winner. The subprocesses receive the diff and project context only.
4. N=1 results are **directional**. Models are non-deterministic, so a single delta may be noise. Report as such; raise `runs` and compare distributions for confidence.
