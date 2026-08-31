# Caching the Read Path

Serving frequent reads from memory instead of disk, and pushing them geographically closer to
the caller [S1].

## When it applies

- Read volume exceeds what a disk-backed database can serve, even with correct indexing [S1].
- The data being read is mostly static after creation, which is what makes it cacheable — the
  source notes cache invalidation is normally complex but is *minimized* here precisely because
  records are read-heavy and rarely change [S1].
- Latency requirements are tight enough that disk access is the dominant cost [S1].

## Why it matters

Indexing solves the wrong problem when the issue is volume rather than lookup efficiency. The
source is explicit that the challenge lies in "the sheer volume of read operations" — a typical
SSD handles around 100,000 IOPS, which is fast, but a design target of ~600k reads per second
exceeds it [S1].

The order-of-magnitude numbers the source gives are the justification for moving to memory [S1]:

| Medium | Access time | Throughput |
| --- | --- | --- |
| Memory | ~100 ns (0.0001 ms) | millions of reads/sec |
| SSD | ~0.1 ms | ~100,000 IOPS |
| HDD | ~10 ms | ~100–200 IOPS |

Memory access is about 1,000× faster than SSD and 100,000× faster than HDD [S1].

## Approaches and tradeoffs

**In-memory cache between the application and the database.** On a request, check the cache
first; on a hit, return from memory and skip the database entirely. On a miss, query the
database, return the result, and store it in the cache for future requests [S1].

Challenges the source raises [S1]:

- **Cache invalidation can be complex**, especially when updates or deletions occur — though
  minimized when records rarely change.
- **The cache needs time to warm up.** Initial requests still hit the database until it is
  populated.
- **Memory is finite**, requiring deliberate decisions about cache size, eviction policy (LRU
  is named), and which entries to store.
- **It adds architectural complexity.** The source's framing: be ready to defend the tradeoffs
  and the invalidation strategy, not just the presence of the cache.

**CDN and edge computing.** Serve the domain through a CDN with points of presence distributed
worldwide, caching entries at the edge so requests are handled close to the caller. Going
further, deploy the read logic itself to the edge so the request never reaches the origin
server at all — meaningfully reducing latency for popular entries [S1].

Challenges the source raises [S1]:

- **Invalidation and consistency across all CDN nodes is complex.**
- **Operational cost is higher**, especially at high traffic volumes.
- **Edge functions are constrained** in execution time, memory, and available libraries,
  requiring careful optimization of the logic you deploy there.
- **Debugging and monitoring a distributed edge environment is harder** than centralized
  servers.
- **The setup itself requires additional configuration** and understanding of serverless
  functions at the edge.

The source's summary of the edge decision is the transferable part: *you are trading cost and
complexity for performance, and whether that is worth it depends on price sensitivity, user
experience requirements, and traffic patterns* [S1].

S2 corroborates the geographic argument from a different starting point and adds a cost control.
Its framing of the problem: the origin store lives in a single region, so distant users see
slower reads no matter how optimal the origin path is [S2]. Its framing of the cost: CDNs are
relatively expensive, so be strategic about *what* is cached and *for how long* — use a
cache-control header to bound the lifetime, and invalidate on update or delete, so only
frequently accessed entries occupy the edge [S2].

The two sources place the emphasis differently on caching's hard part. S1 names invalidation as
complex but minimized because its records rarely change [S1]; S2 treats invalidation as a routine
operation to perform on update or delete [S2].

## Choosing what to cache

S3 states the selection criterion directly: cache data with a **high read rate and a low update
frequency** [S3]. Its examples are static descriptive data — entity details, biographies, venue
information — keyed by identifier to the object [S3]. The corollary is that volatile data (live
availability) is the poor candidate, and the source handles it with a short TTL rather than by
excluding it [S3].

**Vary the TTL by volatility rather than setting one globally.** Long TTLs for static data, short
TTLs for frequently changing data [S3]. A single TTL forces you to serve the static data more
conservatively than necessary, or the volatile data more stalely than acceptable.

S4 reaches the same short-TTL conclusion from the volatility of the data rather than from cost. Its
read-through cache sits between the service and the database: check the cache for a given set of
inputs, return on hit, otherwise query the database and write the result back [S4]. Its stated
freshness lever is a **low TTL — on the order of 1 minute** — chosen because the cached value is
availability data that changes underneath the cache [S4].

