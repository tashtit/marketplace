# Scaling Writes

## Establish the bottleneck

- Estimate write volume and identify disk I/O, CPU, or network limits before adding components. Stronger hardware and local tuning can avoid premature distribution. [S9]
- Write-optimized append-oriented storage trades read work for write throughput. Indexes, triggers, and constraints add write cost; removing features changes what the database does for reads or correctness and is a tradeoff, not a free improvement. [S9]

## Distribute work deliberately

- Horizontal shards divide records. Choose keys that spread write load while grouping frequently accessed data; count the shards each common read must contact. A country key can skew load badly even with many shards. [S9]
- Key-to-node routing can use assigned hash slots or consistent hashing. Naming sharding without explaining the key and routing leaves the central design unresolved. [S9]
- Vertical partitioning separates fields with different access patterns: relatively stable content, frequently updated counters, and append-only analytics can use independently optimized stores. [S9]
- Gradual resharding writes to old and new locations while moving data and prefers the new location for reads. The source presents this migration shape but does not resolve every partial dual-write failure. [S9]

## Bursts and sustained overload

- A durable queue separates accepting a write from committing it to the database. Clients may need completion status, and requirements must permit delay or inconsistent reads. [S9]
- Queues absorb temporary bursts; they do not fix sustained arrival rates above processing capacity. Autoscaling takes time, and database scaling may reduce throughput during the transition. [S9]
- Load shedding drops less valuable work when the business permits it, such as redundant location reports, to preserve more important writes. [S9]

## Reduce the number of writes

- Batching amortizes round trips and transaction/index overhead but adds latency. A batch buffered only in application memory can lose acknowledged data on a crash; replayable upstream input changes that risk. [S9]
- Aggregate repeated updates to the same entity within a window. A one-minute window does little if an entity receives only one event per hour; measure the distribution rather than assuming batching pays. [S9]
- Hierarchical aggregation combines input at intermediate processors and distributes output through broadcast nodes. This bounds per-component fan-in/fan-out at the cost of added latency and stages. [S9]
- Split a hot aggregate into subkeys and combine them on read. Fixed splitting increases storage and read work; dynamic splitting requires readers and writers to agree on the split. This applies to aggregatable values, not arbitrary atomic records. [S9]

## Not covered by sources

- How should resharding reconcile a write that succeeds in only one location?
- How should dropped writes be accounted for in business reporting?

## Sources

- **[S9]** Hello Interview — Scaling Writes — <https://www.hellointerview.com/learn/system-design/patterns/scaling-writes> (user-supplied saved HTML, processed 2026-11-01).
