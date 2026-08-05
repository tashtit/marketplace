# Human review checklist

- [ ] The response first inspects the existing spec, base path, error format,
      and versioning before adding machinery.
- [ ] Work that fits a normal timeout stays synchronous; async is justified.
- [ ] Kickoff uses a state-changing method and returns 202 with a discoverable
      job resource location.
- [ ] The job status resource has an explicit state set, progress when
      knowable, timestamps, a result link, and a structured error.
- [ ] Polling is bounded (429 + Retry-After or advertised interval) and status
      reads do not mutate the job.
- [ ] Cancellation is an explicit idempotent action, not a delete, with honest
      guarantees.
- [ ] Callbacks and webhooks authenticate callers, verify payloads, retry with
      backoff, and tolerate duplicate delivery.
- [ ] A single versioning scheme (URI path or media type) is chosen, justified,
      and applied consistently; schemes are not mixed.
- [ ] Major version bumps are reserved for breaking changes; additive changes do
      not bump.
- [ ] Deprecation and sunset phases are distinguished; deprecated endpoints keep
      working with Deprecation, Sunset, and successor Link headers and a spec
      flag.
- [ ] Sunset endpoints return 410 Gone with the successor Link, not a bare 404.
- [ ] Version counts and windows are stated per API, not invented as universal,
      and external contracts are not shortened unilaterally.
- [ ] Out-of-band notice and usage monitoring accompany in-band signals.
- [ ] One versioning scheme and one error format are used consistently.
- [ ] No secret rides in a URL, identifier, or status payload.
- [ ] No vendor, framework, gateway, or compliance guarantee is invented.
- [ ] Output is materially equivalent on each claimed platform.

After reviewing a scenario on a platform, record the outcome in
`acceptance.json` beside this file. Results are pinned to the plugin version,
so a version bump requires a fresh review.
