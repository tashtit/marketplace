# GitHub Actions Standards

Design, implement, and review secure, reproducible GitHub Actions workflows for
continuous integration, artifact verification, releases, and deployments.

**Maturity: Experimental — 0.1.0.** Repository policy, supported runtimes,
required checks, deployment environments, and release authority remain
repository-specific. This plugin does not certify a workflow or supply chain.

The default is a small CI workflow with explicit triggers, PR-aware
concurrency, bounded jobs, least-privilege permissions, immutable action
references, lockfile-based installs, and checks derived from repository
contracts. Release and deployment work is isolated behind successful CI,
trusted events, and protected environments.

The skill also covers artifact handoff, clean-room smoke tests, compatibility
matrices, integration-service lifecycle, caches, diagnostics, path filters,
untrusted pull requests, OIDC, and evidence-based verification.

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
