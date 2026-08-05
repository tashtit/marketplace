# Changelog

## 0.1.0 - 2026-08-04

- Framed the skill around the API contract along two axes: in-call behavior and
  over-time behavior.
- Added an asynchronous REST contract for job kickoff (`202 Accepted` with a
  status location), job status representation, polling with rate limits, and
  cancellation.
- Added client-controlled async opt-in (`Prefer: respond-async`), idempotent
  kickoff via `Idempotency-Key`, and optional `RateLimit` budget headers.
- Added callback and webhook guidance, including subscription management and
  service-to-service authentication of delivery endpoints.
- Added an API lifecycle and deprecation contract using `Deprecation`,
  `Sunset`, and `Link` headers, OpenAPI `deprecated` flags, and `410 Gone`
  after sunset, without inventing fixed version or notice windows.
- Added authoritative references (RFC 9457, RFC 8594, RFC 7807, RFC 7240,
  RateLimit draft, OpenAPI) and maintainer evaluation scenarios.
