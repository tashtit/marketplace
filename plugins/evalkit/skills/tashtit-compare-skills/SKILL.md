---
name: tashtit-compare-skills
description: "Usage: /tashtit-compare-skills <skillA> <skillB> — requires two skills; static, no task or worktrees. Compare two skills' authoring quality side-by-side by reading their files and synthesizing a difference summary. Static analysis only; runs no coding task and creates no worktrees. Use when asked which of two specific named skills is better written, or to diff two versions of a skill. For a head-to-head run on a real coding task, use tashtit-benchmark-skills instead. Do not trigger on casual mention of comparing skills."
---

# Compare Skills

Compare two skills' authoring quality by reading their artifacts. Never runs a coding task.

This drives the bundled `skill-reviewer` agent independently on each skill, then synthesizes a difference summary from the two reports.

## Arguments

- `skillA` — first skill. Directory path or resolvable skill name.
- `skillB` — second skill. Directory path or resolvable skill name.

When invoked as `/tashtit-compare-skills <skillA> <skillB>`, read both from `$ARGUMENTS`. When triggered from a natural-language request, take the two skills named in the user's message. If fewer than two are identified, ask for the missing one rather than guessing.

## Steps

1. Determine `skillA` and `skillB` as described above. If two skills cannot be determined, ask the user which to compare and stop.

2. Check whether the `skill-reviewer` agent is available — it is available if it appears in the available agent list. It ships bundled with this plugin, so if it is NOT available, reply:

   > The skill-reviewer agent is required. It ships bundled with this plugin. Install evalkit with `/plugin`, then run `/reload-plugins`.

   Then stop.

3. Resolve both skill paths. For each, accept either a directory path or a skill name resolved against known skill load paths (`.claude/skills/`, `.github/skills/`, `src/skills/`, or any plugin skill path). If either is unresolvable, report the error and stop.

4. Invoke `skill-reviewer` on `skillA` and `skillB` **in parallel** — independent reads, neither review aware of the other.

5. Synthesize a difference summary from the two reports. Line up the dimensions the agent already produced; do not invent new criteria. This synthesis step is the only place the two skills are considered together.

6. Emit the comparison:

```text
skill comparison: <skillA> vs <skillB>

dimension              | <skillA>            | <skillB>
-----------------------|---------------------|---------------------
overall rating         | ...                 | ...
description quality    | ...                 | ...
SKILL.md word count    | ...                 | ...
progressive disclosure | ...                 | ...
critical issues        | ...                 | ...
major issues           | ...                 | ...

### Key differences
- <one bullet per material difference>

### Recommendation
<which skill is stronger, and the top fix that would close the gap>
```

Include only rows the two reports actually provide data for.

## Notes

- **Fair comparison.** Both skills are reviewed with the same model and the same agent config. Asymmetric config would bias the result.
- **Static only.** This makes no claim about task performance — use `tashtit-benchmark-skills` for that question.
- **No mutation.** `skill-reviewer` has read-only tools; this never edits the skills it reviews.
