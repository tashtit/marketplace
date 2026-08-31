# System Design Concerns

Reference data, not a skill. A library of engineering concepts where **every claim is cited to a
source that stated it**. Files are written by the `extract-design-concepts` skill, one source at a
time, and read by `mock-design-interview` while it runs. Both ship in the `interview-kit` plugin
alongside this directory.

Nothing here is an instruction to an agent. There is no frontmatter and no trigger surface, on
purpose: this directory is deliberately not a skill so that it cannot be selected, only opened by
a consumer that already has a reason to.

## What this library is and is not

**Is:** an attributable record of engineering reasoning drawn from specific documents. If a
claim is here, a source said it, and the citation tells you which.

**Is not:** a complete treatment of system design. Coverage is exactly as broad as the sources
processed so far — no broader. Each concept file has a `## Not covered by sources` section
naming its own gaps; those gaps are real and are the honest edge of the library, not an
oversight to be filled from general knowledge.

**Consequence for use:** absence of a concern here does not mean the concern doesn't apply to
your system. It means no processed source discussed it. Treat this as a checklist of
*verified* reasoning, not an exhaustive one.

## When not to open this library

**Never while building the implementation an interview would later assess.** The concerns
recorded here, together with `probes/` and `level-expectations.md`, are what that implementation is
later interviewed and graded against. Work built while consulting them scores well on concerns it
was handed, which measures the library rather than the person, and the assessment is then
worthless. This is why `interview-kit` is meant to be enabled only once the building is done.

Legitimate reads are: an interview in progress, an extraction run, or a direct question from the
user about what this library says. When answering such a question, carry the citations — the point
of the library is that a reader can tell which claims are verified, and a claim stripped of its
tag is indistinguishable from general knowledge. Note also that a concept file existing is never a
reason to recommend infrastructure; several sources make the opposite point, that at low volume
the simple thing is correct.

## Concept index

<!-- Maintained by extract-design-concepts. One line per file; no entry without a file. -->

| Concept | Consider it when | Sources |
| --------- | ------------------ | --------- |
| [requirements-scoping](concepts/requirements-scoping.md) | Starting a design; deciding what's out of scope; naming where the emphasis lies; turning "should be fast" into a benchmark; ranking consistency against availability — per operation, not per system | S1, S2, S3, S4, S5 |
| [capacity-estimation](concepts/capacity-estimation.md) | A scale target is stated and a storage, infrastructure, or transfer-time choice follows from it; a needed figure has to be derived from the one you were given | S1, S2, S4, S5 |
| [read-heavy-workloads](concepts/read-heavy-workloads.md) | Reads outnumber writes by orders of magnitude; sizing peak load; splitting read and write paths; scaling a service horizontally | S1, S3, S4, S5 |
| [caching-the-read-path](concepts/caching-the-read-path.md) | Read volume exceeds what disk can serve; data is mostly static after creation; distant users see single-region latency; choosing what to cache and for how long | S1, S2, S3, S4, S5 |
| [point-lookup-indexing](concepts/point-lookup-indexing.md) | The dominant query is "find the one row matching this key" over a large table; weighing the write cost of an index | S1, S3, S5 |
| [unique-identifier-generation](concepts/unique-identifier-generation.md) | Minting short identifiers users will see and share; collisions would break correctness | S1, S2 |
| [content-addressed-identity](concepts/content-addressed-identity.md) | You need to recognize identical content across uploads — for dedup or to resume a transfer | S2 |
| [shared-counter-coordination](concepts/shared-counter-coordination.md) | Correctness depends on one shared counter and the service is being scaled horizontally | S1 |
| [record-expiry](concepts/record-expiry.md) | Records carry an expiration time, especially when they are also cached, or when a cleanup job would otherwise be load-bearing | S1, S3 |
| [client-cached-responses](concepts/client-cached-responses.md) | Choosing response semantics that let clients cache; the mapping may later change | S1 |
| [redundancy-for-availability](concepts/redundancy-for-availability.md) | An availability target is stated and a single stateful dependency is on the critical path | S1, S2 |
| [large-file-transfer](concepts/large-file-transfer.md) | A payload could exceed a request timeout or size limit; progress or resumption is required | S2 |
| [bypassing-the-application-server](concepts/bypassing-the-application-server.md) | Bulk data passes through your server on its way to or from a storage service | S2 |
| [client-authority-and-verification](concepts/client-authority-and-verification.md) | Server state mirrors work the client performed out of the server's sight | S2 |
| [propagating-changes-to-clients](concepts/propagating-changes-to-clients.md) | The same state lives on multiple clients and must converge after a change | S2, S3 |
| [bidirectional-relationship-queries](concepts/bidirectional-relationship-queries.md) | A many-to-many relationship is embedded on one side and queried from the other | S2, S5 |
| [signed-url-access-control](concepts/signed-url-access-control.md) | Clients fetch directly from storage or a CDN, so your server can't check permissions at fetch time | S2 |
| [compression-tradeoffs](concepts/compression-tradeoffs.md) | Deciding whether to compress before transferring, and in what order with encryption | S2 |
| [preventing-double-allocation](concepts/preventing-double-allocation.md) | Finite inventory is claimed by one user at a time; a claim must be held then released, or covers several items at once | S3, S4 |
| [admission-control](concepts/admission-control.md) | Demand for a contended resource so far exceeds supply that a faster interface stops helping | S3 |
| [full-text-search](concepts/full-text-search.md) | Users search free text by keyword and a wildcard query would scan the table | S3 |
| [delegating-external-operations](concepts/delegating-external-operations.md) | A third party performs an operation and reports the outcome by callback, handles data you should never store, or computes an answer synchronously on your read path | S3, S4 |
| [service-and-data-boundaries](concepts/service-and-data-boundaries.md) | Deciding whether separate services get separate databases | S3, S4, S5 |
| [entity-granularity](concepts/entity-granularity.md) | A concern could be its own entity or attributes on an existing one; the abstract type and the physical instance are being conflated | S3, S4, S5 |
| [aggregating-availability-across-locations](concepts/aggregating-availability-across-locations.md) | A resource is spread across places and each caller can only reach some of them, so no stored total is correct | S4 |
| [proximity-candidate-filtering](concepts/proximity-candidate-filtering.md) | Deciding what is "near enough" needs an expensive predicate — travel time, not distance — evaluated per candidate | S4 |
| [partitioning-by-query-locality](concepts/partitioning-by-query-locality.md) | Every read is already scoped to a narrow slice of the keyspace, and one instance is under read pressure | S4 |
| [fan-out-on-read-vs-write](concepts/fan-out-on-read-vs-write.md) | One request must gather data from many other records, or one write must update many; deciding whether to assemble at read time or precompute at write time | S5 |
| [hot-key-load-distribution](concepts/hot-key-load-distribution.md) | A store or cache scales on aggregate throughput but the load is concentrated on a few keys | S5 |
| [cursor-pagination](concepts/cursor-pagination.md) | A client walks a long ordered result a page at a time, and the position has to be carried between calls | S5 |

