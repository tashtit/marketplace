# Probe Seeds — S5

Question seeds for the `mock-design-interview` skill. Each seed is raw material, **not a
script**: the interviewer generates the actual wording live from the seed plus the candidate's
repo and transcript.

## How to read a seed

| Field | Meaning |
| --- | --- |
| **Concern** | The concept being probed. **Never say this out loud.** |
| **Symptom** | The observable situation to describe to the candidate. |
| **Looking for** | What a good answer contains. Grounded in a concept file, never invented. |
| **Bar** | The level at which this is expected unprompted, per `level-expectations.md`. |
| **Follow-up if thin** | Where to push when the first answer is shallow. |

**The symptom is the question.** Describe what is observed and let the candidate name the cause.
The moment you name the concern, you have handed over the answer and the probe is spent.

---

## P1 — one request, thousands of downstream queries

- **Concern:** `fan-out-on-read-vs-write.md` — never spoken aloud
- **Symptom:** A single endpoint is timing out for a small set of accounts and fine for everyone
  else. Traces show the slow requests issuing between two and four thousand small database
  queries, each individually taking under a millisecond.
- **Looking for:** Recognition that the assembly work is proportional to how many related records
  the caller has, and that the remedy is to move the assembly to the moment the underlying data is
  written rather than the moment it is asked for [S5]. Strong answers note that 10s to 100s of
  downstream calls is ordinary but thousands is not, especially under a latency requirement [S5].
- **Bar:** Senior — S5 calls knowing approaches for handling this "essential" at senior [S5].
- **Follow-up if thin:** Ask what has to be true of the requirements for the work to be movable off
  the request path at all.

## P2 — the write that cannot finish

- **Concern:** `fan-out-on-read-vs-write.md` — never spoken aloud
- **Symptom:** A single write from one particular account has to touch a few million rows before
  it is considered done. The host handling it exhausts its connections and the request never
  completes.
- **Looking for:** That a single host cannot do this synchronously — connection limits and the
  latency budget both forbid it — and that even where it appears to work, the load across the fleet
  becomes wildly uneven, which is what makes the tier unscalable [S5]. The move is to a queue with
  a worker fleet consuming it [S5].
- **Bar:** Senior — S5 grades the direct approach "Bad" and the queued one "Good"; senior is
  expected to reach at least the good tier and discuss the deep dive in detail [S5].
- **Follow-up if thin:** Ask what the queue itself has to guarantee, and what goes into a message.

## P3 — the permission slip for background work

- **Concern:** `requirements-scoping.md` — never spoken aloud
- **Symptom:** Two engineers disagree about whether a piece of work belongs inside the request or
  behind a queue. One says the user must see the effect immediately; the other says a minute is
  fine. Nothing written down settles it.
- **Looking for:** That the tolerance is a stated requirement, quantified, and that it is the thing
  that licenses moving work off the request path [S5]. A good answer treats the number as a design
  input rather than a preference, noting that a single-digit-millisecond system needs a dramatically
  different architecture than one allowed a second [S5].
- **Bar:** Mid-level — S5 expects a candidate to have defined the requirements, and quantifying
  them is part of that [S5].
- **Follow-up if thin:** Ask what would have to change in the design if the tolerance were zero.

## P4 — the fleet that cannot be sized

- **Concern:** `fan-out-on-read-vs-write.md` — never spoken aloud
- **Symptom:** A worker pool consuming a queue has wildly variable per-message duration — most
  finish in milliseconds, a few run for many minutes. Autoscaling on queue depth keeps
  overshooting and undershooting.
- **Looking for:** Recognition that the messages represent order-of-magnitude different amounts of
  work, that one message covering a million downstream records is not comparable to one covering a
  thousand, and that such tasks may need to be broken up [S5].
- **Bar:** Senior — stated as a challenge of the "Good" solution, which senior is expected to
  discuss in detail [S5].
- **Follow-up if thin:** Ask whether every message deserves the same treatment, or whether the
  extreme ones should be handled differently.

## P5 — the 0.01% that consumes the fleet

- **Concern:** `fan-out-on-read-vs-write.md` — never spoken aloud
- **Symptom:** Ninety-nine percent of background work is cheap. A handful of accounts generate
  work so large that the whole fleet is sized for them, and the cost is dominated by cases that
  serve very few end users.
- **Looking for:** That the extreme cases can be **excluded** from the precomputation and handled
  live at read time instead, with the two results merged when the caller asks [S5]. Strong answers
  note this makes the read-vs-write choice a per-entity decision rather than a system-wide one, and
  that most entities end up with a mix of both [S5]. The stated cost is more work in the read path
  plus a threshold to tune [S5].
