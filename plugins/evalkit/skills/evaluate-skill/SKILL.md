---
name: evaluate-skill
description: "Usage: /evaluate-skill <skill> <task…> — requires a skill and a task. Measure whether a specific skill changes coding-task outcomes by running the same task twice — once with the skill present, once with it deleted — in isolated git worktrees, then comparing gates, cost, tokens, and review findings. Expensive and side-effecting; spawns two headless agent sessions and leaves worktrees on disk. Invoke only on an explicit request naming both a skill and a task. Do not trigger on casual mention of evaluating, testing, or measuring a skill."
---

# Evaluate Skill

Measure a single skill's effect on a coding task by running the **same task** under two isolated arms — one with the skill, one without — and comparing efficiency, behavior, and output-quality metrics.

The only difference between arms is whether the skill is present. Prompt, base commit, and model are identical by construction, so any delta is attributable to the skill.

> **Cost warning.** This spawns two headless agent sessions and creates two git worktrees that are kept after the run. Confirm the user wants this before starting if the request was at all ambiguous.

## Host resolution (do this first, once)

The headless CLI, its flags, the review-subprocess invocation, the telemetry schema, and the metric names are **host-specific**. Resolve them deterministically instead of guessing:

1. Run `scripts/resolve-host.sh`. It prints the path of the reference file for the current host and exits non-zero if the host cannot be identified.
2. If it exits non-zero, **stop** and tell the user the host could not be determined — do not run any CLI.
3. Read **only** the file it printed (never the other host's file). It defines the exact **Headless invocation**, **Review-layer subprocess**, **Telemetry parsing**, and **Report metric rows** referenced by name below.

## Arguments

| Param | Required | Notes |
| --- | --- | --- |
| `skill` | ✅ | Repo-local skill under test. |
| `task` | ✅ | The identical prompt passed to both arms. |

`skill` and `task` are the only arguments. The rest of the run is fixed by design so the usage stays simple: both arms use the **session's current model**, branch from the **current HEAD**, run the **gates and review** quality layers, do a **single run per arm**, and **keep** both worktrees afterward. If the user explicitly asks for something different — a different base commit, the judge layer, more than one run, or removing the worktrees afterward — honor that request; otherwise never prompt for these.

When invoked as `/evaluate-skill <skill> <task…>`, parse from `$ARGUMENTS`: `skill` is positional arg 1 and `task` is the remaining positional text. When triggered from a natural-language request, extract the same values from the user's message.

**If either `skill` or `task` is missing, ask for it — never guess a task.** Running the wrong task wastes two headless sessions.

## Steps

1. Determine `skill` and `task` as described above. If either is missing, ask and stop.

2. Resolve the skill against known load paths (`.claude/skills/`, `.github/skills/`, `src/skills/`, plugin skill paths). If unresolvable, report the error and stop. Then **classify the source** — see the **Skill isolation** section of the resolved host reference:
   - **Repo-local** — the skill lives inside the repo tree, so it is present in every worktree branched from `base` and the control is a single-file delete.
   - **Plugin / global** — the skill is installed outside the repo (a plugin or a globally installed copy shared by every worktree and session). A worktree delete does **not** remove it, so isolate it per the host reference's **Skill isolation** procedure. If the host cannot isolate it, **stop** and tell the user this skill cannot be evaluated by the delete-based control — never produce a run whose control arm can still reach the skill.

3. Resolve `base` to the current HEAD:

   ```bash
   base = git rev-parse HEAD
   ```

4. Generate a `run-id` from the current timestamp (e.g. `20260803-143021`).

5. Run both arms **in parallel** (isolated worktrees). Both worktrees start from the same base with the skill present; the `without` arm deletes it before the session begins. Use the **Headless invocation** from the resolved host reference for each session, capturing JSONL to `runs/<arm>-<run-id>.jsonl`:

   **Arm `with`** — skill present (repo as-is):

   ```bash
   git worktree add -b eval/<skill>-with-<run-id> eval/with-<run-id> <base>
   cd eval/with-<run-id>
   # headless session per the resolved host reference → runs/with-<run-id>.jsonl
   ```

   **Arm `without`** — skill removed before work begins:

   ```bash
   git worktree add -b eval/<skill>-without-<run-id> eval/without-<run-id> <base>
   # make the skill unavailable in this arm:
   #   repo-local    → delete <resolved skill path> inside the worktree
   #   plugin/global → apply the host reference's Skill isolation procedure for this arm
   cd eval/without-<run-id>
   # headless session per the resolved host reference → runs/without-<run-id>.jsonl
   ```

6. For each arm, run the quality layers in the worktree, before any teardown:

   **`gates`** — run deterministic checks (tests / build / lint) → pass/fail per gate.

   **Commit the result:**

   ```bash
   git add -A && git commit -m "eval: <arm> arm result"
   git diff <base> > runs/<arm>-<run-id>.diff
   ```

   **`review`** — code-review the diff using the **Review-layer subprocess** from the resolved host reference, run inside the arm's worktree so it inherits the host's project-context file and skills. Do **not** pass the arm label to the reviewer (arm-blind). → findings by severity (critical / high / medium).

   **`judge`** (only if the user explicitly requested it) — judge the diff against the task for **task-correctness only**: did it complete the task as specified? Narrowed so it does not overlap the review layer.

   **Telemetry** — parse `runs/<arm>-<run-id>.jsonl` per the **Telemetry parsing** section of the resolved host reference.

   **Fired-check** — from the same JSONL, determine whether the skill under test was actually **invoked** in this arm, using the **Skill-invocation detection** section of the resolved host reference. The task is run exactly as written and the skill is **never force-invoked**, so this check is what separates a real measurement from a skill that simply never triggered. Record `skill_fired` (yes/no) for each arm.

7. **Interpret the fired-check before reporting a verdict:**
   - `skill_fired = no` in the **`with`** arm → the task never triggered the skill, so the arms were effectively identical. Report the run **inconclusive**, not "no effect": tell the user the task did not exercise the skill and suggest a task whose request matches the skill's stated triggers.
   - `skill_fired = yes` in the **`without`** arm → the control leaked (a plugin/global copy was still reachable). Report the run **invalid**, fix isolation, and re-run — do not trust the delta.
   - Only when the skill fired in `with` and did **not** fire in `without` is the delta a valid, directional measurement of the skill's real-world effect.

8. Worktrees are **always kept**. Never auto-remove — use `remove-worktrees` to clean up later.

9. Emit the report, substituting the **Report metric rows** from the resolved host reference for the `<host cost/token rows>` line:

```text
metric            | with                    | without
------------------|-------------------------|------------------------
skill_fired       | yes                     | no
gates_passed      | ...                     | ...
review_findings   | 0c 1h 2m                | 0c 3h 5m
<host cost/token rows>
duration          | ...                     | ...
turns             | ...                     | ...
tool_calls        | ...                     | ...
files_changed     | ...                     | ...
worktree          | eval/with-<run-id>      | eval/without-<run-id>
```

If the fired-check flagged the run **inconclusive** or **invalid** (step 7), say so above the table so the metric deltas are not read as an attributable result.

Both worktrees remain on disk; the user picks a winner and continues there or merges its branch.

## Validity guardrails

1. Identical **prompt**, **base commit**, and **model** across arms.
2. The skill must be absent from **all** load paths in the `without` arm. For a repo-local skill this is a single-file delete; a plugin or globally installed copy is shared by every worktree, so it must be isolated per the host reference's **Skill isolation** procedure (or the run stopped) — a reachable global copy silently invalidates the control. The `without`-arm fired-check confirms the removal actually took effect.
3. **Arm-blind reviewer** — the review subprocess receives the diff and project context, never the arm label.
4. Single-run results are **directional**, not statistical. Report them as such. If the user needs statistical confidence, they can request repeated runs and compare distributions.
5. The skill under test is assumed to be a non-review skill, so the same review skill auto-triggers identically in both arms.
6. **Fired-check.** The task is never modified to force the skill; triggering must happen naturally. A `with` arm where the skill never fired is **inconclusive** (the arms were identical), and a `without` arm where it did fire is **invalid** (leaked control). Only a run that fired in `with` and not in `without` yields an attributable delta.
