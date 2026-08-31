# Partitioning by the Query's Locality

When every read is already scoped to a narrow slice of the keyspace, partitioning on that slice
turns a full-dataset query into a one- or two-partition query [S4].

## When it applies

- Reads are never global. S4's case: inventory is only ever read for a nearby collection of
  locations, never across the whole dataset [S4].
- A natural grouping key exists in the data or can be derived cheaply from it [S4].
- A single instance is showing read pressure that indexing alone does not relieve — see
  `read-heavy-workloads.md` and `caching-the-read-path.md` for the alternatives to reach for
  alongside this one.

## Deriving the partition key from the access pattern

S4 derives the key rather than adopting a pre-existing one: group locations together under a region
id built from **the first 3 digits of their zipcode**, then partition on that region id [S4]. The
stated effect is that queries land on mostly one or two partitions instead of the entire dataset
[S4].

The transferable move is that the partition key is chosen to match the shape of the query, not the
shape of the entity. A key that does not align with how reads are scoped leaves every read
touching every partition.

S4's level expectations name this problem class as one an experienced engineer should spot
immediately, alongside read volume — it calls the partitioning here **trivial**, which is itself the
signal: when the access pattern is inherently local, the partitioning decision is not the hard part
of the design [S4].

## Splitting reads to replicas, by consistency requirement

S4 pairs partitioning with replication, and the split is drawn on the consistency requirement rather
than on load [S4]:

- **Reads that tolerate slight staleness go to read replicas.** S4's availability queries qualify
  explicitly: they can tolerate a small amount of inconsistency [S4].
- **Operations that must be strongly consistent go to the leader.** S4 routes its order
  transactions there because they must not double-allocate [S4]. See
  `preventing-double-allocation.md`.

This is the same per-operation consistency reasoning as `requirements-scoping.md`, applied at the
level of physical routing: the CAP ranking chosen per operation becomes which node the operation
talks to.

## Costs

S4 names two ongoing burdens rather than one-time ones [S4]:

- **Replica sizing must be balanced against traffic**, so the replica count is an operational
  parameter, not a set-and-forget decision.
- **The partitioning itself must be managed to avoid overloading any one replica** — a derived key
  does not guarantee even load, so distribution has to be watched.

## Failure modes

- **Partitioning on a key the queries do not filter by**, so every read still fans out to every
  partition [S4].
- **One partition absorbing disproportionate load**, when the derived grouping is uneven [S4].
- **Under-provisioned replicas** as traffic grows past the sizing they were chosen for [S4].
- **Sending a strongly consistent operation to a replica**, which is what the leader/replica split
  exists to prevent [S4].

## Not covered by sources

- How to detect and repair a hot partition once the grouping proves uneven.
- Whether and how to repartition after the fact, and what that costs.
- How large the replication lag is allowed to be before "a small amount of inconsistency" stops
  being tolerable.
- What happens to a query whose scope legitimately spans many partitions.
- How the region grouping behaves at the edges, where nearby locations fall under different keys.

## Sources

- **[S4]** Hello Interview — Design a Local Delivery Service like Gopuff —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/gopuff>
