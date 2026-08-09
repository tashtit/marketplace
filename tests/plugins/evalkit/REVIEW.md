# Human review checklist

- [ ] Static skills read files only; no coding task runs and no worktree is created.
- [ ] Dynamic harnesses confirm before spawning headless sessions on an ambiguous request.
- [ ] A missing task or unresolvable skill is reported and the run stops; nothing is guessed and no session is spawned.
- [ ] Worktrees are kept after every run; nothing is removed implicitly.
- [ ] Reviewer and judge receive the diff and project context only — never the arm label, and never the model name for `tashtit-compare-models`.
- [ ] `tashtit-evaluate-skill` verifies the skill is absent from all load paths in the `without` arm and warns about a globally installed copy.
- [ ] `tashtit-remove-worktrees` defaults to listing, excludes the main worktree, and confirms individually before removing any dirty worktree.
- [ ] An ambiguous destructive request is not treated as authorization to force-remove work.
- [ ] Dynamic harnesses resolve the host via `scripts/resolve-host.sh` first, read only the resolved reference, and fail closed (stop) on an unknown host.
- [ ] The bundled `skill-reviewer` prerequisite is reported clearly when the agent is absent.

After reviewing a scenario on a platform, record the outcome in
`acceptance.json` beside this file. Results are pinned to the plugin version,
so a version bump requires a fresh review.