- **Bar:** Staff+ — S5 grades this the "Great" solution, and expects a staff candidate to cover all
  the deep dives [S5].
- **Follow-up if thin:** Ask where the exclusion decision is recorded, so the background worker can
  see it.

## P6 — the store that stops honoring its throughput number

- **Concern:** `hot-key-load-distribution.md` — never spoken aloud
- **Symptom:** A managed store is provisioned well above the measured aggregate request rate, and
  is still returning throttling errors. The dashboard shows total consumed capacity at a fraction
  of what was provisioned.
- **Looking for:** That the quoted throughput is conditional on requests being spread across the
  keyspace, and that behind the abstraction are physical machines with their own limits — so one
  key taking hundreds of requests per second while its neighbours take none is not the even load
  the number assumed [S5].
- **Bar:** Senior — S5 frames diagnosing bottlenecks iteratively as a senior expectation, and this
  is the diagnosis its third deep dive turns on [S5].
- **Follow-up if thin:** Ask what property of the data makes this fixable with a cache at all.

## P7 — the remedy that reproduces the problem

- **Concern:** `hot-key-load-distribution.md` — never spoken aloud
- **Symptom:** A cache tier was added in front of a struggling store, keyed by record id and
  spread across twelve nodes. Aggregate hit rate is excellent. Two of the twelve nodes are at
  99% CPU and the other ten are nearly idle, and the same errors are back.
- **Looking for:** That keying the cache the same way as the store hands the cache the same skew —
  the node holding several simultaneously popular records absorbs a disproportionate share while
  the rest are underutilized [S5]. The remedy is to let **every** instance serve **any** record,
  with a load balancer spreading requests, so a popular record's traffic divides across all N
  instances [S5]. Strong answers note the instances need no coordination to do this, which is what
  makes it cheap [S5].
- **Bar:** Staff+ — S5 grades this the "Great" solution [S5].
- **Follow-up if thin:** Ask what is given up by having every instance hold the same records.

## P8 — buying throughput with memory

- **Concern:** `hot-key-load-distribution.md` — never spoken aloud
- **Symptom:** A proposal replaces a partitioned cache tier with one where every node holds the
  same working set. Total memory across the tier is unchanged. A reviewer objects that this is
  strictly worse because it holds fewer distinct records.
- **Looking for:** That the objection is correct but not decisive — the tier holds fewer records
  and takes more initial misses (up to N to the store rather than 1 for a newly popular record),
  and both are accepted in exchange for N times the throughput on any single key with no added
  coordination [S5]. Strong answers note N misses is far smaller than the traffic being absorbed,
  and that the backing store can tolerate some read variability [S5].
- **Bar:** Staff+ — articulating this tradeoff is the pro/con discussion S5 expects at depth [S5].
- **Follow-up if thin:** Ask which shape they would choose if the working set were far larger than
  total memory.

## P9 — the second step with no index

- **Concern:** `point-lookup-indexing.md` — never spoken aloud
- **Symptom:** A two-step read is fast in its first step and slow in its second. The first step
  returns a few hundred identifiers quickly; the second step, which fetches the records belonging
  to those identifiers in time order, scans.
- **Looking for:** That the index was chosen for one table in isolation rather than for the join
  being performed, and that the fix is an index whose partition key is the owning entity and whose
  sort key is the ordering attribute — which returns each entity's records already ordered [S5].
- **Bar:** Mid-level — S5 expects a defined data model, and the interviewer will probe which
  indexes a named datastore offers [S5].
- **Follow-up if thin:** Ask whether adding this index makes the overall request fast, and why not.

## P10 — resuming a scroll

- **Concern:** `cursor-pagination.md` — never spoken aloud
- **Symptom:** A client scrolls through a long ordered list. The team is debating how the server
  should know where the client left off, and the current proposal passes a page number.
- **Looking for:** That because consumption follows the sort order, the position can be carried as
  a single boundary value taken from the ordering itself, and each page returns N entries beyond it
  [S5]. Strong answers note the server returns the next cursor rather than the client computing it,
  and that the cursor is optional on the first call [S5].
- **Bar:** Mid-level — S5 expects clearly defined API endpoints, and this is one of its three [S5].
- **Follow-up if thin:** Ask what has to be true of the index for the boundary value to be cheap.

## P11 — the tail nobody visits

- **Concern:** `cursor-pagination.md` — never spoken aloud
- **Symptom:** A design review stalls on a hypothetical: what if a caller pages a hundred pages
  deep? The optimized path only covers the first few hundred entries, and one reviewer wants it
  extended to cover arbitrary depth.
- **Looking for:** That the question is fair but most systems simply do not support that depth,
  because real callers do not go there [S5]. The design consequence is that the deep tail can be
  served by a slower fallback rather than by the optimized path, and that the bound on the fast
  path is a cost/benefit dial tuned against how much it affects tail callers [S5].
