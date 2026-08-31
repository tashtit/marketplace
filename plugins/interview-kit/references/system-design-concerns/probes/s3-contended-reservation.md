# Probe Seeds — S3

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

## P1 — Losing the item at the payment screen

- **Concern:** preventing-double-allocation
- **Symptom:** "Two users select the same item within a second of each other. Both reach your
  checkout form, both fill in their card details, and one of them gets an error after submitting.
  Support says this is your top complaint. What would you change?"
- **Looking for:** recognition that availability is only being checked at payment time, and that
  the requirement is to hold the item for the duration of checkout and release it if checkout is
  abandoned — three outcomes to handle: completed, abandoned, and a concurrent user correctly
  refused [S3].
- **Bar:** mid-level — solving this with **at least** a stored status plus timeout plus sweep job
  is sufficient at that level [S3].
- **Follow-up if thin:** ask what happens to the item if the user simply closes the tab.

## P2 — The transaction that stays open

- **Concern:** preventing-double-allocation
- **Symptom:** "A candidate holds the row in an open transaction from selection until payment
  completes. Under load the database starts reporting waits and occasional deadlocks, and after a
  process restart some items are unclaimable. Walk me through why."
- **Looking for:** that database locks are designed for near-instant transactions, so holding one
  for minutes strains resources and invites contention and deadlock; that a lock timeout surfaces
  an error rather than queueing the user gracefully; that it scales poorly; and that crashes leave
  locks in an uncertain state, so release depends on user action or a session timeout [S3].
- **Bar:** senior — the source treats this as the option a quality answer rejects on the way to a
  distributed lock or equivalent [S3].
- **Follow-up if thin:** ask how long they expect a user to spend on the payment form, and compare
  that to how long a row lock should be held.

## P3 — The sweep job that stopped

- **Concern:** preventing-double-allocation
- **Symptom:** "Your holds expire after ten minutes and a background job returns expired holds to
  the pool. The job silently failed for forty minutes during your biggest sale. What did users
  see, and what would you change so this failure is less severe?"
- **Looking for:** that the entire inventory appears unavailable when the sweep fails, and that the
  fix is to make availability a read-time predicate — claimable means available **or** reserved
  with an expired reservation — so a delayed sweep no longer changes behavior [S3]. Strong answers
  name the cost: reads filter on two columns, mitigated with a compound index or materialized
  view, and the table is less legible to other consumers [S3].
- **Bar:** senior — mid-level is not expected to move past the sweep-based solution [S3].
- **Follow-up if thin:** ask whether the cleanup job is still needed afterwards, and what breaks if
  it is late.

## P4 — Reaching outside a consistent database

- **Concern:** preventing-double-allocation
- **Symptom:** "You have a strongly consistent relational database that you trust for the booking
  transaction. A candidate adds a separate in-memory store just for holds. Is that justified, or is
  it a component for its own sake?"
- **Looking for:** the specific reason — the relational store has no native row-level expiry, so
  automatic release would have to be reimplemented in application code, whereas the in-memory store
  provides key expiration natively and is fast under high concurrency [S3]. Good answers add that
  the acquire must be atomic (set-if-absent with expiry) so there is no race, and that storing the
  claimant's identity as the value lets you verify the confirming user is the holder [S3].
- **Bar:** senior — understanding a distributed lock for this purpose is stated as expected [S3].
- **Follow-up if thin:** ask what happens when a user claims several items at once and the third
  acquisition fails.

## P5 — The lock store goes down

- **Concern:** preventing-double-allocation
- **Symptom:** "Your hold store becomes unavailable for two minutes at peak. What is the user
  impact, and is it worse or better than the sweep job failing?"
- **Looking for:** that double allocation still cannot happen, because the database enforces it
  with optimistic concurrency control or row-level locking — the hold is an experience
  optimization, not the correctness guarantee [S3]. The degraded outcome is a user occasionally
  refused after entering payment details, which the source ranks as **better** than all inventory
  appearing unavailable [S3].
- **Bar:** staff+ — reasoning about relative severity of failure modes unprompted is the kind of
  depth the source expects at that level [S3].
- **Follow-up if thin:** ask what actually prevents two confirmed sales of the same item.

