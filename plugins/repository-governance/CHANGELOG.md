# Changelog

## 0.2.0 - 2026-08-09

### Changed

- **Breaking:** renamed skill `repository-governance` to `tashtit-repository-governance`.
- **Breaking:** renamed skill `repository-policy` to `tashtit-repository-policy`.
- **Breaking:** renamed skill `repository-settings` to `tashtit-repository-settings`.
- Every Tashtit skill name now carries the `tashtit-` provenance prefix.
  Hosts flatten installed skills into one namespace and GitHub Copilot
  displays only the bare skill name, so unprefixed names can collide with
  or be indistinguishable from skills shipped by other marketplaces. See
  the skill naming policy in `docs/compatibility.md`.

## 0.1.1 - 2026-08-08

- `repository-settings` description now states that it audits GitHub-hosted
  configuration and defers local-checkout file hygiene to the maturity
  plugin's `evaluate-repository-hygiene`, so overlapping CODEOWNERS audit
  requests route deterministically.

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
