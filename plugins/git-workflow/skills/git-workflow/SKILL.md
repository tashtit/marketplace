---
name: git-workflow
description: Prepare safe, focused Git commits and review-ready pull requests while preserving user work and repository policy. Use when inspecting changes, creating branches, splitting commits, writing Conventional Commit messages, rebasing safely, resolving conflicts, pushing branches, or creating and updating pull requests.
---

# Git Workflow

Turn an authorized change into reviewable history without losing work or
bypassing repository controls.

## Safety contract

- Treat unstaged, staged, untracked, stashed, and worktree content as user data.
- Never discard, overwrite, clean, reset, or force-push work unless the exact
  target and recovery implications are explicit and authorized.
- Never commit directly to the default branch.
- Do not change remotes, credentials, identity, signing policy, access, branch
  protection, or repository settings unless separately requested.
- Commit, push, create a pull request, merge, tag, or publish only when the user
  has requested that external effect.
- Follow repository-local instructions over Tashtit preferences when they are
  stricter. Surface material conflicts.

## Workflow

### 1. Inspect before mutation

Determine the repository root, current branch, default branch, remotes,
worktrees, status, staged diff, unstaged diff, and relevant recent history.
Identify pre-existing changes and keep them outside the task.

Verify repository ownership, authenticated account, local Git identity, and
signing configuration before the first remote operation or commit. Do not infer
or silently replace missing identity.

### 2. Establish a safe branch

Use a dedicated, descriptive non-default branch. If the current branch already
has a pull request for the same task, reuse it. Update from the remote using the
repository's documented strategy; default to fast-forward-only updates.

Do not rebase or merge across unrelated local work. Before history rewriting,
confirm that commits are unshared or that rewriting is explicitly authorized.

### 3. Shape the change

Keep commits cohesive and independently understandable. Separate unrelated
behavior, mechanical formatting, generated artifacts, and dependency updates
when that improves review or rollback. Do not split a change so finely that
intermediate commits are invalid or misleading.

Inspect the full staged diff before every commit. Generated files belong in the
same commit as their canonical source unless the repository requires otherwise.

### 4. Validate

Run the smallest complete set of relevant checks allowed by the task. Report
exactly what ran, what passed, what failed, and what was not run. Never convert
an unavailable check into a passing result.

### 5. Commit

Read [commit-messages.md](references/commit-messages.md). Use the repository's
commit convention; otherwise default to Conventional Commits 1.0.0.

Before committing:

- verify the branch is not the default branch;
- verify repository-local name and email;
- verify signing when required;
- ensure the staged diff contains only intended files;
- exclude secrets, local configuration, and build debris;
- omit co-author trailers unless project policy and the user require them.

### 6. Push and open the pull request

Re-verify the remote repository and authenticated account. Push only the task
branch, without force by default. Reuse an existing pull request for the branch.

The pull request MUST explain intent, material design decisions, risk, validation
evidence, and unresolved issues. Use a Conventional Commit-compatible title
when squash merging is expected. Link issues only when the relationship is
known; do not invent closing references.

### 7. Handoff

Return the branch, commit, checks, known limitations, and external pull-request
URL. Do not merge unless explicitly requested.

## Conflict and recovery rules

- Stop before resolving a semantic conflict when intent cannot be established
  from repository evidence.
- Prefer aborting an incomplete rebase or merge over improvising a resolution.
- Use normal revert commits for shared history. Reserve history rewriting for
  explicitly authorized, reviewed cases.
- Never use destructive recovery merely because it is faster.
