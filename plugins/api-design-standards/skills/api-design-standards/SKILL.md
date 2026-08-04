---
name: api-design-standards
description: Design, implement, or review asynchronous REST operations and safe API deprecation. Use when adding long-running endpoints, job status and polling, cancellation, callbacks or webhooks, versioning, or when deprecating and sunsetting endpoints with standard HTTP signals.
---

# API Design Standards

Give an HTTP client a predictable way to start slow work, observe it, and stop
it, and give a consumer an honest, machine-readable warning before an endpoint
disappears. Apply explicit user requirements and repository or organization API
policy first. Treat this skill as a vendor-neutral baseline and a Tashtit
convention, not a certification.

Use `MUST`, `SHOULD`, and `MAY` deliberately. Do not turn one API's base path,
gateway, framework, version count, or notice period into a universal rule.

## Inspect before designing

Read the repository's agent instructions, existing API specification (OpenAPI or
equivalent), routing and versioning conventions, error format, authentication
model, existing job or event patterns, and any published consumer contract.
Reuse the established base path, media types, error envelope, and identifier
style rather than introducing a second convention.

Confirm what the request actually needs before adding machinery. A response
that already fits inside a normal request timeout SHOULD stay synchronous;
asynchronous plumbing is justified only when the work can outlast a request.

## Asynchronous operations

When an operation can exceed a normal request timeout, do not hold the
connection open.

- A kickoff request MUST use a method that expresses intent to change state
  (`POST`, `PUT`, `PATCH`, or `DELETE`), never `GET`.
- A kickoff that is accepted but not yet complete MUST return `202 Accepted`
  and MUST point the client to where progress can be observed, using a
  `Content-Location` (or `Location`) header with the job resource URL.
- The job MUST be addressable as its own resource (for example
  `GET /jobs/{id}`), so status is a plain read, not a side effect.
- If the same request completes fast enough to answer inline, returning the
  final `2xx` result directly is acceptable; do not force a job resource when
  none is needed.

### Job status representation

A job status resource SHOULD expose, in the repository's existing envelope:

- a `state` from a small, explicit set (for example `pending`, `running`,
  `succeeded`, `failed`, `cancelled`);
- progress when it is knowable (for example `percentComplete`), without
  fabricating precision;
- timestamps for creation, last update, and completion;
- a link to the result resource when the job succeeds;
- a structured error using the repository's error format (RFC 9457 problem
  details is a good default) when the job fails.

State MUST be a terminal-versus-active distinction the client can act on; a
client MUST be able to tell "still working" from "done" from "failed" without
parsing free text.

### Polling and rate limits

- Clients poll the job resource. The server SHOULD bound polling cost: return
  `429 Too Many Requests` with a `Retry-After` header, or advertise a poll
  interval, rather than letting clients hammer the endpoint.
- Reads of an unfinished job MUST stay cheap and MUST NOT mutate the job.
- Do not block the status request until the job finishes; long-poll only if it
  is a deliberate, documented choice with a bounded timeout.

### Cancellation

- Long-running jobs SHOULD be cancellable through an explicit action (for
  example `POST /jobs/{id}/actions/cancel`), not by deleting the job resource,
  so the record and its audit trail survive.
- Cancellation MUST be idempotent: cancelling an already-terminal job returns
  its current state rather than erroring.
- Define what cancellation guarantees — best-effort stop, or a durable
  compensating action — and do not overpromise rollback the system cannot
  perform.

### Callbacks and webhooks

When a consumer should be told about completion instead of polling:

- Prefer describing delivery in the API specification (OpenAPI callbacks for
  per-request callbacks, webhooks for standing subscriptions) so the contract
  is discoverable.
- A webhook subscription API SHOULD support register, fetch, enable or disable,
  validate, and delete. A consumer MUST be able to stop delivery without
  contacting an operator.
- Delivery is a request into an untrusted network. The receiver MUST
  authenticate callers (service-to-service credential or signed payload) and
  MUST verify a signature or shared secret before acting; treat every inbound
  payload as untrusted input.
- Delivery MUST be retried with backoff and MUST be safe to receive more than
  once; require or document idempotency keys so a duplicate delivery is not
  processed twice.
- Callbacks and webhooks complement polling; they do not remove the need for an
  authoritative job status resource the consumer can reconcile against.

See `references/async-operations.md` for concrete shapes and status codes.

## API lifecycle and deprecation

Removing or replacing a published endpoint is a breaking change for someone.
Signal it in-band and on a schedule.

- Distinguish two phases explicitly: a **deprecation period**, during which the
  endpoint keeps working while clients migrate, and a **sunset date**, the hard
  removal point.
- A deprecated endpoint MUST keep functioning until its sunset date and MUST
  advertise its status in responses:
  - a `Deprecation` header (RFC 8594) marking it deprecated;
  - a `Sunset` header (RFC 8594) with the removal date when one is set;
  - a `Link` header pointing to migration or successor documentation when it
    exists;
  - `deprecated: true` on the operation in the API specification.
- After the sunset date the endpoint SHOULD return `410 Gone` and SHOULD keep
  returning the deprecation and successor `Link` headers so late clients get an
  actionable signal rather than a bare `404`.
- Limit how many versions run at once and give consumers a realistic migration
  window. The exact version count and window depend on the consumer contract
  (internal callers you control tolerate shorter windows than external ones);
  state the chosen limits, do not invent a universal number, and never shorten
  an external contract without agreement.
- Announce deprecation through the channels the consumers actually watch
  (changelog, release notes, migration guide) in addition to the in-band
  headers; headers alone are not notice.
- Base removal on observed usage where possible. Prefer measuring real traffic
  to an endpoint before sunsetting it over assuming it is unused.

See `references/lifecycle.md` for the header set and phase transitions.

## Cross-cutting requirements

- Versioning: choose one scheme (path or media type) consistent with the
  repository and keep it; do not mix schemes in one API.
- Errors: use one structured error format across sync responses, async job
  failures, and delivery failures. RFC 9457 problem details is a strong
  default.
- Idempotency: state-changing kickoffs, cancellation, and delivery handlers
  MUST be safe to retry.
- Security: never place secrets or tokens in URLs, job identifiers, or status
  payloads; authenticate delivery endpoints; treat all inbound payloads and
  callback URLs as untrusted.

## Definition of done

- Long-running operations return `202` with a discoverable job resource, a
  clear state model, bounded polling, and cancellation where it applies.
- Any callback or webhook path authenticates callers, verifies payloads,
  retries with backoff, and tolerates duplicate delivery.
- Deprecated endpoints carry `Deprecation`, `Sunset`, and successor `Link`
  signals, a spec flag, a stated version and window policy, and out-of-band
  notice; sunset endpoints return `410 Gone`.
- One versioning scheme and one error format are used consistently, and no
  secret rides in a URL or identifier.