## P6 — The hold expires mid-payment

- **Concern:** preventing-double-allocation
- **Symptom:** "A user's ten-minute hold lapses at minute ten; their payment authorizes at minute
  eleven, and someone else acquired the hold at minute ten and a half. What does your system do?"
- **Looking for:** that one of the two database writes fails under optimistic concurrency so only
  one succeeds, and the losing payment is refunded automatically; plus the mitigations — set the
  expiry generously, and extend the hold when payment begins [S3].
- **Bar:** staff+ [S3].
- **Follow-up if thin:** ask which of the two users should win, and how the other finds out.

## P7 — Holds that never disappear from the display

- **Concern:** preventing-double-allocation, record-expiry
- **Symptom:** "You moved holds into an external store and keep a set of held item ids so the
  availability view can render. A week in, items abandoned at checkout still show as held. Why?"
- **Looking for:** that members of the set do not expire when the individual hold keys do, so every
  abandoned checkout leaves a permanent ghost entry; and that scoring members by expiry time fixes
  it, because the read counts only entries scored in the future and stale members can be trimmed
  lazily when the structure is touched — at the cost of an extra round-trip on the read path [S3].
  Writing the held status through to the database and treating the external expiry as the source of
  truth is the stated alternative [S3].
- **Bar:** staff+ — the source presents this as the read-path complexity worth calling out
  unprompted [S3].
- **Follow-up if thin:** ask where the availability view gets its data once holds left the database.

## P8 — Search misses the latency target

- **Concern:** full-text-search
- **Symptom:** "Search filters on keywords appearing anywhere in a name or description, joined by
  `OR`. It met the latency target in staging with a thousand records and misses it badly in
  production. What is happening?"
- **Looking for:** that a leading-wildcard pattern match forces a full table scan no ordinary index
  can satisfy, and that it degrades as the record count grows [S3].
- **Bar:** senior — reaching a search-optimized data store for this class of problem is stated as
  **essential** at this level [S3].
- **Follow-up if thin:** ask whether adding an index on those columns fixes it, and why not.

## P9 — Why not just index harder

- **Concern:** full-text-search, point-lookup-indexing
- **Symptom:** "A candidate's answer to slow search is to add indexes on every searchable column.
  What do they gain, and what have they just bought?"
- **Looking for:** that standard indexes are weak on partial string matches, which is what pushes
  toward full-text capability; and that every additional index increases storage and slows writes,
  since inserts and updates must maintain it — so the number of indexes is a balance against
  overall database performance [S3]. Stronger answers reach in-database full-text indexes as the
  intermediate step, noting they are not the same engine as a dedicated search product and cost
  extra storage and maintenance [S3].
- **Bar:** senior [S3].
- **Follow-up if thin:** ask what happens on a query for a fragment of a word.

## P10 — Keeping a search index honest

- **Concern:** full-text-search
- **Symptom:** "You've added a dedicated search engine alongside your database. A user updates a
  record and search keeps returning the old text. Where does that go wrong?"
- **Looking for:** that the search index must be kept synchronized with the system of record, that
  the source's mechanism is change data capture replicating inserts, updates and deletes for
  near-real-time sync, and that synchronization is genuinely complex and needs a reliable mechanism
  plus cluster operating cost [S3]. Good answers name what the engine buys in return: inverted
  indexes for fast text lookup, and fuzzy matching for typos that would be very hard in SQL alone
  [S3].
- **Bar:** senior [S3].
- **Follow-up if thin:** ask what the system should serve while the search engine is down (the
  source does not answer this — treat a candid "I'd have to decide that" as acceptable).

## P11 — Faster updates make it worse

- **Concern:** admission-control, propagating-changes-to-clients
- **Symptom:** "You push live availability to every client over a persistent connection. For your
  biggest event, users say the view is unusable — it changes under their cursor and they still
  cannot claim anything. Pushing faster hasn't helped. What now?"
- **Looking for:** recognition that contention, not staleness, is the cause, so the answer is to
  restrict who enters the flow rather than to improve delivery — a waiting queue in front of the
  claim flow, ordered by timestamp, dequeuing users periodically or as items sell, with position
  updates pushed over a persistent connection [S3]. The strong detail: **admission is enforced
  server-side** — the dequeued user is marked admitted with an expiry and the claim service checks
  that before accepting any request [S3].
