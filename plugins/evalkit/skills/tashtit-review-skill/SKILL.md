---
name: tashtit-review-skill
description: "Usage: /tashtit-review-skill <skill> — requires one skill; static, no task or worktrees. Review a single skill's authoring quality — structure, description and triggering effectiveness, and progressive disclosure — by reading its files. Static analysis only; runs no coding task and creates no worktrees. Use when asked to review, critique, or improve a specific named skill. To measure whether a skill changes coding-task outcomes, use tashtit-evaluate-skill instead. Do not trigger on casual mention of reviewing a skill."
---

# Review Skill

Assess one skill's authoring quality by reading its artifacts. Never runs a coding task.

This is a thin orchestrator over the bundled `skill-reviewer` agent; it does not re-implement review logic.

## Arguments

`skill` — the skill to review. A directory path (`plugins/foo/skills/bar/`) or a skill name resolved against the session's known skill load paths.

When invoked as `/tashtit-review-skill <skill>`, read it from `$ARGUMENTS`. When triggered from a natural-language request, take the skill named in the user's message. If no skill is identified, ask which one rather than guessing.

## Steps

1. Determine the target `skill` as described above. If none can be determined, ask the user which skill to review and stop.

2. Check whether the `skill-reviewer` agent is available — it is available if it appears in the available agent list. It ships bundled with this plugin, so if it is NOT available, reply:

   > The skill-reviewer agent is required. It ships bundled with this plugin. Install evalkit with `/plugin`, then run `/reload-plugins`.

   Then stop.

3. Resolve the skill path. Accept either:
   - A directory path (e.g. `plugins/foo/skills/bar/`)
   - A skill name resolved against known skill load paths (`.claude/skills/`, `.github/skills/`, `src/skills/`, or any plugin skill path)

   If the skill cannot be resolved to an existing directory, report the resolution error and stop.

4. Invoke the `skill-reviewer` agent on the resolved skill path.

5. Emit the agent's review verbatim: summary and word counts, description analysis, content quality, progressive disclosure assessment, severity-grouped issues, overall rating, and priority recommendations.

## Notes

- **Static only.** This makes no claim about task performance. A well-authored skill can still fail to improve outcomes — use `tashtit-evaluate-skill` for that question.
- **No mutation.** `skill-reviewer` has read-only tools; this never edits the skill it reviews.
