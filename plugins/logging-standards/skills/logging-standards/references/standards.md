# Standards basis

Use these sources to validate or tailor the baseline. Apply newer
organization-specific policy when it is stricter.

## Authoritative guidance

- OpenTelemetry's log data model and event conventions describe the record
  fields, stable event names, structured attributes, and display messages.
  [Logs Data Model](https://opentelemetry.io/docs/specs/otel/logs/data-model/)
  and [Event conventions](https://opentelemetry.io/docs/specs/semconv/general/events/).
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html):
  application and security event selection, data exclusion, injection
  protection, verification, secure transport, access control, and tamper
  protection.
- [OpenTelemetry log and trace context compatibility](https://opentelemetry.io/docs/specs/otel/compatibility/logging_trace_context/):
  portable `trace_id`, `span_id`, and trace flags for non-OTLP log formats.
- [OpenTelemetry exception semantic conventions](https://opentelemetry.io/docs/specs/semconv/exceptions/exceptions-logs/):
  exception event attributes, span association, severity by impact, and the
  sensitivity risk of exception messages.
- [NIST SP 800-92, Guide to Computer Security Log Management](https://csrc.nist.gov/pubs/sp/800/92/final):
  enterprise log-management lifecycle covering generation, transmission,
  storage, analysis, and disposal.

## Baseline conventions

The sources do not prescribe one universal application schema, severity policy,
retention period, vendor, or library. This skill therefore defines a small
portable event contract and decision rules while requiring each organization
to map them to its approved schema, classification, retention, and access
policies.

Do not infer certification or compliance from adopting the baseline. Verify
the implementation, operational controls, and applicable requirements in the
target environment.

## Map to OpenTelemetry when already in use

| Portable field | OpenTelemetry log record |
| --- | --- |
| `timestamp` | `Timestamp`. Use `ObservedTimestamp` separately for collection time. |
| `severity` | Map by impact to `SeverityNumber`. `SeverityText` can preserve the source level label. |
| `event.name` | `EventName`. Use the native field when the transport supports it. |
| `message` | Optional display text in `Body`. |
| `trace_id` / `span_id` | `TraceId` / `SpanId`. Carry existing `TraceFlags` when available. |
| `service.name` | Resource attribute `service.name`. |
| `attributes` and event-specific fields | `Attributes`. Reuse applicable semantic conventions and map only approved data. |

For example, use `http.route` for a route template and `exception.type` for an
approved exception class. Apply the same data policy to the message, stack
trace, and all other attributes when mapping.

## Examples

These fragments show the fields relevant to each decision. Include the usual
record metadata and approved correlation context when emitting the full event.

| Situation | Avoid | Prefer |
| --- | --- | --- |
| Successful import | `INFO` messages like `Done` or one progress line per item. | `INFO` `inventory.import.completed`, message `Inventory import completed`, `outcome=success`, and `items_imported=120` as a number. |
| Terminal storage exception | Serialize the whole exception with its message, stack, and nested causes. | At the job boundary, emit `ERROR` `inventory.import.failed` with `Inventory import failed` and the allowlisted attribute `error_code=storage_timeout`. |
| Retry after a timeout | Log the same `ERROR` in the storage client, on each attempt, and again at exhaustion. | For a delay that degrades service, emit `WARN` `inventory.import.retry_scheduled` with a numeric `attempt`. On exhaustion, emit one `ERROR` at the job boundary. |
| Filterable context | Put the job ID into the event name or write `Imported 120 items in 850 ms`. | Keep `inventory.import.completed` and the summary stable. Carry numeric `duration_ms` and `items_imported` as attributes. Include the approved `job_id` only when needed for correlation. |
| Expected lookup miss | Emit `ERROR` for a missing optional inventory record. | Omit the event if it answers no operational question. Use `DEBUG` for useful lookup diagnostics. |
