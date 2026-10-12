# Fan-Out: Assembling at Read Time vs Precomputing at Write Time

When one request must gather data belonging to many other records, the assembly work can happen
when the request arrives or when the underlying data is written — and the choice is between one
expensive read path and one expensive write path [S5].

## When it applies

- A single incoming request cannot be answered from one record. S5's shape: to answer a request
  you must first look up a set of related entities, then query each one's data, then merge and
  sort the results [S5].
- The number of related entities is unbounded, or bounded only by product policy [S5].
- A latency requirement applies to the request doing the gathering [S5].
- The result is an expensive filtered query, such as candidates matching several attributes and a
  location, that the user expects to be ready the moment they open the app [S7].

## The two directions, named

**Fan-out on read.** A single read request fans out to create many more requests [S5]. The
assembly happens at request time, so the data is always current, and nothing is stored that
would need maintaining.

**Fan-out on write.** Instead of assembling the result when it is asked for, precompute it when
the underlying data is created [S5]. The read becomes a single lookup of an already-assembled
result.

S5's framing of how to move between them is worth keeping as a prompt: when the read fan-out is
the problem, the instinct should be to look for ways to compute the results **on write** instead
[S5].

## The magnitude threshold

S5 gives an order-of-magnitude bound rather than a rule, and it is the most transferable claim in
the section: it is **not uncommon to generate 10s to 100s of requests to satisfy one incoming
request, but rarer to have to generate 1000's** — especially for a service that must serve users
with low latency [S5].

So fan-out on read is not inherently wrong. It becomes wrong at a magnitude, and the magnitude is
lower when latency matters [S5].

## What buys the write-side path

The write-side fan-out is only affordable because of a requirement, not because of a mechanism.
S5 is explicit: because some inconsistency was accepted in the non-functional requirements, there
is a **window of time** in which the writes may be performed [S5] — in its case under one minute.

The transferable form: a stated staleness tolerance is what converts a synchronous write
amplification into a background one. Without it, the millions of writes are on the critical path
of the original request. See `requirements-scoping.md` for stating that tolerance as a benchmark.

## Approaches for the write-side fan-out

S5 grades three, and the grades are the useful part.

**Blast the writes from the host that received the original write — graded bad** [S5]. Its stated
failure modes:

- **Connection limits.** A single host cannot open the number of connections required [S5].
- **Latency.** The work does not fit in the time available [S5].
- **Uneven load, even when it does work.** One host may be writing to millions of records while
  another is idle, which makes the system difficult to scale [S5]. See
  `hot-key-load-distribution.md` — the same skew, on the write side.

**Async workers behind a queue — graded good** [S5]. Queue up the write requests and have a fleet
of workers consume them and apply the updates [S5].

- **The stated requirements on the queue** are at-least-once delivery and high scalability [S5].
- **The message carries identifiers, not the work.** S5 enqueues the id of the new record and the
  id of its creator; each worker then looks up the affected set itself and applies the update
  [S5].
- **Challenge: worker throughput must be enormous** [S5]. Small cases are cheap — a few hundred
  writes — while the extreme cases dominate the fleet's work [S5].
- **Challenge: the cost per queue entry is wildly variable.** One entry representing a million
  downstream writes is dramatically more work than one representing a thousand, and S5 says such
  tasks may need to be broken up [S5]. A uniform queue of non-uniform tasks is the failure.

**Hybrid, chosen per record — graded great** [S5]. Mark the extreme cases as *not precomputed*, and
have the workers skip them; at read time, merge the partially precomputed result with a live query
for the excluded ones [S5].

- The exclusion is stored as a flag on the relationship itself, so the worker can see it [S5].
- **This makes read-vs-write a per-entity decision rather than a system-wide one**, and for most
  entities the system ends up doing a little of both [S5].
- S5 names the generalization directly as a design principle: in most situations you do not need a
  one-size-fits-all solution — solve for the different types of problem separately and combine the
  solutions [S5].
- **The cost:** more computation in the read path, since the merge happens at read time, and the
  threshold above which an entity is excluded is a tunable parameter [S5].

## Bounding the precomputed result

A precomputed result does not have to be complete. S5 stores only a small fixed number of entries
per record — around 200 — holding identifiers rather than full records, so each entry stays compact
and total space stays small [S5]. Two consequences it draws:

