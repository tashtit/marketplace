# Scaling Reads

## Start with the query

- Optimize queries and indexes before distributing the database. Index frequently filtered, joined, and sorted columns; use the query plan to distinguish scans from index lookups. Composite-index column order must match the access pattern. [S8]
- More memory, faster storage, or more CPU can buy capacity without a distributed architecture. The source's rough horizontal-scaling threshold of 50,000–100,000 indexed reads/second depends on hardware, queries, and the data model; it is not a universal limit. [S8]
- Denormalization reduces joins by duplicating data, at the cost of updating multiple copies. Materialized views precompute expensive aggregates rather than rebuilding them on every read. Choose based on the read/write ratio. [S8]

## Replicas, partitions, and caches

- Read replicas distribute reads while the primary handles writes. Asynchronous replication can return stale data, including a user's own recent write; synchronous replication trades latency for consistency. [S8]
- Replicas retain the full dataset. Sharding reduces each node's dataset and can improve locality, but adds operational complexity; caching is often a simpler response to repeated reads. [S8]
- Cache-aside checks memory first, reads the database on a miss, then populates the cache. Skewed popularity makes this useful because many requests reuse the same results. [S8]
- Set TTLs from the permitted staleness. Active updates/deletes add write latency and error handling; queued invalidation leaves a stale window; tagged invalidation requires maintaining dependencies. [S8]
- CDN caches reduce geographic latency and origin traffic for shared content. The source advises against CDN caching of private or user-specific data with no shared hit-rate benefit. [S8]

## Failure and overload cases

- Coalesce concurrent fetches for one key within each application server. This reduces backend requests to one per coalescing server, not one globally. [S8]
- A single cached key can exhaust its server's CPU or network. Replicating it under multiple keys spreads reads but consumes more memory and requires invalidating every copy. [S8]
- Popular entries expiring together cause a cache stampede. Serializing rebuilds with a distributed lock protects the database but makes callers wait and requires timeout/failure handling. Probabilistic early refresh spreads refresh attempts while serving cached data; scheduled refresh avoids demand-driven rebuilds at the cost of infrastructure and potentially wasted work. [S8]
- For entity caches, increment a database version in the same transaction as the update and include it in the cache key. Late fills cannot overwrite another version. Readers still need the current version; extra lookups and old-version cleanup add cost. This is less useful for feeds and computed search results. [S8]
- A small recently-deleted-ID cache can filter cached feeds while larger invalidations propagate. CDN invalidation also takes time; critical data may need to bypass edge caching. [S8]

## When to stop

Small workloads may need only one indexed database. Frequent writes, strict freshness, and collaborative editing constrain how much caching helps; choose against the actual workload and consistency requirements. [S8]

## Not covered by sources

- How should a system guarantee freshness if the cached version pointer itself is stale?
- How should private cache entries be isolated across tenants?

## Sources

- **[S8]** Hello Interview — Scaling Reads — <https://www.hellointerview.com/learn/system-design/patterns/scaling-reads> (user-supplied saved HTML, processed 2026-11-01).
