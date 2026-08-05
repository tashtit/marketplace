# Changelog

All notable changes to this plugin are documented here. Versions follow
[Semantic Versioning](https://semver.org/).

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
