# Changelog

## 0.2.0 - 2026-08-09

### Changed

- **Breaking:** renamed skill `git-workflow` to `tashtit-git-workflow`.
- Every Tashtit skill name now carries the `tashtit-` provenance prefix.
  Hosts flatten installed skills into one namespace and GitHub Copilot
  displays only the bare skill name, so unprefixed names can collide with
  or be indistinguishable from skills shipped by other marketplaces. See
  the skill naming policy in `docs/compatibility.md`.

## 0.1.0 - 2026-07-27

- Added safe branch, commit, push, pull-request, conflict, and recovery guidance.
- Added Conventional Commit defaults and mutation authorization boundaries.
- Inlined the commit-message standard into the skill body because it is read on
  the common commit path, removing an always-hit reference read.
- Added positive, failure, and unsafe acceptance scenarios.
