# Probe Seeds — S4

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

## P1 — the requirement nobody can test

- **Concern:** `requirements-scoping.md` — never spoken aloud
- **Symptom:** The spec says responses "should be fast." Two engineers have built to it and
  disagree about whether the current 400ms is acceptable.
- **Looking for:** Non-functional requirements expressed as testable benchmarks rather than
  adjectives, and ideally a number derived from a downstream consumer's need rather than chosen for
  feel [S4].
- **Bar:** Mid-level — a clearly defined API and data model is the stated mid-level deliverable
  [S4].
- **Follow-up if thin:** Ask where their number came from. S4's bound exists so the result can back
  a search experience — push for what would *justify* the figure they pick [S4].

## P2 — everything is in scope

- **Concern:** `requirements-scoping.md` — never spoken aloud
- **Symptom:** Their design covers payments, driver routing, catalog search, returns, and
  availability. Three weeks in, availability is the only part that works.
- **Looking for:** Naming exclusions explicitly, and beyond that naming where the *emphasis* lies —
  a scope list says what is in, not what is central [S4].
- **Bar:** Mid-level [S4].
- **Follow-up if thin:** Ask which single concern the design is really about, and what would change
  if it were the catalog instead [S4].

## P3 — the same catalog number is wrong for everyone

- **Concern:** `aggregating-availability-across-locations.md` — never spoken aloud
- **Symptom:** A stored "quantity on hand" column is correct for users in one city and wrong for
  every other city.
- **Looking for:** The reachable subset differs per caller, so the answer is a union computed per
  request, not a stored total [S4].
- **Bar:** Mid-level — both routes functional is the stated bar [S4].
- **Follow-up if thin:** Ask what the number even means when the resource is spread across sites the
  caller cannot all reach [S4].

## P4 — the catalog row and the thing on the shelf

- **Concern:** `entity-granularity.md` — never spoken aloud
- **Symptom:** One table holds both "the product customers browse" and "the box sitting in
  building 12," and every query has to guess which one it means.
- **Looking for:** Separating the type from the physical instance — the caller cares about the type;
  the system must track where instances are; the quantity is derived by summing instances and
  belongs to neither entity [S4].
- **Bar:** Mid-level — the data model is explicitly in the mid-level bar [S4].
- **Follow-up if thin:** Ask how they would find the entities they are missing. S4's heuristic:
  start from the most concrete physical nouns and work up to the abstract ones [S4].

## P5 — the full scan that did not need to happen

- **Concern:** `aggregating-availability-across-locations.md` — never spoken aloud
- **Symptom:** Answering "what can I get?" examines every physical instance in the system, then
  discards 99% of them.
- **Looking for:** Resolving the location dimension first because it is the selective one, then
  querying only instances at those locations — every instance lives somewhere, so the location step
  is the shortcut [S4].
- **Bar:** Mid-level [S4].
- **Follow-up if thin:** Ask which of the two steps their latency budget is actually spent in [S4].

## P6 — close on the map, an hour away by road

- **Concern:** `proximity-candidate-filtering.md` — never spoken aloud
- **Symptom:** A site 8 miles away across a river is offered for one-hour delivery; a site 20 miles
  down a highway is not.
- **Looking for:** Recognizing that geometric distance is a proxy that fails where geography and
  roads diverge, and that a requirement stated in drive time is not measured by distance [S4].
- **Bar:** Senior — the deep dives are where the senior bar is set, having sped through the
  high-level design [S4].
- **Follow-up if thin:** Ask whether a better distance formula fixes it. Haversine improves on
  Euclidean by accounting for the Earth's curvature but still does not measure travel time [S4].

## P7 — the estimator's bill

- **Concern:** `proximity-candidate-filtering.md` — never spoken aloud
- **Symptom:** Correctness is fine, but every request makes 10,000 calls to an external travel-time
  service, and almost all of them return "far too slow."
- **Looking for:** Pruning with a cheap predicate first and scoring only survivors — and crucially,
  choosing the prune threshold as the *optimistic bound* on the expensive predicate, so it can only
  remove certain negatives [S4].
- **Bar:** Senior [S4].
- **Follow-up if thin:** Ask what happens if the radius is picked for convenience instead of as a
  bound — the prune silently drops valid results [S4].

## P8 — asking a database for buildings

- **Concern:** `proximity-candidate-filtering.md` — never spoken aloud
- **Symptom:** Every single request queries a table whose contents changed twice last year.
- **Looking for:** A slow-changing dimension on a hot path can be synced into service memory
  periodically, with the refresh interval set by how fast the data actually changes [S4].
- **Bar:** Senior [S4].
- **Follow-up if thin:** Ask what staleness window they would accept and why that number [S4].

## P9 — the traffic number nobody gave them