- **Bar:** senior — a discussion of handling popular events is part of the stated senior bar [S3];
  the source frames arriving here as the good-to-great delta [S3].
- **Follow-up if thin:** ask what stops a user who skips the queue page from posting a claim
  directly.

## P12 — The queue's own failure mode

- **Concern:** admission-control
- **Symptom:** "You gate entry to the claim flow and it holds up under load. But a third of users
  close the tab before their turn comes. What is driving that and what would you do?"
- **Looking for:** that long waits frustrate users, especially when estimated waits are inaccurate
  or the queue moves slower than expected, and that the mitigation is continuous feedback on
  position and estimated wait over the connection already held [S3]. Also that the queue is worth
  making an operator-enabled switch for exceptional demand rather than always on [S3].
- **Bar:** staff+ — the source raises this as a challenge to the solution rather than part of the
  senior bar [S3].
- **Follow-up if thin:** ask how the estimate is computed (the source does not say — do not grade a
  specific method).

## P13 — Caching the wrong things

- **Concern:** caching-the-read-path
- **Symptom:** "You cache everything the read endpoint returns with a single one-hour TTL.
  Descriptive detail is served fine; users complain that availability is wrong. What is the
  problem?"
- **Looking for:** the selection criterion — cache data with a high read rate and low update
  frequency — and that TTL should vary by volatility: long for static data, short for frequently
  changing data [S3]. Good answers add invalidation on change, via database triggers notifying the
  cache, working alongside TTL rather than instead of it [S3].
- **Bar:** senior [S3].
- **Follow-up if thin:** ask which fields in the response they would give different lifetimes.

## P14 — Caching whole result sets

- **Concern:** caching-the-read-path
- **Symptom:** "You cache search results keyed by the query parameters. A new record is added and
  cached result sets keep omitting it. Why is this harder than invalidating a record cache?"
- **Looking for:** that a query and its potential results are not connected, so a changed record
  does not tell you which cached queries it affects; cache tags alongside TTLs are the stated
  handle, and caching fuzzy-matched results makes it harder still [S3]. Good answers note frequent
  misses push load back to the search infrastructure exactly at peak [S3], and that edge caching of
  results is gated on results not being personalized [S3].
- **Bar:** staff+ [S3].
- **Follow-up if thin:** ask whether they would put these results on a CDN, and what has to be true
  first.

## P15 — Adding instances does not help

- **Concern:** read-heavy-workloads
- **Symptom:** "Traffic on one popular record is tens of millions of concurrent requests. You add
  instances behind a load balancer and throughput barely moves. What would you check about the
  service itself?"
- **Looking for:** that statelessness is the precondition for horizontal scaling — the service can
  be scaled by adding instances only because it holds no per-request state [S3]. Good answers
  mention the distribution algorithm (round-robin or least-connections) and that the operational
  cost is managing many instances plus deployment and rollback [S3].
- **Bar:** senior — detailed scaling strategies are expected, and the source explicitly allows that
  **"it's ok if this took some probing/hints from the interviewer"** [S3].
- **Follow-up if thin:** ask where the request-scoped state currently lives.

## P16 — One database behind several services

- **Concern:** service-and-data-boundaries
- **Symptom:** "A reviewer objects that three of your services share one database and cites
  database-per-service. Defend or change the design."
- **Looking for:** that database-per-service is not a hard rule; the stated conditions favouring a
  shared store are tightly coupled data, a requirement for ACID transactions on the critical
  operation, and that splitting would add complexity for no real benefit [S3]. The transferable
  point: the data boundary is downstream of the consistency requirement, since splitting forces you
  to reimplement atomicity across a network [S3].
- **Bar:** senior — the source asks for tradeoffs weighed and a decision made rather than dogma
  repeated [S3].
- **Follow-up if thin:** ask which single operation would become hardest if the databases were
  split.

## P17 — Availability and consistency in one system

- **Concern:** requirements-scoping
- **Symptom:** "In your non-functional requirements you wrote 'the system should be highly
  available'. Is that true of every operation here?"
