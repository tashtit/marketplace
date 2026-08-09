# API lifecycle and deprecation reference

Versioning schemes, header set, and phase transitions for the lifecycle
contract in `SKILL.md`. Dates, version counts, and windows are examples; set
them from the real consumer contract.

## Versioning schemes

Pick one and keep it across the whole API.

URI path — most visible, easy to route and cache:

```http
GET /api/v1/reports
GET /api/v2/reports
```

Media type / content negotiation — one URL, versioned representation:

```http
GET /api/reports
Accept: application/vnd.example.v2+json
```

- Bump the major version only for a breaking change (removed/renamed field,
  tightened validation, changed type or meaning).
- Additive, backward-compatible changes do not get a new version.
- Shipping `/v2` and deprecating `/v1` are one event: publish the new version,
  then start the old version's deprecation clock with a `Link` to the migration
  guide.

## Two phases

- **Deprecation period** — the endpoint is marked deprecated but keeps working.
  Clients migrate during this window.
- **Sunset date** — the hard removal point. After it, the endpoint no longer
  serves its function.

Do not conflate the two: "deprecated" is a warning, "sunset" is removal.

## Deprecated response

While deprecated, the endpoint keeps returning its normal `2xx` response plus
signals:

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Wed, 31 Mar 2027 23:59:59 GMT
Link: <https://docs.example/api/v2/migration>; rel="successor-version"
```

- `Deprecation` (RFC 8594) marks the endpoint deprecated.
- `Sunset` (RFC 8594) carries the removal date once one is set.
- `Link` with `rel="successor-version"` or `rel="deprecation"` points to
  migration or successor docs.
- The API specification marks the operation `deprecated: true`.

```yaml
paths:
  /api/v1/reports:
    get:
      deprecated: true
      summary: List reports (deprecated; use /api/v2/reports)
```

## After sunset

```http
HTTP/1.1 410 Gone
Link: <https://docs.example/api/v2/migration>; rel="successor-version"
```

- Return `410 Gone`, not a bare `404`, so late clients learn the endpoint was
  intentionally removed.
- Keep returning the successor `Link` so the signal stays actionable.

## Version and window policy

- Limit how many versions run concurrently. Internal callers you control
  tolerate tighter limits and shorter windows than external consumers.
- State the chosen limits and window explicitly per API. Do not copy a fixed
  number as if it were universal, and never shorten an external contract
  without agreement.
- Prefer measuring real traffic to an endpoint before sunsetting it over
  assuming it is unused.

## Communication

- In-band headers are necessary but not sufficient. Announce deprecation in the
  channels consumers watch: changelog, release notes, migration guide.
- A migration guide states what replaces the endpoint and how to move.

## References

- RFC 8594 — The Sunset HTTP Header Field.
  <https://www.rfc-editor.org/rfc/rfc8594>
- RFC 9457 — Problem Details for HTTP APIs.
  <https://www.rfc-editor.org/rfc/rfc9457>
- OpenAPI Specification (`deprecated` flag).
  <https://spec.openapis.org/oas/latest.html>
