# API Design Standards

Design, implement, and review asynchronous REST operations and safe API
deprecation across service boundaries.

**Maturity: Experimental — 0.1.0.** Versioning windows, retention of removed
endpoints, and consumer-notice periods always depend on applicable contracts
and organization policy; this plugin makes no compliance claim.

The skill defines a portable contract for long-running operations — kickoff,
job status, polling, cancellation, callbacks, and webhooks — and a lifecycle
contract for deprecating and sunsetting endpoints with standard HTTP signals.

It deliberately does not mandate a vendor, framework, gateway, transport, exact
version-count limits, or notice periods. Map the baseline to repository and
organization policy and to the API's real consumer contract.

No network, credentials, telemetry, or storage are required. Review is
read-only unless implementation is requested.

See [CHANGELOG.md](CHANGELOG.md). Maintainer-only evaluation material lives
outside the distributed plugin in the
[repository test suite](../../tests/plugins/api-design-standards/).
