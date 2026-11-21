# Human review checklist

- [ ] The response first identifies the operational, security, or audit question.
- [ ] Events reuse stable names and consistent domain terms, with bounded,
      typed fields and consistent units.
- [ ] Optional messages state what happened, and investigators can filter by
      safe structured fields without parsing the message.
- [ ] Business or operational transitions are visible without routine execution
      noise.
- [ ] The existing logger and telemetry schema are reused. Local formatting
      preserves the structured event contract and data controls.
- [ ] Severity reflects impact; expected conditions are not inflated.
- [ ] One layer owns each failure, including retry exhaustion.
- [ ] Exceptions use safe allowlisted serialization rather than raw objects.
- [ ] HTTP, job, message, and dependency boundaries exclude raw payloads.
- [ ] Trace and operation identifiers are propagated, bounded, and not used for
      authorization.
- [ ] Security/audit events are considered when the requested system needs them.
- [ ] Sensitive data is minimized; secrets, injection, and nested values are tested.
- [ ] Cardinality, sampling, suppression, volume, and cost are bounded.
- [ ] Transport, access, tamper protection, clock, capacity, retention, and sink
      failure are addressed at the appropriate layer.
- [ ] Verification covers both emitted events and their actual consumers.
- [ ] No vendor, language, library, compliance, or universal-retention claim is
      invented.
- [ ] Output is materially equivalent on each claimed platform.

After reviewing a scenario on a platform, record the outcome in
`acceptance.json` beside this file. Results are pinned to the plugin version,
so a version bump requires a fresh review.