## Support files

- `level-expectations.md` — what interviewers expect at mid / senior / staff+, with the
  prompted-vs-unprompted axis that distinguishes them.
- `probes/` — question seeds per source and problem class, used by `mock-design-interview`.
  Symptom-first, so a probe never names the concern it is testing.
- `rubric.md` — generic 0–5 scale for evaluating whether a concern was handled, with an evidence
  hierarchy that rejects "the dependency exists, therefore it's implemented."

## Who consumes this library

| Skill | Uses | For |
| --- | --- | --- |
| `extract-design-concepts` | writes all of it | growing the library from a new source |
| `mock-design-interview` | `probes/`, `level-expectations.md`, `concepts/` | interviewing you about something you built |

## Growing the library

New claims go to a **versioned checkout**, never to the bundled copy inside an installed plugin:
that directory is managed by the host and has no history, so a reinstall or upgrade discards
whatever was written there. `scripts/library-path.sh write` resolves a safe target and fails
closed when there is none.

Run the `extract-design-concepts` skill with a new source. It will create new concept files or
extend existing ones with additional citations, record contradictions between sources rather
than resolving them, and update this index.

Do not hand-author concept files here. Content that arrives without a citation defeats the
purpose of the library, because a reader can no longer tell which claims are verified.

## Sources processed

<!-- Append one row per source run through extract-design-concepts. -->

