# Atomic Reciprocal Actions

When two users can independently perform reciprocal actions, a match check must not race ahead of both writes or the system can miss a completed pair [S6].

## Why it matters

If two actors both check for the other's action before either writes, both checks return empty; after both writes, neither actor receives the expected immediate result [S6]. Polling later can reconcile missed pairs, but trades immediate feedback for availability and adds periodic database load [S6].

## Approaches and tradeoffs

- **Colocate reciprocal state.** Derive the same key from a sorted pair of user IDs regardless of action direction, so both sides land on one partition or shard; a per-actor partition would separate the two sides [S6].
- **Single-partition conditional operations.** Cassandra lightweight transactions provide linearizable consistency within one partition via Paxos, but not multi-partition atomicity, isolation levels, or rollbacks; multiple node round trips impose overhead [S6]. The source proposes pair-keyed swipes to keep reciprocal operations local, while noting that partitions can grow and hot traffic needs cleanup and management [S6].
- **Atomic in-memory operations.** A Redis Lua script can record one action and read its counterpart in one operation on a pair-keyed hash, with low in-memory latency; a durable store retains the historical record [S6]. This creates operational concerns around node failures, rebalancing, and memory use [S6].

## Not covered by sources

- How is the immediate result delivered exactly once if processing crashes after detecting a reciprocal action?
- How does the historical store participate when the in-memory copy expires or disappears?
- How is a pair-keyed conditional read-and-write implemented with the datastore's supported transaction syntax?

## Sources

- **[S6]** Hello Interview — Design a Dating App Like Tinder —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/tinder>
