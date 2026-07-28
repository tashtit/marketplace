# Logging Standards

Design, implement, and review secure structured logging across services, jobs,
message consumers, and external boundaries.

**Maturity: Experimental — 0.1.0.** Retention and data classification always
depend on applicable policy; this plugin makes no compliance claim.

The skill defines a portable event contract and decision rules for severity,
exceptions, retries, boundary events, correlation, security/audit events,
sensitive data, sampling, delivery, retention, and failure testing.

It deliberately does not mandate a vendor, programming language, logging
library, output destination, retention period, or compliance framework. Map the
baseline to repository and organization policy.

No network, credentials, telemetry, or storage are required. Review is
read-only unless implementation is requested.

See [CHANGELOG.md](CHANGELOG.md). Maintainer-only evaluation material lives
outside the distributed plugin in the
[repository test suite](../../tests/plugins/logging-standards/).
