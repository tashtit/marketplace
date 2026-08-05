---
name: api-design-standards
description: Design, implement, or review the contract an HTTP API makes to its clients over time — how long-running work behaves and how endpoints are versioned and retired. Use when adding async operations, job status and polling, cancellation, callbacks or webhooks, choosing a versioning scheme (path or media type), or when deprecating and sunsetting endpoints with standard HTTP signals.
---

# API Design Standards

An API is a contract with its clients, and that contract has to hold across two
axes of time: within a single call, and across the life of an endpoint. This
skill governs both. **In-call behavior**: give a client a predictable way to
start slow work, observe it, and stop it. **Over-time behavior**: give a client
an honest, machine-readable warning — on a schedule — before an endpoint
changes or disappears. Both are the same promise: the client is never
surprised.

Apply explicit user requirements and repository or organization API policy
first. Treat this skill as a vendor-neutral baseline and a Tashtit convention,
not a certification.

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

## In-call behavior: asynchronous operations

When an operation can exceed a normal request timeout, do not hold the
connection open.

- A kickoff request MUST use a method that expresses intent to change state
  (`POST`, `PUT`, `PATCH`, or `DELETE`), never `GET`.
- A kickoff that is accepted but not yet complete MUST return `202 Accepted`
  and MUST point the client to where progress can be observed, using a
  `Content-Location` (or `Location`) header with the job resource URL.
- Where a single operation may be answered either inline or asynchronously, a
  client MAY signal its preference with `Prefer: respond-async` (RFC 7240) and
  the server SHOULD echo `Preference-Applied` when it honors it.
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
- The server MAY advertise remaining budget with `RateLimit` and
  `RateLimit-Policy` headers (IETF draft) so a client can self-throttle before
  it is refused.
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

## Over-time behavior: API lifecycle and deprecation

An endpoint's contract changes over its life. Versioning is how you make a
breaking change without breaking existing clients; deprecation is how you retire
the version they leave behind. Treat the two as one flow: publish the next
version, then deprecate and sunset the previous one.

### Versioning

- Every published API MUST carry an explicit version. Do not ship an
  unversioned public endpoint and retrofit a version later.
- Choose **one** scheme and apply it consistently across the whole API:
  - **URI path** (for example `/api/v1/...`) — the most common and most
    visible; easy to route, cache, and reason about. A good default for
    external, human-facing APIs.
  - **Media type / content negotiation** (for example
    `Accept: application/vnd.example.v2+json`) — keeps one URL per resource and
    versions the representation; better when the resource identity is stable and
    only the shape changes.
  - **Custom header or query parameter** — acceptable when a gateway or
    constraint requires it, but the least discoverable; prefer the two above.
  Do not mix schemes in one API.
- Bump the **major** version only for a breaking change: removing or renaming a
  field, tightening validation, changing a type, or changing the meaning of a
  response. Additive, backward-compatible changes (new optional fields, new
  endpoints) MUST NOT require a new version — clients ignore what they do not
  know.
- Keep the version granularity coarse. Version the API (or a stable resource
  group), not every individual endpoint, so clients are not tracking dozens of
  independent versions.
- A new major version and the deprecation of its predecessor are the same
  event: ship `/v2`, then start the `/v1` deprecation clock with the signals
  below and a `Link` to the `/v2` migration guide.

### Deprecation and sunset

Removing or replacing a published endpoint or version is a breaking change for
someone. Signal it in-band and on a schedule.

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

- Versioning: use the single scheme defined above consistently; never mix path
  and media-type versioning in one API.
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
- Every public API carries an explicit version under one scheme; major bumps
  are reserved for breaking changes and additive changes do not bump.
- One versioning scheme and one error format are used consistently, and no
  secret rides in a URL or identifier.
