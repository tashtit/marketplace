# Detecting Mutual Actions

When an outcome depends on two parties each acting toward the other, such as a match when both say
yes, recording one action and checking for the other must happen as one step. Otherwise
near-simultaneous actions can both miss each other [S7].

## When it applies

- An outcome fires only when two users have each taken an action toward the other, and the second
  action may come long after the first [S7].
- The second actor must learn of the outcome immediately, so it cannot wait for a later pass [S7].
- The volume of actions is large enough that they cannot all sit on one partition [S7].

## Why the naive flow fails

The naive flow is: write my action, then look for the reverse one. The source's failure sequence for
two parties acting at about the same time [S7]:

1. A's action arrives and the check for B's action finds nothing.
2. B's action arrives and the check for A's action finds nothing.
3. A's action is saved.
4. B's action is saved.

Both actions are stored, but the outcome is never detected, so neither party is told [S7].

## Ranking consistency for this operation

The source requires strong consistency for this action specifically, because the last actor has to
be told at once [S7]. It describes the alternative as a legitimate tradeoff to discuss. A periodic
reconciliation process could find reciprocal pairs that were missed and notify both parties, who
would assume the other had just acted. That favours availability over consistency [S7]. The source
cautions that this makes the problem less challenging, so an interviewer may welcome the discussion
but still ask you to keep consistency [S7]. See `requirements-scoping.md` on ranking consistency per
operation.

## Approaches and tradeoffs

**Poll the store for reciprocal pairs — graded bad** [S7]. A periodic job finds matching pairs and
creates the outcome. It cannot notify anyone immediately, so the source calls it a non-starter that
is still worth naming. Its challenges are latency between polls, which loses the instant feedback
the experience depends on, and unnecessary load on the database from frequent polling [S7].

**A transaction around the write and the check — graded good** [S7]. If consistency is required,
the source says to reach for transactions first: save the action and check for the reverse one in
the same transaction, so that both succeed or neither does [S7]. At this volume, though, the
transaction would have to span partitions [S7]. The source's stated example is a store whose
lightweight transactions give linearizable consistency only within one partition. They have no
multi-partition atomicity, isolation levels or rollback, and they need several round trips between
nodes, so they suit simple conditional updates but not complex workflows [S7].

**Put both directions in the same partition — graded great** [S7]. Build the partition key from the
two user IDs in sorted order, so that A→B and B→A always land in the same partition. Then record and
check atomically within that one partition [S7]. This avoids distributed transactions entirely
[S7]. Challenges [S7]:

- Partitions grow as a pair accumulates history, which can hurt performance.
- Very active users can create hot partitions. See `hot-key-load-distribution.md`.
- A cleanup strategy is needed to archive or delete old records so that partitions do not grow
  without bound.

**An in-memory atomic store keyed by the pair, backed by a durable store — graded great** [S7].
The same sorted-pair key, held in an in-memory store. A server-side script records one party's
action and reads the other's in a single atomic operation [S7]. The source's reasoning is that its
durable, write-heavy store is not built for this kind of atomic operation, while the in-memory store
gives consistency at low latency and scales horizontally. Consistent hashing keeps each pair's key
on one node [S7]. Challenges [S7]:

- The cluster has to be operated carefully, including node failures and rebalancing the hashing
  ring. The source judges this easier than getting consistency out of the durable store.
- Memory has to be managed. Because the durable store holds the full history, the in-memory copy can
  expire data aggressively and keep only recent actions, flushing to the durable store periodically
  [S7].
- If a node is lost, only the ability to detect outcomes for very recent actions is lost. Users can
  act again, and the historical record survives [S7].

## Notifying both parties

The two parties are notified differently [S7]:

- **The second actor** is told inline, in the response to the action that completed the pair [S7].
- **The first actor** may have acted weeks earlier and is not in the flow, so they are told by a
  push notification delivered through a device-native push service [S7].

The source treats delivery as an external capability it assumes exists, and advises stating that
assumption to the interviewer [S7].

## Failure modes

- **A lost outcome**, when both parties check before either write lands [S7].
- **Delayed outcomes and polling load**, when detection is left to a periodic job [S7].
- **Transactions that cannot span the data**, when the pair is split across partitions [S7].
- **Unbounded partition growth and hot partitions**, when both directions share a partition [S7].
- **Missed detection for very recent actions** after losing an in-memory node [S7].

## Not covered by sources

- How the in-memory and durable copies are kept consistent if a flush fails.
- How an outcome is created idempotently if the same pair is detected twice.
- What happens if the push notification to the first actor fails.
- How long recent actions must stay in memory for detection to remain correct.
- How the cleanup strategy decides which history to keep.

## Sources

- **[S7]** Hello Interview — Design a Dating App Like Tinder —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/tinder>
