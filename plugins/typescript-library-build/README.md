# TypeScript Library Build

Set up, implement, and review a dual ESM and CommonJS build and publish pipeline
for a TypeScript or JavaScript library so that both `import` and `require`
consumers get correct code and types.

**Maturity: Experimental — 0.2.0.** The registry, package manager, test runner,
release tool, supported runtime range, and repository release authority remain
repository-specific. This plugin does not certify a package or its supply chain.

The default is a small build that emits ESM and CJS output plus type
declarations, keeps runtime dependencies external, describes entry points with a
single `exports` map whose `types` condition is listed first, and ships a
generated minimal publish manifest instead of the development `package.json`.
Both output formats are verified from a packed tarball in a clean consumer with
`import` and `require` before the package is trusted.

It presents two proven shapes:

- a single-package Rollup build for one or a few entry points;
- a workspaces monorepo build using `tsc` for declarations and Rollup
  `preserveModules` for per-module ESM and CJS output across many entries.

It deliberately does not mandate a package manager, registry, test runner,
bundler alternative, monorepo tool, or Node.js version. `tsup` and `unbuild` are
noted only as alternatives to the Rollup default.

Running a build writes files under the output directory and may execute
`package.json` scripts. Publishing to a registry is an external side effect that
requires its own authorization and credentials. No credentials, network service,
or persistent storage are required by the plugin itself.

See [CHANGELOG.md](CHANGELOG.md). Maintainer-only evaluation material lives
outside the distributed plugin in the
[repository test suite](../../tests/plugins/typescript-library-build/).

## Installation

```bash
# Claude Code
claude plugin marketplace add tashtit/marketplace
claude plugin install typescript-library-build@tashtit

# GitHub Copilot CLI
copilot plugin marketplace add tashtit/marketplace
copilot plugin install typescript-library-build@tashtit

# OpenAI Codex CLI
codex plugin marketplace add tashtit/marketplace
codex plugin add typescript-library-build
```
