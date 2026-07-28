---
name: logging-standards
description: Design, implement, or review secure, structured production logging and audit events across services, jobs, and message consumers. Use when defining event schemas, adding or reviewing logs, handling exceptions and retries, propagating trace context, controlling sensitive data or cardinality, planning retention and access, or diagnosing noisy, unsafe, duplicated, missing, or unusable telemetry.
---

# Logging Standards

Create logs that answer operational and security questions without becoming an
unbounded sensitive-data store. Apply repository policy and applicable legal,
privacy, and regulatory requirements first. Treat this skill as a
vendor-neutral baseline, not a compliance certification.

Use `MUST`, `SHOULD`, and `MAY` to distinguish requirements, strong defaults,
and optional practices. Map the portable field names below to an established
organizational or telemetry schema rather than maintaining two schemas.

## Decide before emitting

For each proposed event:

1. State the operational, security, or audit question it answers.
2. Identify the event owner and the system boundary where it belongs.
3. Reuse the existing logger, schema, severity model, trace context, and error
   taxonomy.
4. Define safe fields, types, bounds, and cardinality before implementation.
5. Decide who consumes the event and whether it drives an alert, investigation,
   audit trail, metric, or debugging workflow.
6. Remove the event if an existing signal answers the same question.

Do not use logs as the authoritative business ledger, analytics warehouse,
distributed trace, or metrics system. Link to those systems with safe
identifiers when needed.

## Portable event contract

Emit structured events. A production event SHOULD contain:

| Field | Contract |
| --- | --- |
| `timestamp` | Event time in UTC with an unambiguous offset; preserve ingestion time separately when the platform supports it. |
| `severity` | One normalized level from the severity policy. |
| `event.name` | Stable, low-cardinality machine name describing what happened. |
| `event.version` | Schema version when an event contract can evolve independently of the deployment. |
| `message` | Optional bounded human summary; never the primary query contract. |
| `service.name` | Stable producer identity when it is not supplied by the collector. |
| `component` | Stable subsystem, module, worker, or boundary. |
| `outcome` | A small documented set such as `success`, `failure`, `unknown`, or `degraded`. |
| `attributes` | Typed, allowlisted, bounded event-specific facts. |
| `trace_id` / `span_id` | Existing distributed trace context when available and safe; preserve trace flags when the transport defines them. |

Add deployment version, environment, region, host, or runtime identity at the
collector/resource layer when reliable there. Do not make every application
call repeat static infrastructure metadata.

Keep field meanings and types stable across versions. Reserve names centrally
and document incompatible schema changes. Never derive field names,
`event.name`, severity, or logger category from untrusted or high-cardinality
values. Keep user-controlled text in sanitized values.

Use identifiers instead of copied objects. Distinguish identifier types:
request, trace, operation, job, message, and tenant identifiers are not
interchangeable. Include optional identity fields only when justified,
classified, and permitted.

## Apply severity by impact

- `TRACE`: extremely detailed flow diagnostics; optional and disabled in normal
  production.
- `DEBUG`: diagnostic state useful during targeted investigation; disabled or
  sampled in normal production.
- `INFO`: expected lifecycle transitions or material operational state.
- `WARN`: unexpected or degraded behavior that recovered, was handled, or
  needs attention.
- `ERROR`: an operation failed, its intended outcome was not achieved, and the
  failure requires caller handling or investigation.
- `FATAL`: the running process or service instance cannot continue safely.

Classify by operational impact, not by the presence of an exception. Expected
validation failures, not-found results, and safely handled conditions are not
automatically warnings or errors. `FATAL` describes impact; it does not require
terminating a serverless or externally managed runtime.

## Own exceptions and retries once

The layer that handles, translates, or terminates an operation owns its failure
event. Lower layers SHOULD return typed failures or add trace context instead
of logging and rethrowing the same failure. Emit another log only when it adds a
distinct decision or boundary transition.

Never pass arbitrary exception objects to a generic serializer. Use an
approved allowlisting serializer and record only safe, useful fields such as:

- a stable exception type or error code;
- the affected operation and safe bounded context;
- retryability, attempt number, and final outcome;
- exception message or stack trace only under an explicit data and access
  policy.

Assume messages and stack traces may contain secrets, personal data, queries,
paths, source content, or payload fragments. Sanitizing line breaks alone does
not make them safe.

For retries, avoid an indistinguishable error per attempt. Record bounded
attempt/defer events only when operationally useful, then emit one final
success, exhaustion, or abandonment event. Preserve the final actionable
failure even when intermediate events are sampled.

## Log boundaries, not payloads

For HTTP boundaries, prefer safe fields such as method, route template, status
class or code, duration, outcome, and trace/request correlation. Do not log raw
URLs, query strings, authorization headers, cookies, full header maps, or
request/response bodies by default.

