# Dealing with Contention

## Guard the actual resource

- Separate reads and writes leave a window in which another writer can change the state used for a decision. Enforce correctness at the resource's authoritative store rather than relying on application-server coordination alone. [S13]
- If a safety condition can be evaluated in the write, use an atomic conditional update. A failed predicate may change zero rows without raising an error; dependent inserts or side effects must be gated on success, and related database writes belong in one transaction. [S13]
- Guard the resource actually being allocated. A positive inventory counter prevents overselling the count but does not prevent two buyers selecting the same numbered seat; a conditional transition on that seat's own row makes the conflict visible. [S13]

## Read, decide, then write

- Pessimistic locking holds the relevant rows while application code makes its decision. It is predictable when conflicts are frequent, but broad locks or long transactions serialize unrelated work. Keep slow external I/O outside the locked interval. [S13]
- Acquire shared resources in one globally consistent order to prevent circular waiting. Handle database deadlock-abort errors by retrying; a lock-wait timeout is a separate backstop for locks held too long. [S13]
- Optimistic concurrency records a version on read and conditions the write on that version, changing it on every successful update. Re-read and retry or reject when the affected count is zero. Rare conflicts favor this approach; repeated conflicts can make retries more expensive than locking. [S13]
- A business value that returns to its original value hides intervening changes, the ABA problem. The source's preferred defense is a dedicated monotonically increasing version; timestamps require adequate resolution and updates on every write. [S13]

## Cross-row invariants

- Write skew occurs when transactions rely on overlapping reads but update different rows. Checks limited to each writer's own row can allow both transactions to commit while violating the shared rule. [S13]
- Serializable isolation can detect this conflict and abort an execution for the application to retry. Alternatively, materialize the invariant on a common row that every participant guards. The source cautions that stricter isolation adds tracking and retry cost. [S13]

## Reservations across a wait

- A transaction-scoped row lock is a poor fit for holding a resource through a long checkout. Store a reservation owner and expiry as shared data so the hold outlives one transaction and is visible across request handlers. [S13]
- A database reservation can claim the row conditionally when free or expired. Expiry participates in the acquisition predicate, so correctness need not wait for a cleanup job. This reuses the database but its hot reservation row can still bottleneck. [S13]
- Redis SET with NX and expiry provides a fast lease, but an owner paused beyond expiry may resume after another caller acquires it. A TTL alone does not guarantee exclusive action. Coordination services offer stronger coordination behavior at the cost of another cluster to operate. [S13]

## One extremely hot resource

- Adding shards or application servers does not split a conflict over one indivisible row. First consider whether requirements permit dividing the resource or relaxing immediacy. [S13]
- When strong ordering is needed, process that resource's requests sequentially through a queue and one worker. This exchanges contention for bounded serial throughput, waiting time, and a worker failure dependency requiring a standby. [S13]
- Keep one authoritative home where possible. Operations spanning independent stores or concurrently writable replicas require additional coordination or conflict-resolution reasoning outside this article's scope. [S13]

## Not covered by sources

- How should a resumed former lease holder be prevented from acting after expiry?
- How can a full-row equality comparison detect history if every compared field returns to its original value?
- How should an operation commit atomically across independent authoritative stores?

## Sources

- **[S13]** Hello Interview — Dealing with Contention — <https://www.hellointerview.com/learn/system-design/patterns/dealing-with-contention> (user-supplied saved HTML, processed 2026-11-01).