- **Looking for:** the per-operation split — availability for read paths (viewing, searching) but
  strong consistency for the claim path, because two users must never be sold the same item — and
  that the unit of the CAP decision is the operation, not the system [S3]. Strong answers connect
  it forward: the consistent operation is what justifies ACID transactions and a shared store, the
  available ones justify caching and horizontal scaling [S3].
- **Bar:** mid-level — a clearly defined data model and API is part of the stated mid bar [S3],
  though the split framing itself is not graded at that level.
- **Follow-up if thin:** ask which reads must see the very latest write.

## P18 — One order, several items

- **Concern:** entity-granularity
- **Symptom:** "A candidate puts the buyer id and payment status directly on each item row. A user
  then buys four items in one go. What starts to hurt?"
- **Looking for:** that a separate entity earns its place when one transaction covers several
  items, because the group then has properties of its own — a shared payment status and a shared
  total — with nowhere else to live [S3].
- **Bar:** mid-level — a clearly defined data model is part of the stated mid bar [S3].
- **Follow-up if thin:** ask where the total price of a multi-item purchase is stored.

## P19 — Rendering a composed view

- **Concern:** entity-granularity
- **Symptom:** "Your layout structure is stored once on the parent record and each child carries
  only its own coordinates and status. How does the client end up with the interactive view?"
- **Looking for:** that the client combines the shared layout with each item's status to render,
  rather than the layout being duplicated onto children or the view materialized server-side [S3].
  A strong answer connects this to holds: once a hold lives outside the item record, the status half
  of that composition needs another source [S3].
- **Bar:** senior — the connection to where hold state lives is the part worth depth credit [S3].
- **Follow-up if thin:** ask what changes if holds move into an external store.

## P20 — The provider calls you twice

- **Concern:** delegating-external-operations
- **Symptom:** "Your payment provider notifies you by callback. Your logs show one order confirmed
  twice and, once, a duplicate downstream side effect. What is going on?"
- **Looking for:** that the provider retries callbacks on failure, so the handler is at-least-once
  and must be idempotent — embed your own identifier in the metadata, read it back as the
  idempotency key, and **check the current status before updating** [S3]. Good answers also commit
  the resulting state changes in one transaction so the two records cannot disagree [S3].
- **Bar:** senior [S3].
- **Follow-up if thin:** ask what makes a retry safe rather than merely rare.

## P21 — Card details on your servers

- **Concern:** delegating-external-operations
- **Symptom:** "Your checkout posts the card number to your API, which forwards it to the payment
  provider. What would a reviewer say?"
- **Looking for:** that the client should tokenize using the provider's client-side library so your
  server never sees the raw number, receiving only a token forwarded with your internal identifier
  — which the source states is standard for the relevant compliance regime [S3].
- **Bar:** senior [S3].
- **Follow-up if thin:** ask what your servers actually need in order to complete the charge.

## Coverage note

These seeds cover the concepts S3 developed for high-contention reservation and booking. S3 places
**viewing already-booked events, administrative creation of events and venues, and dynamic
pricing** explicitly out of scope [S3] — **do not probe those**, and do not let a candidate's
failure to mention them affect a score.

S3 also declares **GDPR compliance, fault tolerance, secure transactions for purchases, CI/CD
pipelines, and backup and recovery** out of scope in its requirements phase [S3]. Note the
tension: it nonetheless describes client-side tokenization and idempotent callbacks later in the
booking flow [S3], which is what P20 and P21 probe. Probe only what the booking-flow discussion
actually establishes; treat the broader security and reliability topics as unbarred.

S3 says nothing that establishes a bar for: observability, rate limiting, authentication and
authorization, multi-region deployment, cost modelling, or the internals of the sweep and refund
paths. Do not probe or score them. Add seeds only when a source establishes the bar.

Two named grading constraints from `level-expectations.md` apply directly to these seeds: the
mid-level bar on the contention problem is satisfied by the **status/timeout/sweep** solution, so
P3 through P7 must not be counted as mid-level misses [S3]; and the senior scaling discussion
explicitly permits **"some probing/hints"**, so a prompted answer on P15 still clears its bar [S3].

## Sources

- **[S3]** Hello Interview — Design Ticketmaster —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster>