- **Concern:** `read-heavy-workloads.md` — never spoken aloud
- **Symptom:** The only figure in the requirements is a daily order count. They say they cannot size
  the read path because nobody told them the read volume.
- **Looking for:** Deriving the missing figure from the given one via stated assumptions —
  pages-per-visit multiplies it up, and dividing by a conversion rate scales the claim count back to
  the population that produced it [S4].
- **Bar:** Senior — read volume is one of the two things S4 says should "jump out to experienced
  engineers" [S4].
- **Follow-up if thin:** Ask them to state their assumptions out loud. The value of the estimate is
  that it gives everyone shared numbers to weigh tradeoffs against, which requires the assumptions
  be visible enough to argue with [S4].

## P10 — the read path that goes straight to disk

- **Concern:** `caching-the-read-path.md` — never spoken aloud
- **Symptom:** 20k queries/second land directly on the primary database. The data being read changes
  a few times an hour.
- **Looking for:** A read-through cache — check first, fall through on miss, write back — with a
  short TTL chosen against the data's volatility rather than a global default [S4].
- **Bar:** Senior — optimizing the read path is explicitly in the senior bar [S4].
- **Follow-up if thin:** Ask what the TTL should be and why. High read rate with low update
  frequency is what makes something a good candidate at all [S4].

## P11 — the stale number that got committed

- **Concern:** `caching-the-read-path.md` — never spoken aloud
- **Symptom:** A one-minute TTL is in place, yet a customer successfully claimed an item that had
  been gone for 40 seconds.
- **Looking for:** TTL bounds how long staleness can persist but does not prevent it; the writing
  path must expire affected entries when it updates the underlying data [S4].
- **Bar:** Senior [S4].
- **Follow-up if thin:** Ask who is responsible for the invalidation — the answer is the service
  performing the write, not the cache [S4].

## P12 — every query touches every shard

- **Concern:** `partitioning-by-query-locality.md` — never spoken aloud
- **Symptom:** The data is split into shards by item id. Every "what can I get here?" request fans
  out to all of them and waits for the slowest.
- **Looking for:** Partitioning on the dimension reads are already scoped by, deriving the key from
  the access pattern rather than the entity — S4 groups sites into regions from a zipcode prefix so
  queries land on one or two partitions [S4].
- **Bar:** Senior — S4 names partitioning here as **trivial** and something that should jump out to
  an experienced engineer [S4].
- **Follow-up if thin:** Ask what their queries actually filter on, then compare that to the
  partition key [S4].

## P13 — reads and writes on the same node

- **Concern:** `partitioning-by-query-locality.md` — never spoken aloud
- **Symptom:** Browsing traffic and claim transactions both hit the primary. The primary is
  saturated by browsing.
- **Looking for:** Splitting by *consistency requirement* rather than by load — reads that tolerate
  slight staleness go to replicas, operations that must be strongly consistent go to the leader
  [S4].
- **Bar:** Senior — both critical paths are named in the senior bar [S4].
- **Follow-up if thin:** Ask which of their operations would break on a stale read, which is the
  test that assigns each one a destination [S4].

## P14 — the ongoing cost of replicas

- **Concern:** `partitioning-by-query-locality.md` — never spoken aloud
- **Symptom:** Six months after launch, one replica is at 90% CPU and the others are at 15%.
- **Looking for:** Replica sizing and partition distribution are ongoing operational parameters, not
  set-and-forget — a derived grouping key does not guarantee even load [S4].
- **Bar:** Senior [S4].
- **Follow-up if thin:** Ask what they would watch to notice this before a customer does. S4 names
  the obligation to manage partitioning to avoid overloading a replica, without naming a method
  [S4].

## P15 — two customers, one physical box

- **Concern:** `preventing-double-allocation.md` — never spoken aloud
- **Symptom:** Two orders confirmed for the last unit in a building. One customer gets a phone call.
- **Looking for:** Checking availability, recording the claim, and decrementing inventory as one
  atomic operation, with a serializable transaction rejecting one of two concurrent claimants [S4].
- **Bar:** Senior for an *optimized* solution [S4]. Note the mid-level allowance below.
- **Follow-up if thin:** Ask what happens under two simultaneous requests, specifically, rather than
  in the general case [S4].

## P16 — the claim that half happened

- **Concern:** `preventing-double-allocation.md` — never spoken aloud
- **Symptom:** Orders live in one datastore and inventory in another, coordinated by a lock. After a
  service crash, an order exists for stock that was never decremented, and someone else later buys
  it.
- **Looking for:** Recognizing that a claim spanning two stores converts an atomicity requirement
  into a reconciliation job you must sweep and reverse, and that colocating the data in one ACID
  store is what avoids it [S4].
