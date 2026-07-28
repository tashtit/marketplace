# Standards basis

Use these sources to validate or tailor the baseline. Apply newer
organization-specific policy when it is stricter.

## Authoritative guidance

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