- **Bar:** Senior — S5 expects the tradeoffs of architectural choices to be articulated and
  justified [S5].
- **Follow-up if thin:** Ask what the fallback path actually is, if the optimized one is exhausted.

## P12 — the same relationship, asked from both ends

- **Concern:** `bidirectional-relationship-queries.md` — never spoken aloud
- **Symptom:** A directed relationship between two entities is stored with one side as the
  partition key. "Everything A points at" is instant. "Everything pointing at A" is a full scan.
- **Looking for:** That the store can maintain the reverse structure itself — a secondary index
  with the keys swapped — which covers the reverse range query without a second copy to keep in
  sync [S5]. A complete answer names all three access patterns the pair supports: the point lookup
  on both keys, and the range query in each direction [S5].
- **Bar:** Mid-level — S5 expects a defined data model, and this is the model for its second
  requirement [S5].
- **Follow-up if thin:** Ask what this costs on the write path.

## P13 — reaching for the specialist store

- **Concern:** `bidirectional-relationship-queries.md` — never spoken aloud
- **Symptom:** An engineer proposes introducing a purpose-built store for a many-to-many
  relationship, on the grounds that the data is a graph. The only queries in the requirements are
  "does A relate to B" and "list everything related to A".
- **Looking for:** That being graph-shaped is not the criterion — traversals that step between
  nodes are, such as reaching two hops out or building an embedding for recommendations [S5]. With
  only one-hop queries, a plain key-value store models the relationship directly, and choosing the
  specialist store invites its own scaling problem for no traversal benefit [S5].
- **Bar:** Senior — S5 expects architectural choices justified with pros and cons [S5].
- **Follow-up if thin:** Ask what query would change their answer.

## P14 — where per-pair policy lives

- **Concern:** `entity-granularity.md` — never spoken aloud
- **Symptom:** A background job needs to treat certain pairings differently from others. The
  attribute is not a property of either participant on its own — it is true only of that specific
  pairing — and there is currently nowhere to put it.
- **Looking for:** That the link between two records deserves to be an explicit entity rather than
  an attribute on either side, particularly when the relationship is directed and so has a distinct
  meaning each way [S5]. The link row is then the natural home for state that applies to one
  pairing [S5].
- **Bar:** Mid-level — part of the data model S5 expects to be clearly defined [S5].
- **Follow-up if thin:** Ask how much detail this modeling step warrants at this stage.

## P15 — two workloads in one service

- **Concern:** `service-and-data-boundaries.md` — never spoken aloud
- **Symptom:** One service handles both a write path with simple key-based inserts and a read path
  that gathers and merges across many records. They scale together, deploy together, and their
  performance profiles have nothing in common.
- **Looking for:** That the read side is not merely higher-volume but has **very different query
  patterns**, and that divergent query shape is itself a reason to separate, distinct from volume
  [S5]. Volume argues for more instances; a different query shape argues for a different service.
- **Bar:** Senior — S5 expects the maintainability and scalability impact of such choices to be
  articulated [S5].
- **Follow-up if thin:** Ask what makes the write side trivially scalable by comparison.

## P16 — the tier that scales by addition

- **Concern:** `read-heavy-workloads.md` — never spoken aloud
- **Symptom:** One service tier absorbs traffic growth by adding hosts with no coordination
  changes. A neighbouring tier cannot, and nobody can articulate the difference.
- **Looking for:** That the easily scaled tier holds no per-request state — in S5's case because
  its hosts only write to the database — and that this is what makes capacity a matter of adding
  hosts behind a load balancer [S5].
- **Bar:** Mid-level — expect the interviewer to probe what each named component does and how, and
  this is that probe for the entry point [S5].
- **Follow-up if thin:** Ask what would break if a host kept something in local memory between
  requests.

## P17 — sizing a structure before adopting it

- **Concern:** `capacity-estimation.md` — never spoken aloud
- **Symptom:** A proposal adds a derived structure holding a few hundred identifiers per user,
  across a user base in the billions. Nobody has worked out what it costs to store, and the review
  is proceeding on the assumption that it is fine.
- **Looking for:** The arithmetic done before the structure is accepted rather than after: bytes
  per identifier × identifiers per record × record count, producing a total to judge against
  ordinary hardware [S5]. Strong answers keep the entries compact deliberately, holding identifiers
  rather than full records, precisely to keep this number small [S5].
- **Bar:** Senior — S5 places this gut-check inside the deep dive it expects to be discussed in
  detail [S5].
- **Follow-up if thin:** Ask whether terabytes is the right unit for deciding this is reasonable.

## P18 — is this cost reasonable

