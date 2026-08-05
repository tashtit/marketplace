# Asynchronous operations reference

Concrete shapes for the async contract in `SKILL.md`. Paths, media types, and
the error envelope are illustrative; use the repository's existing conventions.

## Kickoff

```http
POST /api/v1/exports
Content-Type: application/json
Idempotency-Key: 4f1a-9d2c-8b7e
Prefer: respond-async

{ "format": "csv", "filter": { "since": "2026-01-01" } }
```

```http
HTTP/1.1 202 Accepted
Content-Location: /api/v1/jobs/8c2f
Preference-Applied: respond-async
```

- Use a state-changing method, never `GET`.
- Return `202` when the work is accepted but not finished.
- Point at the job resource with `Content-Location` (or `Location`).
- An `Idempotency-Key` lets a client safely retry a kickoff: the same key
  returns the same job instead of starting a second one.
- `Prefer: respond-async` lets a client opt into async where inline is also
  possible; echo `Preference-Applied` when honored.
- If the work finishes inline, return the final `2xx` result instead; do not
  invent a job resource that is never needed.

## Job status

```http
GET /api/v1/jobs/8c2f
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "8c2f",
  "state": "running",
  "percentComplete": 42,
  "createdAt": "2026-08-04T10:00:00Z",
  "updatedAt": "2026-08-04T10:00:20Z"
}
```

Succeeded:

```json
{
  "id": "8c2f",
  "state": "succeeded",
  "completedAt": "2026-08-04T10:01:05Z",
  "result": { "href": "/api/v1/exports/8c2f/download" }
}
```

Failed — use the repository's error format (RFC 9457 shown):

```json
{
  "id": "8c2f",
  "state": "failed",
  "error": {
    "type": "https://errors.example/export-source-unavailable",
    "title": "Export source unavailable",
    "status": 502
  }
}
```

- `state` comes from a small explicit set (`pending`, `running`, `succeeded`,
  `failed`, `cancelled`).
- A client can distinguish active from terminal from failed without parsing
  prose.
- Reads never mutate the job.

## Polling and rate limits

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 5
RateLimit: limit=100, remaining=0, reset=5
RateLimit-Policy: 100;w=60
```

- Bound polling with `429` + `Retry-After`, or advertise a poll interval.
- Optionally expose remaining budget with `RateLimit` / `RateLimit-Policy` so a
  client can self-throttle before it is refused.
- Keep status reads cheap; do not block until completion unless long-poll is a
  deliberate, bounded, documented choice.

## Cancellation

```http
POST /api/v1/jobs/8c2f/actions/cancel
```

- Cancel via an explicit action, not by deleting the job resource.
- Idempotent: cancelling a terminal job returns its current state.
- Document what cancellation actually guarantees (best-effort stop vs. durable
  compensation).

## Callbacks and webhooks

- Describe delivery in the API spec: OpenAPI `callbacks` for per-request
  callbacks, `webhooks` for standing subscriptions.
- A subscription API supports register, fetch, enable/disable, validate, and
  delete, so a consumer can stop delivery without operator help.
- The receiver authenticates the caller and verifies a signature or shared
  secret before acting.
- Delivery retries with backoff and is safe to receive more than once; use
  idempotency keys.
- Delivery never replaces an authoritative job status resource to reconcile
  against.

## References

- RFC 9457 — Problem Details for HTTP APIs.
  <https://www.rfc-editor.org/rfc/rfc9457>
- RFC 7807 — Problem Details (obsoleted by 9457; still widely deployed).
  <https://www.rfc-editor.org/rfc/rfc7807>
- RFC 7240 — Prefer Header for HTTP (`respond-async`).
  <https://www.rfc-editor.org/rfc/rfc7240>
- RateLimit header fields for HTTP (IETF draft).
  <https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/>
- OpenAPI Specification (callbacks and webhooks).
  <https://spec.openapis.org/oas/latest.html>
