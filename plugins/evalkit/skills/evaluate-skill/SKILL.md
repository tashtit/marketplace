---
name: evaluate-skill
description: Measure whether a specific skill changes coding-task outcomes by running the same task twice — once with the skill present, once with it deleted — in isolated git worktrees, then comparing cost, tokens, gates, and review findings. Expensive and side-effecting; spawns two headless agent sessions and leaves worktrees on disk. Invoke only on an explicit request naming both a skill and a task. Do not trigger on casual mention of evaluating, testing, or measuring a skill.
---

# Evaluate Skill

Measure a single skill's effect on a coding task by running the **same task** under two isolated arms — one with the skill, one without — and comparing efficiency, behavior, and output-quality metrics.

The only difference between arms is whether the skill is present. Prompt, base commit, and model are identical by construction, so any delta is attributable to the skill.

> **Cost warning.** This spawns two headless `claude -p` sessions and creates two git worktrees that are kept after the run. Confirm the user wants this before starting if the request was at all ambiguous.

## Arguments

| Param    | Required | Default        | Notes |
|----------|----------|----------------|-------|
| `skill`  | ✅       | —              | Repo-local skill under test. |
| `task`   | ✅       | —              | The identical prompt passed to both arms. |
| `runs`   | ⬜       | `1`            | N per arm. >1 adds a seed loop and distribution reporting; cost scales linearly. |
| `model`  | ⬜       | current / auto | Applied identically to both arms — never per-arm. |
| `base`   | ⬜       | `HEAD`         | Commit both worktrees branch from. |
| `layers` | ⬜       | `gates,review` | Which quality layers run: `gates` / `review` / `judge`. |
| `keep`   | ⬜       | `true`         | Keep worktrees after the run. |

When invoked as `/evaluate-skill <skill> <task…>`, parse from `$ARGUMENTS`: `skill` is positional arg 1, `task` is the remaining positional text, and named params use `--` prefixes. When triggered from a natural-language request, extract the same values from the user's message.

**If either `skill` or `task` is missing, ask for it — never guess a task.** Running the wrong task wastes two headless sessions.

## Steps

1. Determine `skill` and `task` as described above. If either is missing, ask and stop.

2. Resolve the skill path against known load paths (`.claude/skills/`, `.github/skills/`, `src/skills/`, plugin skill paths). If unresolvable, report the error and stop.

3. Resolve `base`:
   ```
   base = <--base value, or: git rev-parse HEAD>
   ```

4. Generate a `run-id` from the current timestamp (e.g. `20260803-143021`).

5. Run both arms **in parallel** (isolated worktrees). Both worktrees start from the same base with the skill present; the `without` arm deletes it before the session begins:

   **Arm `with`** — skill present (repo as-is):
   ```
   git worktree add -b eval/<skill>-with-<run-id> eval/with-<run-id> <base>
   cd eval/with-<run-id>
   claude -p "<task>" \
          --model <model> \
          --permission-mode bypassPermissions \
          --output-format stream-json \
          > runs/with-<run-id>.jsonl
   ```

   **Arm `without`** — skill deleted before work begins:
   ```
   git worktree add -b eval/<skill>-without-<run-id> eval/without-<run-id> <base>
   # delete <resolved skill path> inside the worktree
   cd eval/without-<run-id>
   claude -p "<task>" \
          --model <model> \
          --permission-mode bypassPermissions \
          --output-format stream-json \
          > runs/without-<run-id>.jsonl
   ```

6. For each arm, run the quality layers in the worktree, before any teardown:

   **`gates`** (if in `layers`) — run deterministic checks (tests / build / lint) → pass/fail per gate.

   **Commit the result:**
   ```
   git add -A && git commit -m "eval: <arm> arm result"
   git diff <base> > runs/<arm>-<run-id>.diff
   ```

   **`review`** (if in `layers`) — code-review the diff. Run inside the arm's worktree so it inherits CLAUDE.md and project skills. Do **not** pass the arm label to the reviewer (arm-blind). → findings by severity (critical / high / medium).

   **`judge`** (if in `layers`) — judge the diff against the task for **task-correctness only**: did it complete the task as specified? Narrowed so it does not overlap the review layer.

   **Telemetry** — parse `runs/<arm>-<run-id>.jsonl`:
   - Final `result` event: `total_cost_usd`, `usage.input_tokens`, `usage.output_tokens`, `usage.cache_read_input_tokens`, `usage.cache_creation_input_tokens`, `duration_ms`, `turns`, `session_id`
   - Tool profile: count `tool_use` events grouped by `name`
   - Tool errors: count `tool_result` events where `is_error` is `true`

7. Worktrees are **kept** unless `keep` is false. Never auto-remove — use `remove-worktrees` to clean up later.

8. Emit the report:

```
metric            | with                    | without
------------------|-------------------------|------------------------
gates_passed      | ...                     | ...
review_findings   | 0c 1h 2m                | 0c 3h 5m
tokens (in/out)   | ...k/...k               | ...k/...k
cost (USD)        | $...                    | $...
duration          | ...                     | ...
turns             | ...                     | ...
tool_calls        | ...                     | ...
files_changed     | ...                     | ...
worktree          | eval/with-<run-id>      | eval/without-<run-id>
```

Both worktrees remain on disk; the user picks a winner and continues there or merges its branch.

## Validity guardrails

1. Identical **prompt**, **base commit**, and **model** across arms.
2. The skill must be absent from **all** load paths in the `without` arm. Under the repo-local assumption this is a single file delete; a globally installed copy would silently invalidate the control — check for one and warn if found.
3. **Arm-blind reviewer** — the review subprocess receives the diff and project context, never the arm label.
4. N=1 results are **directional**, not statistical. Report them as such. Raise `runs` and compare distributions for confidence.
5. The skill under test is assumed to be a non-review skill, so the same review skill auto-triggers identically in both arms.
