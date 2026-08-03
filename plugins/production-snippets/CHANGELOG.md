# Changelog

## 0.1.0 - 2026-08-03

- Added the seven-dimension reference implementation contract requiring
  supported versions, failure behavior, resource cleanup, security,
  observability, tests, and operational tradeoffs for every snippet.
- Added Redis connection lifecycle, pooling, timeout, and TLS guidance with a
  shared-pool, degrade-to-source read pattern.
- Added retry guidance with exponential backoff, full jitter, bounded budgets,
  and idempotency-key safety for non-idempotent operations.
- Added cache-aside guidance with TTL jitter, single-flight stampede protection,
  and delete-on-write invalidation.
- Added database and HTTP client connection-management guidance with bounded
  pools, timeouts, transactions, and TLS verification.
- Added health-check, readiness, and graceful-shutdown guidance with bounded
  draining.
- Added worked reference examples and maintainer evaluation scenarios.