S4 also names the obligation that a short TTL alone does not discharge: the writing path must expire
the affected cache entries when it updates the underlying data [S4]. TTL bounds how long a stale
entry can live; explicit invalidation on write is what keeps a claim from being made against a
number the cache is still serving.

S5 sets the TTL from the *opposite* property and shows the rule generalizes in both directions: its
records are very rarely edited, so it keeps a **long TTL** with **LRU eviction**, and invalidates a
specific entry only when that record is edited — not when one is created [S5]. Read alongside S3
and S4, the selection rule is one rule: the TTL tracks the write rate of the cached item, and
volatility is what moves it, not policy.

S5 also supplies a sizing model for the cache itself: with N hosts of M memory, the cache holds
what fits in N × M, and the cache earns its place as long as that is big enough to hold most of
the recent or popular records [S5]. The cache size question is therefore answerable — it is the
working set, not a fraction of the dataset.

**A cache does not fix skewed load by itself.** S5's stated defect in the obvious approach is that
a cache sharded by key inherits the hot-key problem of the store it fronts [S5] — see
`hot-key-load-distribution.md` for the replicated alternative and what it costs.

## Invalidating on change

S3 adds a mechanism beyond TTL: **database triggers that notify the caching system when the
underlying data changes**, invalidating the affected entries [S3]. It pairs this with TTL as a
periodic refresh, so the two work together rather than either being sufficient [S3]. The stated
challenge is that keeping cache and database consistent is hard specifically when updates are
frequent [S3].

## Caching query results rather than records

Repeated searches can be cached as whole result sets, keyed by the query parameters so each
distinct query gets a unique key, with a TTL for freshness [S3]. Two escalations the source
offers [S3]:

- **A search engine's own caches**, which store frequent filter results and full responses at the
  shard level — useful for aggregation-heavy queries, and adaptable over time to whichever queries
  are most frequent.
- **Edge caching of results**, which the source gates on a precondition: it only makes sense if
  results are **not personalized**, meaning the same query returns the same results for every user
  [S3].

Invalidating query-result caches is harder than invalidating record caches, because a query and
its potential results are not connected — you cannot tell from a changed record which cached
queries it affects [S3]. The source names cache tags alongside TTLs as the handle for this [S3],
and warns that caching fuzzy-matched results makes it harder still [S3]. Frequent misses also push
load back onto the search infrastructure exactly at peak [S3].

## Interaction with expiry

If cached records can expire, the cache TTL must be set to match or be shorter than the record's
expiration time, so stale entries are evicted automatically [S1]. See `record-expiry.md`.

## Failure modes

- **Serving stale entries** after an update or delete [S1].
- **Cold-cache load falling through to the database** during warm-up [S1].
- **Eviction of entries that are still hot**, when cache size or policy is misjudged [S1].
- **Divergence between CDN nodes** when invalidation does not propagate [S1].
- **Caching rarely accessed entries at the edge**, paying CDN cost for no hit rate [S2].
- **Stale results served from a query cache** whose entries no changed record maps back to [S3].
- **Serving personalized results from a shared edge cache**, when the personalization precondition
  was not checked [S3].
- **Load returning to the origin at peak** through frequent cache misses [S3].
- **A claim made against a cached quantity** that the writing path never invalidated [S4].
- **A cache that inherits the skew of the store it fronts**, when it is sharded by the same key
  [S5].

## Not covered by sources

- Concrete invalidation mechanisms beyond TTL and cache-control lifetime (both sources name
  invalidation as a challenge; neither resolves how it propagates).
- What cache hit rate to target, or how to measure whether the cache is earning its complexity.
- Behavior when the cache itself becomes unavailable.
- How to choose between cache-aside and other caching patterns; only the read-through-on-miss
  flow is described.
- How to decide which entries are worth caching at the edge, beyond "frequently accessed".
- How the notifying trigger reaches the cache, and what happens if that notification is lost.
- How to choose specific TTL values for a given volatility.
- How a cache key built from a set of request inputs is kept from fragmenting into near-unique
  entries.
- How cache tags are assigned to query results in practice.
- How to measure the working set, in order to size a cache against it.

## Sources

- **[S1]** Hello Interview — Design Bit.ly —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/bitly>
- **[S2]** Hello Interview — Design a File Storage Service Like Dropbox —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/dropbox>
- **[S3]** Hello Interview — Design Ticketmaster —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster>
- **[S4]** Hello Interview — Design a Local Delivery Service like Gopuff —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/gopuff>
- **[S5]** Hello Interview — Design Facebook's News Feed —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/fb-news-feed>
