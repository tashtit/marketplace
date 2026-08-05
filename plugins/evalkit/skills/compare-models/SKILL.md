---
name: compare-models
description: "Usage: /compare-models <task…> — requires a task; the two models are picked interactively afterward. Compare two models on the same coding task by running each in an isolated git worktree and diffing gates, cost, tokens, and review findings. Expensive and side-effecting; spawns two headless agent sessions and leaves worktrees on disk. Invoke only on an explicit request to benchmark two models against a specific task. Do not trigger on general questions about which model to use."
---

# Compare Models

Compare two models on the **same coding task** by running it under two isolated arms — one per model — and comparing efficiency, behavior, and output-quality metrics.

The only difference between arms is `--model`. Prompt, base commit, skill state, and every quality layer are identical by construction, so any delta is attributable to the model.

> **Cost warning.** This spawns two headless agent sessions and creates two git worktrees that are kept after the run. Confirm the user wants this before starting if the request was at all ambiguous.

## Host resolution (do this first, once)

The headless CLI, its flags, the review-subprocess invocation, the telemetry schema, and the metric names are **host-specific**. Resolve them deterministically instead of guessing:

1. Run `scripts/resolve-host.sh`. It prints the path of the reference file for the current host and exits non-zero if the host cannot be identified.
2. If it exits non-zero, **stop** and tell the user the host could not be determined — do not run any CLI.
3. Read **only** the file it printed (never the other host's file). It defines the exact **Headless invocation**, **Review-layer subprocess**, **Telemetry parsing**, and **Report metric rows** referenced by name below.

## Arguments

| Param  | Required | Notes |
|--------|----------|-------|
| `task` | ✅       | The identical prompt passed to both arms. |

`task` is the only argument. The two models are **not** arguments — they are selected via picker after the task is known, so they can never be typos or unresolvable IDs.

The rest of the run is fixed by design so the usage stays simple: it branches from the **current HEAD**, runs **all quality layers** (gates, review, judge), does a **single run per arm**, and **keeps** both worktrees afterward. If the user explicitly asks for something different — a different base commit, only some layers, more than one run, or removing the worktrees afterward — honor that request; otherwise never prompt for these.

When invoked as `/compare-models <task…>`, parse `task` from `$ARGUMENTS` as all positional text. When triggered from a natural-language request, take the task from the user's message. **If no task is given, ask for it — never guess one.**

## Steps

1. Determine `task` as described above. If missing, ask and stop.

2. Query the session for the available models list.

3. Present a picker — **"Select model for Arm A"** — with the available models as options. Store as `modelA`.

4. Present a picker — **"Select model for Arm B"** — with the available models as options. Store as `modelB`.

   If `modelA == modelB`, re-prompt: "Models must differ — pick a different model for Arm B." Do not error out cold.

5. Resolve `base` to the current HEAD:
   ```
   base = git rev-parse HEAD
   ```

6. Generate a `run-id` from the current timestamp (e.g. `20260803-143021`).

7. Run both arms **in parallel** (isolated worktrees). Use the **Headless invocation** from the resolved host reference for each session — passing `<modelA>` / `<modelB>` as the model — and capture JSONL to `runs/<arm>-<run-id>.jsonl`:

   **Arm A** — runs with `modelA`:
   ```
   git worktree add -b mcmp/A-<run-id> mcmp/A-<run-id> <base>
   cd mcmp/A-<run-id>
   # headless session (model = <modelA>) per the resolved host reference → runs/A-<run-id>.jsonl
   ```

   **Arm B** — runs with `modelB`:
   ```
   git worktree add -b mcmp/B-<run-id> mcmp/B-<run-id> <base>
   cd mcmp/B-<run-id>
   # headless session (model = <modelB>) per the resolved host reference → runs/B-<run-id>.jsonl
   ```

8. For each arm, run the quality layers in the worktree, before any teardown:

   **`gates`** — run deterministic checks (tests / build / lint) → pass/fail per gate.

   **Commit the result:**
   ```
   git add -A && git commit -m "mcmp: <arm> arm result"
   git diff <base> > runs/<arm>-<run-id>.diff
   ```

   **`review`** — code-review the diff using the **Review-layer subprocess** from the resolved host reference, run inside the arm's worktree so it inherits the host's project-context file and skills. Do **not** pass the arm label **or the model name** to the reviewer. → findings by severity.

   **`judge`** — judge the diff against the task for **task-correctness only**. Also arm- and model-blind.

   **Telemetry** — parse `runs/<arm>-<run-id>.jsonl` per the **Telemetry parsing** section of the resolved host reference. AI-unit / USD cost is per-model-priced, which is exactly the dimension being compared here.

9. Worktrees are **always kept**. Never auto-remove — use `remove-worktrees` to clean up later.

10. Emit the report, substituting the **Report metric rows** from the resolved host reference for the `<host cost/token rows>` line:

```
metric            | A (<modelA>)       | B (<modelB>)
------------------|--------------------|-------------------
gates_passed      | ...                | ...
judge_completed   | ...                | ...
review_findings   | 0c 1h 2m           | 0c 0h 1m
<host cost/token rows>
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
4. Single-run results are **directional**. Models are non-deterministic, so a single delta may be noise. Report as such; if the user needs statistical confidence, they can request repeated runs and compare distributions.
