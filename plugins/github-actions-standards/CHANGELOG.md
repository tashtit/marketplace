# Changelog

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
