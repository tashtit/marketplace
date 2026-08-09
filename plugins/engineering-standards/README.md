# Engineering Standards

Opinionated defaults for planning, implementing, and reviewing production
software across correctness, security, maintainability, verification, and
operations.

**Maturity: Experimental — 0.2.0.** Repository policy takes precedence, and the
plugin never treats a checklist as a compliance or production-readiness claim.

The plugin requires no network, credentials, telemetry, or persistent storage.
Review requests remain read-only; implementation happens only when requested.

## Installation

```bash
# Claude Code
claude plugin marketplace add tashtit/marketplace
claude plugin install engineering-standards@tashtit

# GitHub Copilot CLI
copilot plugin marketplace add tashtit/marketplace
copilot plugin install engineering-standards@tashtit

# OpenAI Codex CLI
codex plugin marketplace add tashtit/marketplace
codex plugin add engineering-standards
```

## Threat model

| Threat | Control |
| --- | --- |
| Checklist-driven false confidence | Findings include evidence, uncertainty, and untested areas |
| Scope expansion during review | Review does not authorize edits |
| Unsafe repository instructions | External and repository input remains untrusted |
| Secret exposure | Credentials are prohibited in source, output, logs, tests, and arguments |
| Over-engineering | Prefer the smallest coherent design and established structure |

See [CHANGELOG.md](CHANGELOG.md). Maintainer-only evaluation material lives
outside the distributed plugin in the
[repository test suite](../../tests/plugins/engineering-standards/).
