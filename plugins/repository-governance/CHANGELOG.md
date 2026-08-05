# Changelog

## 0.1.0 - 2026-08-05

- Merged the `repository-settings` and `repository-policy` plugins into one
  `repository-governance` plugin, since auditing and applying repository
  governance are two modes of a single capability.
- Added a `repository-governance` router skill that dispatches between the
  audit-only `repository-settings` skill and the mutating `repository-policy`
  skill.
- Preserved the audit-first governance guidance: rulesets, branch protection,
  reviews, checks, signing, merge controls, CODEOWNERS, templates, security
  features, dependency updates, and reversible policy-as-code.
- Preserved the opinionated apply path: squash-only merges with the pull-request
  title and commit details, auto-merge, head-branch deletion, suggested branch
  updates, unused wiki and projects disabling, and ruleset application from a
  reviewed definition with validated status checks and bypass actors.
- Consolidated the positive, failure, and unsafe acceptance scenarios from both
  source plugins.
