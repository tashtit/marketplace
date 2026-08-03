# Repository Settings

Audit, plan, and review GitHub repository settings and policy-as-code without
silently changing shared governance.

**Maturity: Experimental - 0.1.0.** Repository, organization, enterprise, and
regulatory policy remain authoritative. This plugin does not certify compliance
or configuration security.

The default is audit-only: collect evidence, identify gaps, propose a scoped
plan, require explicit confirmation, and retain a tested rollback before any
settings mutation. The skill covers rulesets and protected branches, reviews,
checks, signing, merge methods, CODEOWNERS, templates, security features,
dependency updates, and reversible policy-as-code.

It does not mandate a review count, check list, signature method, merge
strategy, GitHub plan, infrastructure provider, or organization policy. Map the
baseline to the repository's risk model and approved governance process.

Read-only inspection may use documented GitHub APIs or CLI commands with least
privilege and disclosed network access. The plugin itself requires no
credentials, network service, telemetry, or persistent storage.

See [CHANGELOG.md](CHANGELOG.md). Maintainer-only evaluation material lives
outside the distributed plugin in the
[repository test suite](../../tests/plugins/repository-settings/).
