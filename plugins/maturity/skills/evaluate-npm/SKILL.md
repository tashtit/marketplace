---
name: evaluate-npm
description: Evaluate npm projects in a local checkout for maturity issues — missing or conflicting lockfiles, outdated lockfile version, non-reproducible git/file dependencies, missing .npmrc or .nvmrc, and CI that installs with npm install instead of npm ci or with --ignore-scripts. Use when asked to audit or evaluate npm, package.json, lockfile, or Node dependency hygiene, or to score npm project maturity. Applies deterministic fixes only when the user explicitly asks.
---

# Evaluate npm

Evaluate npm projects against a fixed rule catalog by reading files only. Never
run `npm install`, `npm ci`, or any script to reach a finding. Fixes are applied
only when the user explicitly asks, and only for rules marked fixable below.

## Discovery

Find every `package.json` outside `node_modules` (any depth). For each, inspect
its siblings: `package-lock.json`, `yarn.lock`, `.npmrc`, `.nvmrc`. CI rules
inspect workflow files under `.github/workflows/`. A rule whose precondition
does not hold is **not relevant** and is excluded from the score.

## Rules

Each rule lists its stable id, precondition, detection, priority, weight,
whether it is automatically fixable, and the reference to cite.

### lockfile-missing (High, weight 8, report-only)

- Precondition: a `package.json` exists.
- Detect: no `package-lock.json` beside it.
- Why: without a lockfile, installs are not reproducible.
- Remediation (manual): run `npm install` to generate `package-lock.json` and
  commit it. Report only — generating a lockfile resolves the network and is
  not a static edit.
- Reference: <https://docs.npmjs.com/cli/configuring-npm/package-lock-json>

### lockfile-conflicting (High, weight 7, report-only)

- Detect: both `package-lock.json` and `yarn.lock` exist in the same project.
- Why: two lockfiles cause inconsistent resolution depending on the tool used.
- Remediation (manual): pick one package manager and delete the other lockfile.
  Report only — choosing the manager is a project decision.
- Reference: <https://docs.npmjs.com/cli/configuring-npm/package-lock-json>

### lockfile-outdated-version (Medium, weight 5, report-only)

- Precondition: `package-lock.json` exists and parses as JSON.
- Detect: its top-level `lockfileVersion` equals `1` (npm v5–v6).
- Why: v2/v3 lockfiles give deterministic resolution and better performance.
- Remediation (manual): delete the lockfile and regenerate it with npm v7+.
  Report only — regeneration resolves the network.
- Reference: <https://docs.npmjs.com/cli/configuring-npm/package-lock-json#lockfileversion>

### lockfile-non-reproducible-deps (Medium, weight 5, report-only)

- Precondition: a `package.json` exists and parses as JSON.
- Detect: any entry in `dependencies`, `devDependencies`, or `peerDependencies`
  whose version specifier is a git reference (`git+`, `github:`,
  `<owner>/<repo>` shorthand, or a git URL) or a `file:` reference.
- Why: these specifiers can change without a version bump, breaking builds
  silently and bypassing registry provenance.
- Remediation (manual): publish the dependency to the registry, or pin the git
  reference to an exact commit SHA. Report only — the correct target is a
  project decision.
- Reference: <https://docs.npmjs.com/cli/configuring-npm/package-json#dependencies>

### setup-npmrc (High, weight 5, report-only)

- Precondition: a `package-lock.json` exists (the project uses npm).
- Detect: no `.npmrc` beside it.
- Why: an `.npmrc` pins registry and install behavior so every environment
  resolves packages the same way.
- Remediation (manual): add an `.npmrc` with the project's registry
  configuration. Report only — registry values are environment-specific and
  must not be guessed.
- Reference: <https://docs.npmjs.com/cli/configuring-npm/npmrc>

### setup-nvmrc (Medium, weight 3, fixable)

- Precondition: a `package.json` exists.
- Detect: no `.nvmrc` beside it.
- Why: an `.nvmrc` pins the Node.js version across contributors and CI.
- Fix: create `.nvmrc` containing the major version derived from the
  `engines.node` range in `package.json`. Only apply when `engines.node`
  declares a concrete version; if it is absent or a wide range, report only and
  ask which version to pin.
- Reference: <https://github.com/nvm-sh/nvm#readme>

### npm-install-not-ci (Medium, weight 4, report-only)

- Precondition: a `package-lock.json` exists and a CI workflow exists under
  `.github/workflows/`.
- Detect: a CI step runs `npm install` (or `npm i`) rather than `npm ci` for a
  clean install.
- Why: `npm ci` installs strictly from the lockfile and fails on drift, giving
  reproducible CI installs; `npm install` may mutate the lockfile.
- Remediation (manual): replace the CI install step with `npm ci`. Report only —
  confirm the step is a clean-install step and not an intentional update.
- Reference: <https://docs.npmjs.com/cli/commands/npm-ci>

### npm-ignore-scripts (Medium, weight 4, report-only)

- Precondition: a `package-lock.json` exists.
- Detect: an install command in CI or scripts passes `--ignore-scripts`.
- Why: silently skipping lifecycle scripts can hide required build steps and
  mask supply-chain expectations.
- Remediation (manual): remove `--ignore-scripts`, or document why it is
  required. Report only.
- Reference: <https://docs.npmjs.com/cli/commands/npm-ci>

## Fixing on request

Only `setup-nvmrc` is automatically fixable, and only when `package.json`
declares a concrete `engines.node` version to derive from. Apply it only when
the user asks, and only to projects you reported. For every other rule, restate
the manual remediation instead of editing files, because each resolves the
network or requires a project decision.