| Tag | Source | Date | Concepts touched |
| ----- | -------- | ------ | ------------------ |
| S1 | [Hello Interview — Design Bit.ly](https://www.hellointerview.com/learn/system-design/problem-breakdowns/bitly) | 2026-08 | all 10 concepts (created); level bars; 12 probe seeds |
| S2 | [Hello Interview — Design a File Storage Service Like Dropbox](https://www.hellointerview.com/learn/system-design/problem-breakdowns/dropbox) | 2026-08 | 8 created, 5 extended; level bars; 13 probe seeds |
| S3 | [Hello Interview — Design Ticketmaster](https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster) | 2026-08 | 6 created, 6 extended; level bars; 21 probe seeds |
| S4 | [Hello Interview — Design a Local Delivery Service like Gopuff](https://www.hellointerview.com/learn/system-design/problem-breakdowns/gopuff) | 2026-08 | 3 created, 8 extended; level bars; 21 probe seeds |
| S5 | [Hello Interview — Design Facebook's News Feed](https://www.hellointerview.com/learn/system-design/problem-breakdowns/fb-news-feed) | 2026-08 | 3 created, 8 extended; level bars; 21 probe seeds |

### Rejected from S1

Concepts named by the source but without transferable reasoning attached, so no file was
created:

- **Consistency** — stated only as a ranking ("availability > consistency"); no reasoning about
  what that implies. Recorded as a gap in `redundancy-for-availability.md`.
- **Analytics / click tracking, authentication, spam and malicious-content filtering** — declared
  out of scope by the source.
- **Observability, rate limiting, idempotency, asynchronous processing** — not discussed.

### Rejected from S2

- **Blob storage internals** — explicitly declared out of scope by the source, which suggests it
  as separate reading.
- **Database selection** — the source names a document store and immediately says a relational
  one would work as well and not to dwell on it. The transferable part (the workload doesn't
  discriminate) was folded into `capacity-estimation.md` rather than given its own file.
- **Authentication and token placement** — the source states the convention (credentials in
  headers, never the body, because the body is client-manipulable) but treats users as already
  authenticated and develops nothing further. One sentence, no surrounding reasoning.
- **Encryption in transit and at rest** — named as no-brainers with no tradeoff attached; kept as
  context inside `signed-url-access-control.md` rather than as a concept.
- **File editing, in-place viewing, storage limits per user, versioning, virus and malware
  scanning** — declared out of scope by the source.
- **Load balancers, API gateways, SSL termination** — listed as components in the final design
  with no reasoning about when or why.
- **Observability, rate limiting, idempotency** — not discussed.

### Rejected from S3

- **Payment processing as a named service** — the source routes payment through a specific
  provider but gives no reasoning for choosing it. The transferable parts (client-side
  tokenization, idempotent callbacks) went into `delegating-external-operations.md` instead.
- **The specific database engine** — the source names one but says any engine with ACID
  properties is fine, so the engine choice carries no reasoning. The parts that do — the
  transactional requirement, and needing isolation levels plus row locking or optimistic
  concurrency control — went into `preventing-double-allocation.md` and
  `service-and-data-boundaries.md`.
- **API gateway, load balancers** — the load-balancing algorithms came with a reason and went into
  `read-heavy-workloads.md`; the gateway itself appears only as a box in the design.
- **Sharding and replication** — named in the senior-level bar as expected knowledge, but the
  source never explains either. Recorded as a bar in `level-expectations.md` with no concept file,
  since there is nothing cited to check an answer against.
- **GDPR, fault tolerance, secure transactions, CI/CD, backups** — declared out of scope by the
  source in its requirements phase.
- **Viewing booked events, admin event creation, dynamic pricing** — declared out of scope as
  functional requirements.
- **Diagramming and interview communication advice** — interview meta-advice, not engineering
  reasoning.
- **Observability, rate limiting, multi-region deployment** — not discussed.

### Rejected from S4

- **Load balancing** — named in the staff+ expectations as a topic to understand, with no reasoning
  attached. The reasoning-bearing statelessness argument already lives in
  `read-heavy-workloads.md` from S3.
- **Search index over the catalog** — mentioned as something the source would ideally add, with no
  reasoning about how or when. The transferable part (divergent consumers and workloads justify the
  split) went into `service-and-data-boundaries.md` instead.
- **Database selection** — the source names a relational engine for its transaction and a key-value
  store for the rejected split-store option, but the criterion it states is only "an ACID store when
  atomicity is required", which was folded into `preventing-double-allocation.md`.
- **Payment and purchase handling, driver routing and deliveries, catalog and search APIs,
  cancellations and returns** — declared out of scope by the source.
- **Privacy and security, disaster recovery** — declared out of scope by the source.
- **Observability, rate limiting, idempotency, asynchronous processing** — not discussed.

### Rejected from S5

- **API gateway and load balancer** — named as the entry point with a reason for horizontal scaling
  attached, but that reason is statelessness, which already has a home. The transferable claim went
  into `read-heavy-workloads.md`; the gateway itself appears only as a box.
- **Database selection** — the source picks a specific key-value store for "simplicity and
  scalability" and notes it allows high provisioned throughput. The only reasoning-bearing part is
  the condition on that throughput (even load across the keyspace), which went into
  `hot-key-load-distribution.md`. The choice itself is a name-drop.
- **Single-table versus multi-table modeling** — the source notes the platform's recommended
  practice and says it deliberately used separate tables for clarity, but explains neither practice.
  The transferable habit (labelling a simplification as one) went into
  `service-and-data-boundaries.md`.
- **Idempotency** — stated as the reason for choosing one HTTP verb over another for a binary
  action, which is a real criterion, but it is one sentence with no reasoning about retries,
  duplicate delivery, or failure. Not enough to support a file; recorded here rather than rounded
  up.
- **Queue technology selection** — a specific managed queue is named, but the reasoning-bearing part
  is the requirements it must meet (at-least-once delivery, high scalability), which went into
  `fan-out-on-read-vs-write.md`. The product name carries nothing.
- **Reactions and replies on a record, visibility and privacy rules, removing a relationship** —
  declared out of scope by the source.
- **Authentication** — the source explicitly assumes it is already handled and declines to detail
  it.
- **Ranking and relevance** — the source's ordering is reverse chronological by requirement; it
  makes no claim about scoring.
- **Observability, rate limiting, multi-region deployment, disaster recovery** — not discussed.