- **Concern:** `capacity-estimation.md` — never spoken aloud
- **Symptom:** A storage total is agreed and correct. The room still cannot decide whether it is
  acceptable, and the discussion cycles between "that's a lot" and "that's nothing".
- **Looking for:** Converting the total into a **per-unit cost in currency** and comparing it
  against per-unit revenue — what one user, tenant, or item costs per month against what it earns
  [S5]. The comparison is what answers the question; the total alone cannot.
- **Bar:** Staff+ — S5 attaches this to weighing cost among scalability, reliability and
  maintenance, which it places at staff level [S5].
- **Follow-up if thin:** Ask what number they would need from the business to complete the
  comparison.

## P19 — a long TTL, deliberately

- **Concern:** `caching-the-read-path.md` — never spoken aloud
- **Symptom:** A team sets a uniform 60-second expiry on every cache entry as a house rule. One
  dataset in the cache is written once and essentially never modified, and its hit rate is poor.
- **Looking for:** That the expiry should track how often the item is actually written — rarely
  edited records support a long lifetime with least-recently-used eviction, with a specific entry
  invalidated only when that record is edited, not when one is created [S5]. Strong answers can
  size the tier: N hosts × M memory, sufficient if it holds the popular working set [S5].
- **Bar:** Mid-level — S5 grades this caching approach as one of its "Good" solutions and says a
  mid-level candidate may have some of the "Good" solutions, without being expected to cover every
  scaling edge case in the deep dives [S5].
- **Follow-up if thin:** Ask what this cache does *not* fix about the load pattern underneath it.

## P20 — the naive version, on purpose

- **Concern:** `requirements-scoping.md` — never spoken aloud
- **Symptom:** A candidate is forty minutes into a design and has one component modeled in
  extraordinary depth. Two of the four stated requirements have not been touched at all.
- **Looking for:** That covering the breadth of the requirements before going deep is the
  discipline, and getting lost in one scaling problem before having a mostly complete design is a
  named failure mode [S5]. Strong answers describe building the inadequate version deliberately and
  saying out loud that it will not scale and will be fixed separately [S5], and deferring detail
  with an explicit "I'll come back to this if there's time" rather than silently skipping it [S5].
- **Bar:** Mid-level — S5 expects a functional high-level design covering the requirements, and
  drives the early stages onto the candidate [S5].
- **Follow-up if thin:** Ask what signal an interviewer takes from where a candidate spends time.

## P21 — changing the product instead of the system

- **Concern:** `requirements-scoping.md` — never spoken aloud
- **Symptom:** A requirement states that one dimension is unbounded. Every architecture that
  honors it is expensive, and the expense is entirely driven by a few hundred accounts at the
  extreme.
- **Looking for:** Asking whether the **product** can move rather than the system — capping the
  dimension, or giving the extreme cases a deliberately different experience, which S5 notes
  production systems commonly do [S5]. Strong answers justify it by user impact: the extreme-case
  user is unlikely to notice a couple of minutes of delay [S5].
- **Bar:** Staff+ — S5 places anticipating problems and proposing preemptive solutions
  independently at this level [S5].
- **Follow-up if thin:** Ask who they would need agreement from before assuming the cap.

## Coverage note

Concerns S5 does **not** establish a bar for. Do not probe or score these from this source:

- **Authentication and session handling.** S5 explicitly assumes the caller is already
  authenticated and their identity available, and declines to detail it [S5].
- **Privacy and visibility rules.** Declared out of scope [S5].
- **Interactions on a record** — reactions, replies. Declared out of scope [S5].
- **Removing a relationship.** S5 mentions the verb in passing and marks it out of scope [S5].
- **Ranking or relevance.** S5's ordering is purely reverse chronological by requirement; it makes
  no claim about scoring or ordering by anything else [S5].
- **Content structure.** S5 deliberately leaves the internal shape of its main record undefined,
  so there is nothing to grade [S5].
- **Observability, rate limiting, disaster recovery, idempotency beyond the one endpoint.** Not
  discussed [S5].

Two scoping rules specific to this source:

- **P18 is a staff+ probe only because of where S5 files the cost reasoning.** S5 gives the
  per-unit-cost rule of thumb as an aside rather than as a graded expectation; if the candidate has
  no revenue figure available to compare against, the probe has no answer and must not be scored.
- **Do not import S3's or S4's calibration of solution tiers.** S5 sets its own: at mid-level the
  candidate *may* have some of the "Good" solutions and is not expected to cover every scaling edge
  case [S5]. That is neither S4's tolerance of a "Bad" solution nor S3's requirement of at least the
  "Good" one. Grade against S5's wording when running this file.

## Sources

- **[S5]** Hello Interview — Design Facebook's News Feed —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/fb-news-feed>
