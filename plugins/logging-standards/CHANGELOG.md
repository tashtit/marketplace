# Changelog

## 0.2.0 - 2026-08-09

### Changed

- **Breaking:** renamed skill `logging-standards` to `tashtit-logging-standards`.
- Every Tashtit skill name now carries the `tashtit-` provenance prefix.
  Hosts flatten installed skills into one namespace and GitHub Copilot
  displays only the bare skill name, so unprefixed names can collide with
  or be indistinguishable from skills shipped by other marketplaces. See
  the skill naming policy in `docs/compatibility.md`.

## 0.1.0 - 2026-07-27

- Added a portable structured-event contract and stable schema guidance.
- Added exception ownership, retry, HTTP, job, messaging, dependency, and
  correlation rules.
- Added security and audit event guidance without making compliance claims.
- Added sensitive-data, injection, cardinality, sampling, delivery, storage,
  retention, and failure-mode controls.
- Added authoritative standards references and expanded maintainer evaluation
  scenarios.
