# Changelog

All notable changes to this plugin are documented here. Versions follow
[Semantic Versioning](https://semver.org/).

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
