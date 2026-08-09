# Changelog

All notable changes to this plugin are documented here. Versions follow
[Semantic Versioning](https://semver.org/).

## 0.4.0 - 2026-08-09

### Changed

- **Breaking:** renamed skill `maturity` to `tashtit-maturity`.
- **Breaking:** renamed skill `evaluate-ci-workflow` to `tashtit-evaluate-ci-workflow`.
- **Breaking:** renamed skill `evaluate-dockerfile` to `tashtit-evaluate-dockerfile`.
- **Breaking:** renamed skill `evaluate-npm` to `tashtit-evaluate-npm`.
- **Breaking:** renamed skill `evaluate-repository-hygiene` to `tashtit-evaluate-repository-hygiene`.
- Every Tashtit skill name now carries the `tashtit-` provenance prefix.
  Hosts flatten installed skills into one namespace and GitHub Copilot
  displays only the bare skill name, so unprefixed names can collide with
  or be indistinguishable from skills shipped by other marketplaces. See
  the skill naming policy in `docs/compatibility.md`.

## 0.3.1 - 2026-08-08

### Changed

- Router skill description now names all four ecosystems (Dockerfiles, npm,
  repository hygiene, and CI workflows) so general maturity requests route
  through it; it previously mentioned only Dockerfiles and npm.
- `evaluate-ci-workflow` and `evaluate-repository-hygiene` descriptions now
  state their boundaries with `github-actions-standards` and
  `repository-settings`, so overlapping requests route deterministically.
- Default prompt now covers all four ecosystems.

## 0.3.0 - 2026-08-06

### Added

- `evaluate-ci-workflow` skill with six GitHub Actions CI-workflow rules
  (missing CI workflow, unpinned remote actions, overly permissive
  `GITHUB_TOKEN` permissions, missing workflow permissions, jobs without a
  timeout, and unsafe `pull_request_target` checkout of untrusted code). Every
  rule is report-only and aligns with the `github-actions-standards` skill.
- Positive, failure, and unsafe-input acceptance scenarios for the new skill.

### Changed

- Router skill now routes to four ecosystems and discovers CI-workflow files
  during scope establishment; `setup-ci-workflow` is always relevant while the
  remaining CI rules require a parseable workflow.

## 0.2.0 - 2026-08-05

### Added

- `evaluate-repository-hygiene` skill with five collaboration and documentation
  rules (missing CODEOWNERS, malformed CODEOWNERS, missing README, missing
  CONTRIBUTING, missing `.editorconfig`).
- Opt-in, deterministic fix for `setup-editorconfig` (writes a portable default
  `.editorconfig`); every other hygiene rule is report-only.
- Positive, failure, and unsafe-input acceptance scenarios for the new skill.

### Changed

- Router skill now routes to three ecosystems and discovers repository-hygiene
  files during scope establishment.

## 0.1.0 - 2026-08-05

### Added

- Router skill defining the read-only safety contract, weighted maturity
  scoring model, and report format.
- `evaluate-dockerfile` skill with five Node.js Dockerfile rules (Alpine base,
  source-before-install, end-of-life Node.js, `.nvmrc` compatibility, npm as the
  container command).
- `evaluate-npm` skill with eight package.json, lockfile, `.npmrc`, `.nvmrc`,
  and CI install rules.
- Opt-in, deterministic fixes for `dockerfile-nodejs-slim` and `setup-nvmrc`;
  every other rule is report-only.
- Positive, failure, and unsafe-input acceptance scenarios.
