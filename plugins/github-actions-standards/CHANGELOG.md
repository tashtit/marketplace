# Changelog

## 0.4.0 - 2026-08-09

### Changed

- **Breaking:** renamed skill `github-actions-standards` to `tashtit-github-actions-standards`.
- Every Tashtit skill name now carries the `tashtit-` provenance prefix.
  Hosts flatten installed skills into one namespace and GitHub Copilot
  displays only the bare skill name, so unprefixed names can collide with
  or be indistinguishable from skills shipped by other marketplaces. See
  the skill naming policy in `docs/compatibility.md`.

## 0.3.0 - 2026-08-09

### Added

- Job naming and single-job conventions: short undecorated lowercase job
  identifiers, no job-level display names, a short stable workflow name, and
  consolidation guidance for checks that share a trigger. (This entry was
  backfilled; the release shipped without a changelog entry.)

## 0.2.1 - 2026-08-08

- Skill description now defers scored, read-only maturity audits to the
  maturity plugin's `evaluate-ci-workflow`, so overlapping "audit our GitHub
  Actions" requests route deterministically.
- Corrected the README maturity claim, which still advertised 0.1.0.

## 0.2.0 - 2026-08-06

- Added credential-persistence guidance: check out with
  `persist-credentials: false` unless a later step in the same job must
  authenticate as the repository, and declare `persist-credentials: true`
  explicitly when it does.
- Added scalar quoting guidance covering YAML type coercion in `with:`, `env:`,
  and runtime-version fields.
- Extended the review checklist with scalar quoting and credential persistence.

## 0.1.0 - 2026-07-29

- Added opinionated GitHub Actions CI, artifact, release, and deployment rules.
- Added trust-boundary, permissions, action-pinning, secret-lifecycle, and safe
  ephemeral-preview guidance.
- Added positive, failure, and unsafe acceptance scenarios.
