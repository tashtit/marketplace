# GitHub Actions Standards

Design, implement, and review secure, reproducible GitHub Actions workflows for
continuous integration, artifact verification, releases, and deployments.

**Maturity: Experimental — 0.5.0.** Repository policy, supported runtimes,
required checks, deployment environments, and release authority remain
repository-specific. This plugin does not certify a workflow or supply chain.

Start with a single `ci` job in `ci.yml`. A package can add smoke tests of
the packed artifact, a desktop app can add platform-specific packaging, and
an existing publisher can run downstream of its required checks. The skill
explains when a separate workflow earns its place and how to preserve dry
runs, required checks and approvals when simplifying an existing pipeline.

Routine jobs use direct commands and safe action defaults with no stored
secrets. The worked YAML example shows the property order, quoted step
names, spacing and 160-column inline convention. GitHub-authored actions use
exact release tags. Third-party actions use full upstream commit SHAs, and
unverified actions require explicit user approval.

The skill also covers artifact handoff, clean-room smoke tests, compatibility
matrices, integration-service lifecycle, caches, diagnostics, path filters,
untrusted pull requests, isolated preview deployments, secret lifecycle, OIDC,
and evidence-based verification.

It deliberately does not mandate a programming language, package manager, task
runner, runner provider, registry, deployment platform, release tool, coverage
service, or observability vendor.

Workflow changes write repository files and may consume Actions minutes when
they run. Publishing, deployment, secret creation, environment changes, and
repository settings require their own authorization. No credentials, network
service, or persistent storage are required by the plugin itself.

See [CHANGELOG.md](CHANGELOG.md). Maintainer-only evaluation material lives
outside the distributed plugin in the
[repository test suite](../../tests/plugins/github-actions-standards/).

## Installation

```bash
# Claude Code
claude plugin marketplace add tashtit/marketplace
claude plugin install github-actions-standards@tashtit

# GitHub Copilot CLI
copilot plugin marketplace add tashtit/marketplace
copilot plugin install github-actions-standards@tashtit

# OpenAI Codex CLI
codex plugin marketplace add tashtit/marketplace
codex plugin add github-actions-standards
```