- **The general path remains the fallback.** When a caller exhausts the precomputed result, the
  system can fall back to querying the underlying tables directly [S5]. The precomputed result is
  an optimization for the common case, not the only way to answer.
- **The bound is a cost/benefit dial**, tunable by how much it affects tail users against the
  storage it costs [S5].

See `cursor-pagination.md` for the stated reason a small bound is acceptable at all.

## Precomputing on a schedule, with a live fallback

S7 precomputes on a timer rather than on write, and grades three options for a low-latency
candidate feed [S7]:

**Query an indexed search store in real time — graded good** [S7]. Index the fields the feed filters
on, including a geospatial index on location, in a search-optimized store, and build each feed on
demand [S7]. The challenge is keeping that store in sync with the primary database. Lag or failure
shows users outdated profiles or misses new candidates [S7]. See `full-text-search.md` for the sync
mechanism and `proximity-candidate-filtering.md` for the location filter.

**Precompute and cache feeds in background jobs — graded good** [S7]. Periodic jobs build each
user's feed and cache it, so it is ready when the app opens. The jobs can run off-peak [S7].
Challenges [S7]:

- Very active users exhaust their cached feed and wait while more is generated.
- Precomputed feeds miss recent changes to profiles and preferences, and new users.
- Running out of the cached feed means running the expensive query again.

**Combine the two — graded great** [S7]. Serve the precomputed feed immediately. As it runs low,
generate more in real time from the indexed store [S7]. Trigger the refresh when only a few items
remain, so the feed appears endless to the user [S7]. This has the same shape as S5's bounded
precomputed result with a fallback to the general path [S5][S7].

### Staleness of a scheduled precomputation

S7 names the cost of precomputing as **stale entries**: candidates that no longer match the user's
filter [S7]. Entries become stale when [S7]:

- a candidate moves out of range, or changes the attributes that qualified them;
- the user changes their own filters, or moves a significant distance.

Its stated mitigations [S7]:

- **A strict TTL on cached feeds**, under an hour, with a background job recomputing on a schedule.
- **Precompute only for users active within a chosen window.** Doing the work several times a day
  for everyone is expensive at scale, so warm the caches only for users likely to use them.
- **Refresh in the background when the user changes their filters or location**, so that the next
  feed is ready when they start using it.

### Tunable parameters as a design property

S7 draws a general lesson from these mitigations. The TTL, the number of cached entries, and the set
of users whose feeds are precomputed can all be tuned without changing the system's logic [S7]. Such
parameters let operators find an efficient configuration for the scale, adjust it over time, and
control the system's health without reworking it [S7]. S5's threshold and bound are parameters of
the same kind [S5].

## Failure modes

- **A read that fans out into thousands of downstream requests** under a latency requirement [S5].
- **Write amplification landing on the request path**, when no staleness tolerance was stated
  [S5].
- **A single host attempting the whole fan-out**, hitting connection and latency limits [S5].
- **Uneven load across a fleet**, when the fan-out work is not distributed [S5].
- **A queue whose entries have order-of-magnitude different costs**, so workers cannot be sized
  [S5].
- **Precomputing for the extreme case anyway**, when excluding it was the point [S5].
- **Serving entries that no longer qualify**, from a precomputed result whose inputs changed [S7].
- **Very active users outrunning a precomputed result** and waiting on the expensive path [S7].
- **Precomputing for users who never return**, paying the cost with no benefit [S7].

## Not covered by sources

- How to choose the threshold above which an entity is excluded from precomputation.
- How to size the worker fleet, or how to break up an oversized task once identified.
- What happens when a precomputed result and the live merge disagree, or produce duplicates.
- How the precomputed result is repaired if a worker's at-least-once delivery produces a double
  write.
- What the merge at read time costs, relative to the fan-out it replaced.
- How to backfill precomputed results when a new relationship is created, as opposed to a new
  record.
- Whether the excluded-entity flag can be changed live, and what happens to in-flight work.
- How to choose the activity window for precomputing, or the number of remaining entries that
  triggers a refresh.
- How a change on a candidate's side, as opposed to the user's, reaches the precomputed results that
  already contain that candidate.

## Sources

- **[S5]** Hello Interview — Design Facebook's News Feed —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/fb-news-feed>
- **[S7]** Hello Interview — Design a Dating App Like Tinder —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/tinder>
