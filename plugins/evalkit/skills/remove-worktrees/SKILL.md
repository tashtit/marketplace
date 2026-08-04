---
name: remove-worktrees
description: List and remove git worktrees and their associated branches, with a confirmation gate for any worktree holding uncommitted or unpushed work. Defaults to listing only. Use when asked to list, clean up, or remove worktrees — including leftovers from evaluate-skill, benchmark-skills, or compare-models runs.
---

# Remove Worktrees

Inspect and remove git worktrees (and their branches) that accumulate from harness runs or any other source. The main worktree is always excluded and can never be targeted.

**With no arguments this only lists** — nothing is removed until the user asks for a specific target, a prefix, or `all`.

## Arguments

| Param / subcommand  | Notes |
|---------------------|-------|
| *(no args)*         | Equivalent to `list` — print the worktree table and exit without removing anything. |
| `list`              | Print the worktree table (name, branch, commit, age, status). No removals. |
| `all`               | Remove every non-main worktree. Dirty worktrees are confirmed individually. |
| `--prefix <prefix>` | Remove all worktrees whose path starts with `<prefix>` (e.g. `eval/`, `bench/`, `mcmp/`). Case-sensitive; repeatable. |
| `<name>…`           | One or more worktree paths to remove (e.g. `eval/with-20260803-143021`). |
| `--keep-branches`   | Remove the worktree directory but leave the associated branch intact. |

`all`, `--prefix`, and `<name>` are mutually exclusive — mixing them is a usage error.

When invoked as `/remove-worktrees [args]`, parse from `$ARGUMENTS`. When triggered from a natural-language request, infer the mode from the user's message — but **default to `list` whenever the intent is not unambiguously destructive**, and show the user what would be removed before removing it.

## Steps

1. Determine the mode (`list` / `all` / `prefix[]` / `names[]`) and flags. If the mode is ambiguous or mixes mutually exclusive selectors, report the usage error and stop.

2. Run `git worktree list --porcelain` to enumerate all non-main worktrees. If none exist, print "No worktrees found." and stop.

3. **If mode is `list` or no args:** print the worktree table and stop.

4. Resolve targets:
   - `all` → every non-main worktree
   - `--prefix` → worktrees whose path starts with any supplied prefix
   - `<name>…` → worktrees matching the given paths; if any name is unresolvable, print "Unknown worktree: `<name>`." and stop **without removing anything**

   If the target list is empty, print "No matching worktrees found." and stop.

5. Print a pre-removal summary table of the targets.

6. For each target:

   **Dirty check** — a worktree is dirty if either:
   - `git -C <path> status --porcelain` returns non-empty output, or
   - `git -C <path> log @{u}..HEAD` returns any commits (skip this check if no upstream is configured)

   **If dirty:**
   - Show what would be lost (untracked/modified file count, unpushed commit count)
   - Prompt: "Worktree `<name>` has unsaved changes. Remove anyway? [y/N]"
   - No → print "Skipped `<name>`." and continue to the next target
   - Yes → `git worktree remove --force <path>`

   **If clean:** `git worktree remove <path>`

   **Branch cleanup** — unless `--keep-branches`: `git branch -D <branch>`. Failure here is non-fatal; print a warning and continue, since the worktree is already gone.

7. Print the final summary: "Removed N, skipped M."

## List / summary table format

```
worktree                        branch                    commit   age      status
─────────────────────────────── ───────────────────────── ──────── ──────── ──────
eval/with-20260803-143021       eval/with-20260803        a3f91c2  3d ago   clean
eval/without-20260803-143021    eval/without-20260803     b12e445  3d ago   clean
mcmp/A-20260805-090501          mcmp/A-20260805           d9a2f78  1d ago   dirty *
mcmp/B-20260805-090501          mcmp/B-20260805           c4b3e11  1d ago   clean
```

`dirty *` = uncommitted changes or unpushed commits.

## Error handling

| Condition | Behavior |
|-----------|----------|
| No worktrees exist | Print "No worktrees found." and exit cleanly. |
| Named worktree not found | Print "Unknown worktree: `<name>`." and abort before removing anything. |
| `--prefix` matches nothing | Print "No worktrees match prefix '`<prefix>`'." and exit cleanly. |
| `git worktree remove` fails | Print the error, mark it failed in the summary, continue with remaining targets. |
| `git branch -D` fails | Print a warning; non-fatal — the worktree was already removed. |