For jobs and message consumers, prefer job/message type, stable operation,
attempt, outcome, duration, and safe correlation identifiers. Do not log raw
payloads, queue credentials, or unrestricted broker metadata.

For database and dependency calls, prefer dependency identity, stable
operation, duration, outcome, and an approved error code. Do not log raw query
parameters, connection strings, or complete statements containing values.

## Protect sensitive data

Classify data before collecting it. Prefer a field allowlist and minimization;
redaction is a fallback, not permission to collect arbitrary objects.

Events MUST NOT contain credentials, tokens, private keys, authentication or
authorization headers, raw cookies or session identifiers, payment
authentication data, or unrestricted request/response bodies. Treat personal,
tenant, source-code, financial, health, and location data according to
applicable policy.

Normalize or reject control characters, delimiters, and invalid encodings to
prevent log injection and parser confusion. Bound strings, arrays, object
depth, and serialized size. Test sanitization with synthetic hostile inputs.

Hashing does not automatically make data anonymous or safe. Use hashing only
when the threat model, collision properties, access model, and re-identification
risk have been reviewed.

## Correlate deliberately

Propagate existing trace context across supported boundaries. For JSON outside
an established telemetry transport, use top-level `trace_id` and `span_id` when
available so log-trace correlation remains portable.

Do not invent a new globally unique identifier at every layer. Validate
externally supplied correlation values, bound their length, and never trust
them for authorization. If a workflow crosses systems without tracing, create
one documented operation identifier at the initiating boundary and propagate
it.

## Capture security and audit events when applicable

Define separate security or audit events when the system performs relevant
actions such as:

- authentication and authorization decisions;
- privileged, administrative, or break-glass actions;
- permissions, policy, or security-sensitive configuration changes;
- credential, key, or secret lifecycle actions;
- sensitive-data access, bulk export, or destructive operations;
- suspicious input, abuse controls, or workflow-integrity failures.
- changes to logging levels, destinations, filtering, sampling, or required
  event controls.

Record a safe actor identifier, action, target type and identifier, outcome,
reason/error code, event time, and correlation context as policy permits. Do
not record credentials or sensitive target contents.

Required security and audit events MUST NOT be disabled by ordinary debug
controls. Protect them with stricter access, integrity, retention, and
monitoring appropriate to their purpose. Application logs alone do not provide
non-repudiation or prove legal compliance.

## Control volume, cardinality, and sampling

Set budgets for event rate, bytes, field size, and cardinality. Never place
unbounded values such as raw URLs, user input, timestamps, identifiers, or
exception messages in event names, metric labels, logger names, or indexed
dimensions.

Sample repetitive success, trace, and debug events consistently using stable
keys when correlation matters. Record sampling policy and, where possible,
dropped-event counts. Do not sample away the only record of an actionable
failure or required security/audit event unless an approved policy provides an
equivalent durable signal.

Prefer aggregation or metrics for high-volume counts and latency distributions.
Rate-limit repeated diagnostics while retaining evidence that suppression
occurred.

## Engineer the logging pipeline

- Use authenticated, encrypted transport where logs cross trust boundaries.
- Apply least-privilege write, read, search, export, and deletion access.
- Protect stored logs against unauthorized modification and deletion.
- Preserve event time and ingestion time; maintain reliable clock
  synchronization and surface clock uncertainty.
- Define buffering, backpressure, disk, network, quota, and collector-outage
  behavior. Logging MUST NOT block a critical path indefinitely or crash the
  application merely because a best-effort sink is unavailable.
- Detect when expected logging stops, delivery falls behind, events are
  dropped, parsing fails, or storage approaches capacity.
- Define retention, archival, deletion, legal hold, and export from data
  classification and policy. Never invent a universal retention period.

Some audit or safety-critical workflows require durable recording before an
operation succeeds. Treat that as an explicit transactional requirement, not
as ordinary best-effort application logging, and design its failure behavior
accordingly.

## Verify the implementation

Test representative success, handled failure, final failure, retry, timeout,
cancellation, and degraded-path events. Verify:

- schema, required fields, stable types, severity, and timestamps;
- trace and operation correlation across boundaries;
- one owner for each failure and no accidental duplicate emission;
- secret and sensitive-data exclusion, including exceptions and nested values;
- injection resistance, encoding, truncation, cardinality, and size bounds;
- sampling, suppression accounting, and required-event preservation;
- behavior under slow, full, unavailable, malformed, or unauthorized sinks;
- access, retention, deletion, and tamper controls at the platform layer;
- dashboards, searches, alerts, and runbooks can answer the intended question.

Use synthetic fixtures. Do not place real secrets or personal data in tests.
For reviews, lead with findings by severity and cite code or configuration
evidence. Modify the implementation only when requested.

Read [references/standards.md](references/standards.md) when validating the
baseline against authoritative guidance or explaining why a control exists.
