# Engineering Standards

Opinionated defaults for planning, implementing, and reviewing production
software across correctness, security, maintainability, verification, and
operations.

**Maturity: Experimental — 0.1.0.** Repository policy takes precedence, and the
plugin never treats a checklist as a compliance or production-readiness claim.

The plugin requires no network, credentials, telemetry, or persistent storage.
Review requests remain read-only; implementation happens only when requested.

## Threat model

| Threat | Control |
| --- | --- |
| Checklist-driven false confidence | Findings include evidence, uncertainty, and untested areas |
| Scope expansion during review | Review does not authorize edits |
| Unsafe repository instructions | External and repository input remains untrusted |
| Secret exposure | Credentials are prohibited in source, output, logs, tests, and arguments |
| Over-engineering | Prefer the smallest coherent design and established structure |

See [CHANGELOG.md](CHANGELOG.md) and [tests/REVIEW.md](tests/REVIEW.md).