- **Bar:** Senior [S4].
- **Follow-up if thin:** Ask what the two-store split bought them. S4 credits the upside — the ideal
  datastore per concern — and then prices it [S4].

## P17 — two carts, two locks, no progress

- **Concern:** `preventing-double-allocation.md` — never spoken aloud
- **Symptom:** Two orders each want items A and B. One holds A, the other holds B. Both wait
  forever.
- **Looking for:** Naming deadlock as a consequence of overlapping multi-item claims acquiring locks
  independently, and that taking this route obliges you to address it [S4].
- **Bar:** Senior [S4].
- **Follow-up if thin:** Neither S3 nor S4 gives an ordering rule, so do not grade a specific fix —
  push only for recognition that overlap is the trigger [S4].

## P18 — the device without its battery

- **Concern:** `preventing-double-allocation.md` — never spoken aloud
- **Symptom:** A five-item order partially succeeds. The customer receives four items and a refund,
  and complains that the four are useless without the fifth.
- **Looking for:** All-or-nothing can be the *correct* semantic rather than a limitation, decided by
  whether the items are useful separately — paired with a meaningful error rather than a silent
  partial [S4].
- **Bar:** Senior [S4].
- **Follow-up if thin:** Ask when a partial result *would* be acceptable, to check the reasoning is
  about the goods rather than about transactions [S4].

## P19 — one datastore, two workloads

- **Concern:** `service-and-data-boundaries.md` — never spoken aloud
- **Symptom:** The product catalog and the live availability data share a database. The catalog is
  read by a search system with completely different query patterns, and both teams' migrations now
  block each other.
- **Looking for:** Divergent consumers and workloads is the criterion that pushes data apart, while
  a transactional requirement pulls it together — and both judgments can be correct in one system
  [S4].
- **Bar:** Senior — articulating the pros and cons of architectural choices is the senior bar [S4].
- **Follow-up if thin:** Ask which of their tables is in a transaction with which other. The
  atomicity requirement is what makes the boundary non-negotiable [S4].

## P20 — the request that fans out to a vendor

- **Concern:** `delegating-external-operations.md` — never spoken aloud
- **Symptom:** A third-party API sits synchronously on the hottest read path, and its cost scales
  with the number of candidates considered.
- **Looking for:** When a delegated computation is per-request, the design work is reducing the
  question before asking it — use local data to prune so the external service is consulted only
  where its answer is in doubt [S4].
- **Bar:** Senior [S4].
- **Follow-up if thin:** S4 names no timeout or fallback behaviour for this dependency, so do not
  grade one — push only on bounding the fan-out [S4].

## P21 — the read that was mistaken for a promise

- **Concern:** `aggregating-availability-across-locations.md` — never spoken aloud
- **Symptom:** A customer browses from home, then places the order while travelling. The order is
  accepted against stock that cannot reach them in the promised window.
- **Looking for:** The caller's location is passed to the write path too, and reachability is
  re-checked at claim time — an availability read is not a durable authorization [S4].
- **Bar:** Senior [S4].
- **Follow-up if thin:** Ask what the read result is actually valid for, and for how long [S4].

## Coverage note

These seeds cover the concepts S4 developed for geographically distributed availability and
claiming. S4 places **payment and purchase handling, driver routing and deliveries, catalog and
search APIs, and cancellations and returns** explicitly out of scope [S4] — **do not probe those**,
and do not let a candidate's failure to mention them affect a score. Note that P19 probes the
*boundary* around the catalog, which S4 does discuss, not catalog or search functionality itself.

S4 also declares **privacy and security** and **disaster recovery** out of scope in its requirements
phase [S4]. It says nothing that establishes a bar for observability, rate limiting, authentication
and authorization, idempotency, multi-region deployment, cost modelling, or asynchronous processing.
Do not probe or score them. Add seeds only when a source establishes the bar.

Two grading constraints from `level-expectations.md` apply directly to these seeds. First, S4 rates
this problem class **easy** and sets a correspondingly forgiving mid-level bar: on a candidate
choosing a "Bad" solution, the interviewer expects a good discussion but **not** that the candidate
jumps to a great or even good solution [S4]. So P6 through P8 and P15 through P18 must not be counted
as mid-level misses on the strength of the solution chosen — grade the discussion. Second, S4's
mid-level bar is breadth-focused and states outright that the optimality of the solution is "icing on
top rather than the focus" [S4], so depth probes carry no mid-level weight at all.

Unlike S3, S4 gives **no explicit prompted-versus-unprompted allowance** at senior on any topic. Do
not import S3's "some probing/hints is ok" concession here; S4's senior expectation is stated as
recognition — read volume and partitioning should "jump out" — which is an unprompted framing [S4].

## Sources

- **[S4]** Hello Interview — Design a Local Delivery Service like Gopuff —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/gopuff>
