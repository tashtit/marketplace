---
name: logging-standards
description: Design or review secure, structured production application logging with consistent events, severity, correlation, redaction, cardinality, sampling, retention, and verification. Use when adding logs, reviewing observability, defining an event schema, or diagnosing noisy, unsafe, or unusable telemetry.
---

# Logging Standards

Make logs useful for operating software without turning them into an
unbounded, sensitive data store. Repository policy and applicable legal or data
requirements take precedence; the rules below are Tashtit defaults.

## Event contract

Emit structured events through the project's logging abstraction. Each event
SHOULD have a stable machine-readable event name, timestamp supplied by the
logging pipeline, severity, component, outcome, and relevant correlation
identifiers. Add deployment version and environment at the collector when
possible rather than repeating application configuration.

Use descriptive keys with stable types. Log facts, not prose assembled from
untrusted input. Never use dynamic values as field names or event names.

## Severity

- `DEBUG`: diagnostic detail disabled or sampled in normal production.
- `INFO`: expected lifecycle or material business/operational state.
- `WARN`: degraded or unexpected behavior that recovered or needs attention.
- `ERROR`: an operation failed and requires investigation or caller handling.
- `FATAL`: the process cannot continue safely.

Do not log the same failure at every layer. The layer that handles, translates,
or terminates the operation owns the error event.

## Context and correlation

Propagate trace and request identifiers using existing standards. Include job,
message, operation, and tenant identifiers only when needed and safe. Do not
invent globally unique correlation values at every layer or overload one field
with multiple identifier types.

## Data safety

Never log credentials, tokens, session identifiers, private keys, authorization
headers, raw cookies, payment data, or full request/response bodies by default.
Classify personal and tenant data before logging it. Prefer allowlisted fields;
redaction is a fallback, not permission to collect everything.

Sanitize control characters and prevent log injection. Error objects may contain
sensitive messages: record an approved error code and bounded safe context.

## Cost and reliability

Bound field sizes and high-cardinality values. Sample repetitive success and
debug events, but preserve security signals and actionable failures according
to policy. Logging MUST NOT block critical request paths indefinitely or cause
the application to fail when the telemetry sink is unavailable.

Define retention, access, deletion, and export controls with the owning team.
Do not claim a universal retention period.

## Implementation workflow

1. Define the operational question and event owner.
2. Reuse the existing schema, logger, trace context, and error taxonomy.
3. Specify example success, failure, retry, and degraded events with synthetic
   values.
4. Threat-model sensitive data, injection, cardinality, volume, and sink loss.
5. Add tests for schema, severity, correlation, redaction, bounds, and duplicate
   emission.
6. Verify locally with safe fixtures and document dashboards or alerts that
   consume the event.

For reviews, lead with findings by severity and cite code/config evidence. Do
not modify code unless implementation was requested.
