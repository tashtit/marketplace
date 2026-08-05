# API Design Standards

Design, implement, and review the contract an HTTP API makes to its clients
over time: how long-running work behaves within a call, and how endpoints
retire across the life of the API.

**Maturity: Experimental — 0.1.0.** Versioning windows, retention of removed
endpoints, and consumer-notice periods always depend on applicable contracts
and organization policy; this plugin makes no compliance claim.

The skill treats both concerns as one promise — the client is never surprised.
**In-call**: kickoff, job status, polling, cancellation, callbacks, and
webhooks. **Over-time**: deprecating and sunsetting endpoints with standard HTTP
signals.

It deliberately does not mandate a vendor, framework, gateway, transport, exact
version-count limits, or notice periods. Map the baseline to repository and
organization policy and to the API's real consumer contract.

No network, credentials, telemetry, or storage are required. Review is
read-only unless implementation is requested.

See [CHANGELOG.md](CHANGELOG.md). Maintainer-only evaluation material lives
outside the distributed plugin in the
[repository test suite](../../tests/plugins/api-design-standards/).
