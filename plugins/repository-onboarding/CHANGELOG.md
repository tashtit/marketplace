# Changelog

All notable changes to this plugin are documented here. Versions follow
[Semantic Versioning](https://semver.org/).

## 0.2.0 - 2026-08-09

### Changed

- **Breaking:** renamed skill `repository-onboarding` to `tashtit-repository-onboarding`.
- Every Tashtit skill name now carries the `tashtit-` provenance prefix.
  Hosts flatten installed skills into one namespace and GitHub Copilot
  displays only the bare skill name, so unprefixed names can collide with
  or be indistinguishable from skills shipped by other marketplaces. See
  the skill naming policy in `docs/compatibility.md`.

## 0.1.0 - 2026-07-27

### Added

- Read-only repository discovery and evidence classification.
- Structured onboarding report format.
- Explicit prompt-injection, secret-handling, and no-execution guardrails.
- Positive, failure, and unsafe-input acceptance scenarios.
