# Human review checklist

- [ ] The response treats the snippet as a reference implementation, not a
      paste-only fragment.
- [ ] Supported language, runtime, and library versions are stated, including
      version-specific behavior where relevant.
- [ ] Failure behavior is explicit for timeout, connection loss, and dependency
      outage, and one layer owns the final failure.
- [ ] Every resource (connection, socket, transaction, timer, background task)
      is released on success, error, and cancellation paths.
- [ ] Transport security (TLS) and peer authentication are required for off-host
      hops; certificate verification is not disabled outside isolated tests.
- [ ] Credentials and endpoints are placeholders from configuration, never
      inlined, logged, or placed in metric labels.
- [ ] Observability is specified: bounded structured events plus latency, error,
      and saturation metrics; no secrets or payloads.
- [ ] Tests are described and cover failure paths (timeout, pool exhaustion,
      retry exhaustion, rollback, shutdown mid-request).
- [ ] Operational tradeoffs (pool size, timeout, retry budget, TTL) and their
      costs are stated.
- [ ] Retries apply only to idempotent operations or use a deduplicated
      idempotency key, with bounded budget, backoff, and jitter.
- [ ] Cache-aside sets a TTL, protects the miss path from stampedes, invalidates
      on write, and degrades to the source on cache outage.
- [ ] Health checks separate liveness from readiness and shutdown drains
      in-flight work within a bounded window.
- [ ] No vendor, language, library, product, or compliance claim is invented.
- [ ] Output is materially equivalent on each claimed platform.

After reviewing a scenario on a platform, record the outcome in
`acceptance.json` beside this file. Results are pinned to the plugin version,
so a version bump requires a fresh review.
