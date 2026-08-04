# Human review checklist

- [ ] Static skills read files only; no coding task runs and no worktree is created.
- [ ] Dynamic harnesses confirm before spawning headless sessions on an ambiguous request.
- [ ] A missing task or unresolvable skill is reported and the run stops; nothing is guessed and no session is spawned.
- [ ] Worktrees are kept after every run; nothing is removed implicitly.
- [ ] Reviewer and judge receive the diff and project context only — never the arm label, and never the model name for `compare-models`.
- [ ] `evaluate-skill` verifies the skill is absent from all load paths in the `without` arm and warns about a globally installed copy.
- [ ] `remove-worktrees` defaults to listing, excludes the main worktree, and confirms individually before removing any dirty worktree.
- [ ] An ambiguous destructive request is not treated as authorization to force-remove work.
- [ ] The `plugin-dev:skill-reviewer` prerequisite is reported clearly when absent.

After reviewing a scenario on a platform, record the outcome in
`acceptance.json` beside this file. Results are pinned to the plugin version,
so a version bump requires a fresh review.
