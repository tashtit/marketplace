# Record Expiry

When records carry an expiration time, expiry has to be enforced on the read path, propagated
into every cache, and cleaned up in storage [S1].

## When it applies

- Records have an optional or mandatory expiration date supplied at creation time [S1].
- Those records are also cached, which means expiry now has two places to be honored [S1].

## Why it matters

Expiry is not a storage detail; it is a correctness property of every read. A record past its
expiration must not resolve, and a cache that does not know about expiry will keep serving it
after the database would have stopped [S1].

## Approaches and tradeoffs

**Enforce on read.** Compare the current time against the stored expiration date as part of the
lookup, and only return the record if it has not expired [S1].

**Distinguish expired from absent in the response.** For expired records the source returns
`410 Gone` rather than a generic not-found, which tells the caller the record existed and is
deliberately no longer available [S1].

**Align cache TTL with record expiry.** The source calls this the more important of the two
cleanup concerns: set the cache TTL to match or be shorter than the record's expiration time,
so stale entries are evicted automatically [S1]. This makes the cache's own expiry mechanism do
the invalidation work rather than requiring an explicit purge.

**Storage cleanup is optional.** A background job can periodically delete expired rows — or you
can simply keep them with their expiration date, since the read path already filters them [S1].
The source presents deletion and retention as equally acceptable, which frames cleanup as a
storage-cost decision rather than a correctness one [S1].

## Expiry as a derived predicate rather than stored state

S3 arrives at the same enforce-on-read conclusion from a different direction, and adds a reason
that generalizes: when a record's effective state is "expired unless proven otherwise", deriving it
at read time makes the cleanup job **non-load-bearing** — a delayed sweep no longer changes system
behavior, whereas in a design that relies on the sweep to flip the stored status, a delayed sweep
is a correctness problem [S3]. The cost is that reads must filter on two columns rather than one,
partly recoverable with a compound index or a materialized view, and that the stored rows are less
legible to other consumers because some read as active but are actually expired [S3]. See
`preventing-double-allocation.md`.

**Where the store has no native expiry, that is itself a design input.** S3's stated reason for
introducing a separate in-memory store for holds is that its relational database has no row-level
time-to-live, so automatic expiration would have to be reimplemented as application logic [S3].

**A collection of expiring items needs its own expiry semantics.** If expiring entries are tracked
in an aggregate structure, membership of that structure must expire too, or abandoned entries
persist as ghosts forever; S3's fix is to score members by expiry time so a read counts only
entries scored in the future, and stale members can be trimmed lazily [S3].

## Interaction with caching

A cache TTL longer than the record's expiration is the specific bug this concept exists to
prevent: the database would reject the record while the cache continues to serve it [S1]. See
`caching-the-read-path.md`.

## Failure modes

- **A cache serving an expired record** because its TTL outlives the record's expiration [S1].
- **Expired records resolving normally** when the read path does not check the expiration date
  [S1].
- **Unbounded growth of expired rows** when no cleanup job runs and retention was not a
  deliberate choice [S1].
- **Records stuck in their pre-expiry state** when the sweep that flips stored status is delayed
  or failed [S3].
- **Ghost entries in an aggregate** whose members do not expire with the records they track [S3].

## Not covered by sources

- How often a cleanup job should run, or how to delete in batches without disrupting live
  traffic.
- Whether expired identifiers may be reissued.
- Expiry at CDN or edge tiers, where TTL alignment is harder to guarantee.
- Whether callers should be able to extend or renew an expiration. S3 recommends extending a hold
  when a dependent operation begins but does not describe how to bound that.

## Sources

- **[S1]** Hello Interview — Design Bit.ly —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/bitly>
- **[S3]** Hello Interview — Design Ticketmaster —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster>
