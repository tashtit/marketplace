# Logging Standards

Secure, structured production logging for useful operations without uncontrolled
sensitive data, cardinality, duplication, or cost.

**Maturity: Experimental — 0.1.0.** Retention and data classification always
depend on applicable policy; this plugin makes no compliance claim.

No network, credentials, telemetry, or storage are required. Review is
read-only unless implementation is requested.

Key controls include allowlisted fields, stable event schemas, consistent
severity, trace correlation, bounded values, sampling, sink-failure tolerance,
and tests.

See [CHANGELOG.md](CHANGELOG.md). Maintainer-only evaluation material lives
outside the distributed plugin in the
[repository test suite](../../tests/plugins/logging-standards/).
