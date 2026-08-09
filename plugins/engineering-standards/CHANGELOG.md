# Changelog

## 0.2.0 - 2026-08-09

### Changed

- **Breaking:** renamed skill `engineering-standards` to `tashtit-engineering-standards`.
- Every Tashtit skill name now carries the `tashtit-` provenance prefix.
  Hosts flatten installed skills into one namespace and GitHub Copilot
  displays only the bare skill name, so unprefixed names can collide with
  or be indistinguishable from skills shipped by other marketplaces. See
  the skill naming policy in `docs/compatibility.md`.

## 0.1.0 - 2026-07-27

- Added production engineering standards and definition of done.
- Added security, testing, operational, and review-output guardrails.
- Added positive, failure, and unsafe acceptance scenarios.
