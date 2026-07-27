# Git Workflow

Git Workflow turns an authorized change into focused commits and a review-ready
pull request while preserving local work, identity, signing, and repository
policy.

## Maturity

**Experimental — 0.1.0.** Behavioral compatibility still requires review on
each target agent.

## Defaults

- inspect status and policy before mutation;
- use a dedicated non-default branch;
- preserve unrelated work;
- use Conventional Commits when the repository has no stronger convention;
- validate before committing;
- avoid force pushes and destructive recovery;
- reuse the pull request for an existing branch;
- never merge without an explicit request.

The plugin can create commits and remote pull requests, so those effects require
the user's authorization. It does not change credentials, Git identity,
repository access, branch protection, or merge policy.

## Threat model

| Threat | Control |
| --- | --- |
| Loss of uncommitted work | Inspect all worktree states and prohibit implicit cleanup |
| Commit to protected/default branch | Resolve and compare the default branch before commit |
| Wrong account or repository | Verify both immediately before remote operations |
| History damage | No force push or rewrite without explicit scope and authorization |
| Secret inclusion | Inspect staged content and exclude credentials/local configuration |
| Misleading review evidence | Report checks exactly; unavailable checks are not passing |

See [CHANGELOG.md](CHANGELOG.md). Maintainer-only evaluation material lives
outside the distributed plugin in the
[repository test suite](../../tests/plugins/git-workflow/).
