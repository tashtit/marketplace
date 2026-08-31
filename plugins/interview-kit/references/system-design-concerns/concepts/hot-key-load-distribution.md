# Hot Keys and Load Distribution Across a Keyspace

A store that scales on aggregate throughput can still fail when the load is concentrated on a few
keys, because the physical machine behind those keys has its own limit [S5].

## When it applies

- A key-value or partitioned store is chosen for its throughput ceiling, and that ceiling is
  conditional on load being spread across the keyspace [S5].
- Access is naturally skewed. S5's shape: most records are read for a few days and never again,
  while a few records take a massive share of reads in their first hours [S5].
- The skew is a property of the domain, not a bug to be fixed upstream.

## Why aggregate throughput is the wrong number

S5 states the condition plainly: such stores scale to very high throughput **provided certain
conditions are met**, and one of the more important is **even load across the keyspace** [S5].
Under the covers there are physical machines with real limitations like any other database, so one
key taking hundreds of requests per second while its neighbours take none is not even load [S5].

The transferable point is that a throughput figure quoted for a distributed store is a figure for
the whole keyspace, and a single key inherits only its shard's share of it.

## What makes the skew tractable

S5 names one property that makes the problem cache-shaped rather than consistency-shaped: the
records are **far more likely to be created than edited** [S5]. Where reads dominate and writes to
the same key are rare, a cache in front of the store is available as a remedy. See
`caching-the-read-path.md`.

## Approaches and tradeoffs

**A sharded cache in front of the store — graded good** [S5]. Place a distributed cache between the
readers and the store, keyed by record id so records spread evenly across the cluster [S5].

- Because records are rarely edited, a **long TTL** is acceptable, with **LRU eviction** to keep
  the working set resident [S5].
- The sizing model S5 gives: with N hosts of M memory, the cache holds what fits in N × M, and as
  long as that covers the recent or popular records, the vast majority of reads never reach the
  store [S5].
- **Invalidate on edit, not on create** [S5] — the write path's only obligation here.
- **The stated defect is that this does not solve the problem it was reached for.** A cache
  sharded by key has **the same hot key problem the store had**: the shard holding several
  simultaneously popular records gets an unequal share of load, many hosts sit underutilized, and
  the cache becomes hard to scale [S5]. Putting a distributed cache in front of a hot key moves
  the hot key; it does not spread it.

**A replicated cache, where every instance can serve any key — graded great** [S5]. The stated
difference: instead of each record living on exactly one node, every instance can serve every
record, and a load balancer spreads requests across them [S5].

- **The instances do not need to coordinate** [S5]. That is what makes the approach cheap: a
  popular record's read traffic divides across all N instances instead of hammering one shard, so
  you get **N times the throughput for a hot key with no additional coordination** [S5].
- **The cost is duplicated memory**, so the cache holds fewer distinct records overall than a
  sharded one of the same total size [S5].
- **The cost is more initial misses.** For one very popular record with N instances, the first
  wave produces up to N requests to the store rather than 1 [S5]. S5's own weighing: N is much,
  much smaller than the read volume the cache is absorbing, and the backing store can handle some
  variability in read throughput [S5].

## How to decide

The axis S5 uses is **whether your problem is capacity or concentration** [S5]:

- Sharding by key maximizes distinct records held per byte of memory, and is the right shape when
  the working set is large and load is spread.
- Replication maximizes throughput for any single key, at the cost of holding fewer records, and
  is the right shape when a few keys dominate.

Both solve the caching problem; only one solves the hot-key problem [S5].

## Failure modes

- **Relying on a store's aggregate throughput figure** when load is concentrated [S5].
- **Moving a hot key into a sharded cache** and reproducing the skew one layer up [S5].
- **Underutilized hosts alongside an overloaded one**, which is what makes a skewed tier hard to
  scale [S5].
- **A thundering set of misses on a newly popular key** in a replicated cache, bounded by the
  instance count [S5].
- **Uneven work distribution on the write side too** — S5's rejected fan-out approach fails partly
  because one host does millions of writes while another is idle [S5]. See
  `fan-out-on-read-vs-write.md`.

## Not covered by sources

- How to detect a hot key in production, or at what skew ratio to switch strategies.
- How to size the number of replicated instances, beyond "N times the throughput".
- How invalidation reaches every instance of a replicated cache, and what happens if it reaches
  only some.
- Whether a hybrid — replicating only known-hot keys while sharding the rest — is viable.
- What the memory cost of full replication is relative to the hit rate it gives up.
- How the load balancer in front of a replicated cache should distribute requests.

## Sources

- **[S5]** Hello Interview — Design Facebook's News Feed —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/fb-news-feed>
