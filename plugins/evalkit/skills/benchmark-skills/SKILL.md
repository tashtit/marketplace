---
name: benchmark-skills
description: Compare two specific skills head-to-head by running the same coding task under each, in isolated git worktrees, then comparing cost, tokens, gates, and review findings. Expensive and side-effecting; spawns two headless agent sessions and leaves worktrees on disk. Invoke only on an explicit request naming two skills and a task. Do not trigger on casual mention of comparing or benchmarking skills — for a static read-only comparison use compare-skills instead.
---

# Benchmark Skills

Compare two skills head-to-head on the **same coding task** by running it under two isolated arms — one per skill — and comparing efficiency, behavior, and output-quality metrics.

The two skills are the **only** intentional asymmetry. Prompt, base commit, model, and every quality layer are identical by construction, so any delta is attributable to the skill.

> **Cost warning.** This spawns two headless `claude -p` sessions and creates two git worktrees that are kept after the run. Confirm the user wants this before starting if the request was at all ambiguous. For a cheap static comparison of authoring quality, use `compare-skills` instead.

## Arguments

| Param    | Required | Default        | Notes |
|----------|----------|----------------|-------|
| `skillA` | ✅       | —              | First skill. Arm A. |
| `skillB` | ✅       | —              | Second skill. Arm B. |
| `task`   | ✅       | —              | The identical prompt passed to both arms. |
| `runs`   | ⬜       | `1`            | N per arm. >1 adds a seed loop and distribution reporting; cost scales linearly. |
| `model`  | ⬜       | current / auto | Applied identically to both arms — a single value, never per-arm. |
| `base`   | ⬜       | `HEAD`         | Commit both worktrees branch from. |
| `layers` | ⬜       | `gates,review` | Which quality layers run: `gates` / `review` / `judge`. |
| `keep`   | ⬜       | `true`         | Keep worktrees after the run. |

When invoked as `/benchmark-skills <skillA> <skillB> <task…>`, parse from `$ARGUMENTS`: `skillA` and `skillB` are positional args 1 and 2, `task` is the remaining positional text, and named params use `--` prefixes. When triggered from a natural-language request, extract the same values from the user's message.

**If any of `skillA`, `skillB`, or `task` is missing, ask for it — never guess a task.** Running the wrong task wastes two headless sessions.

## Steps

1. Determine `skillA`, `skillB`, and `task` as described above. If any is missing, ask and stop.

2. Resolve both skill paths against known load paths (`.claude/skills/`, `.github/skills/`, `src/skills/`, plugin skill paths). If either is unresolvable, report the error and stop.

3. Resolve `base`:
   ```
   base = <--base value, or: git rev-parse HEAD>
   ```

4. Generate a `run-id` from the current timestamp (e.g. `20260803-143021`).

5. Run both arms **in parallel** (isolated worktrees). Both skills are repo-local and present at the base commit, so each arm deletes the other skill — a symmetric single-file operation:

   **Arm A** — only `skillA` present:
   ```
   git worktree add -b bench/A-<run-id> bench/A-<run-id> <base>
   # delete <resolved skillB path> inside the worktree
   cd bench/A-<run-id>
   claude -p "<task>" \
          --model <model> \
          --permission-mode bypassPermissions \
          --output-format stream-json \
          > runs/A-<run-id>.jsonl
   ```

   **Arm B** — only `skillB` present:
   ```
   git worktree add -b bench/B-<run-id> bench/B-<run-id> <base>
   # delete <resolved skillA path> inside the worktree
   cd bench/B-<run-id>
   claude -p "<task>" \
          --model <model> \
          --permission-mode bypassPermissions \
          --output-format stream-json \
          > runs/B-<run-id>.jsonl
   ```

6. For each arm, run the quality layers in the worktree, before any teardown:

   **`gates`** (if in `layers`) — run deterministic checks (tests / build / lint) → pass/fail per gate.

   **Commit the result:**
   ```
   git add -A && git commit -m "bench: <arm> arm result"
   git diff <base> > runs/<arm>-<run-id>.diff
   ```

   **`review`** (if in `layers`) — code-review the diff. Run inside the arm's worktree so it inherits CLAUDE.md and project skills. Do **not** pass the arm label to the reviewer (arm-blind). Both skills are assumed to be non-review skills, so the same review skill auto-triggers identically in both arms. → findings by severity.

   **`judge`** (if in `layers`) — judge the diff against the task for **task-correctness only**.

   **Telemetry** — parse `runs/<arm>-<run-id>.jsonl`:
   - Final `result` event: `total_cost_usd`, `usage.input_tokens`, `usage.output_tokens`, `usage.cache_read_input_tokens`, `usage.cache_creation_input_tokens`, `duration_ms`, `turns`, `session_id`
   - Tool profile: count `tool_use` events grouped by `name`
   - Tool errors: count `tool_result` events where `is_error` is `true`

7. Worktrees are **kept** unless `keep` is false. Never auto-remove — use `remove-worktrees` to clean up later.

8. Emit the report:

```
metric            | A (<skillA>)       | B (<skillB>)
------------------|--------------------|-------------------
gates_passed      | ...                | ...
review_findings   | 0c 1h 2m           | 0c 0h 1m
tokens (in/out)   | ...k/...k          | ...k/...k
cost (USD)        | $...               | $...
duration          | ...                | ...
turns             | ...                | ...
tool_calls        | ...                | ...
files_changed     | ...                | ...
worktree          | bench/A-<run-id>   | bench/B-<run-id>

### Recommendation
<which skill to use, and the tradeoff — e.g. "B produces cleaner code and is
faster/cheaper; prefer B unless skillA has other advantages for this codebase.">
```

## Validity guardrails

1. Identical **prompt**, **base commit**, and **model** across arms.
2. Each arm has exactly one of the two skills present. No other skill state differs between arms.
3. **Arm-blind reviewer** — the review subprocess receives the diff and project context, never the arm label.
4. N=1 results are **directional**, not statistical. Report them as such. Raise `runs` and compare distributions for confidence.
