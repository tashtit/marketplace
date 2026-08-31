# Preventing Double Allocation of a Finite Resource

When a fixed inventory item can be claimed by only one user, and many users try at once, the
system must guarantee exactly one winner while still releasing abandoned claims promptly [S3].

## When it applies

- Inventory is finite and individually identified, so two users paying for the same item is a
  correctness failure, not a degraded experience [S3].
- The claim is not instantaneous: the user needs time to complete a multi-step flow (entering
  payment details) between selecting the item and paying for it [S3].
- Contention is high — the source's scale case is millions of users converging on one event's
  inventory [S3].

## Why the naive flow is unacceptable

Checking availability only at payment time technically works, but the user fills out a payment
form and *then* discovers the item is gone [S3]. The source is blunt that this is the defect
driving the whole design: nobody wants to spend five minutes on a payment form only to lose the
item to someone who typed their card number faster [S3].

So the requirement is not just "no double allocation" — it is **hold the item during checkout,
and release it if checkout is abandoned** [S3]. Three outcomes must be handled: the user
completes and the item becomes sold, the user abandons and the item returns to the pool, and a
concurrent user is correctly refused [S3].

## What the store has to provide

The requirement constrains the datastore, but only weakly: it must support transactions, and the
source states that any engine with ACID properties is a fine choice — the named examples span a
relational and a non-relational store [S3]. The specific engine is not the interesting decision;
the transactional guarantee is.

What it does require beyond "supports transactions" is **proper isolation levels together with
either row-level locking or optimistic concurrency control** to fully prevent double allocation
[S3]. This is the guarantee the rest of the design leans on — see *Defense in depth* below.

## Approaches and tradeoffs

**Long-running database locks.** Take a row lock inside a transaction that stays open for the
duration of checkout — the source names `SELECT FOR UPDATE` as the typical mechanism, where
other transactions attempting the same row block until the lock releases [S3]. The source
presents this as the **bad** option, with specific reasoning [S3]:

- Database locks are designed for short, near-instant transactions; holding one for minutes
  strains database resources and raises the risk of lock contention and deadlocks [S3].
- A lock timeout exists but is not graceful for a user-facing flow: the user sees an error rather
  than being queued [S3].
- It scales poorly under load — prolonged locks increase wait times and become a bottleneck [S3].
- Crashes and network failures can leave locks in an uncertain state, and releasing the hold
  otherwise depends on the user's subsequent actions or a session timeout, risking items locked
  indefinitely [S3].

**Explicit status field plus expiration timestamp, swept by a background job.** Model the item as
available / reserved / sold, recording the reservation time; a periodic job finds reserved rows
past the lock duration and returns them to available [S3]. Better, but the sweep is the weakness
[S3]:

- **Delay in releasing.** There is inherent lag between expiry and the job running, so items sit
  unavailable after they should have been released — worst exactly when demand is highest [S3].
- **Reliability.** If the job fails or lags, the booking process is disrupted [S3].

**Implicit status — derive availability rather than storing it.** Recognize that "claimable" is
the combination of two attributes: available, *or* reserved with an expired reservation [S3]. Use
short transactions that check that condition and set reserved with a fresh expiry, instead of
holding a lock open [S3].

The source's transaction, in outline: begin; check the item is available or reserved-but-expired;
set reserved with expiry now + the hold duration; commit [S3]. This guarantees a single winner
**and** that expired reservations become claimable by others [S3].

Costs the source names [S3]:

- Reads get slightly slower by filtering on two values, partly recoverable with a compound index
  or materialized views.
- The table is less legible to other consumers, since some rows read as reserved but are actually
  expired. A sweep job can still tidy this — **with the crucial difference that a delayed sweep no
  longer changes system behavior** [S3].

That last point is the transferable one: the same cleanup job goes from load-bearing to cosmetic
purely by moving expiry from stored state to a read-time predicate.

**A distributed lock with a TTL in an external store.** Acquire a lock keyed by the item id with a
time-to-live; release it explicitly on success, or let it expire automatically on abandonment
[S3]. The source's stated reason for reaching outside a strongly consistent database is narrow and
worth keeping: the database has no native row-level TTL, so automatic expiry would have to be
reimplemented as application logic, whereas an in-memory store provides key expiration natively
and acquires and releases very fast under high concurrency [S3].

- **The acquire must be atomic.** A single set-if-not-exists-with-expiry command means only one
  client can win, so there is no race in acquisition [S3].
- **Store the claimant's identity as the value**, so that on confirmation you can verify the
  confirming user is the one who holds the reservation [S3].
- **Multi-item claims acquire sequentially and roll back on partial failure** — release the locks
  already held if any acquisition fails; a server-side script can make multi-lock acquisition
  atomic when the keys live on the same node [S3].
- It simplifies the durable model: the item table returns to just available and sold, with holds
  living entirely in the lock store [S3].

## Holding state outside the database moves a problem onto the read path

Once reservations live in the lock store, the read that renders availability no longer sees them
[S3]. The source works through the trap and the fix:

- **A plain set of locked item ids does not work**, because set members do not expire when the
  individual lock keys do — every abandoned checkout leaves a ghost entry that shows its item as
  held forever [S3].
- **A sorted set scored by expiry time does**: the read counts only entries scored in the future,
  so expired holds vanish from the display on their own, and stale members can be trimmed lazily
  whenever the structure is touched [S3]. The cost is an extra round-trip on the read path [S3].
- **Alternatively, write the reserved status through to the database** on acquisition, treating
  the lock store's TTL as the source of truth for expiration and sweeping stale rows periodically
  [S3].

## Claiming several items at once

When one claim covers multiple items, the atomicity requirement widens from one row to a set. S4
works this case directly: check that every item is in stock, and if any is not, the whole
transaction fails; otherwise record the claim and mark all of the items claimed, in a single
transaction [S4].

S4 states the user-facing cost of that choice plainly: if any one item becomes unavailable the
entire claim fails, which calls for a meaningful error message — but it argues this is preferable to
partially succeeding, because a partial result may be worthless to the requester [S4]. Its example
is a device ordered together with its battery [S4]. The transferable point is that all-or-nothing is
sometimes the *correct* semantic rather than a limitation, and whether it is depends on whether the
items are useful separately.

S4 also names the failure mode that appears only with multi-item claims under lock-based approaches:
**deadlock between overlapping claims** — two requesters each holding one of the two items the other
needs, so neither can proceed [S4]. Its stated mitigation for the sequential-acquire shape is the
same as S3's: you must be able to address this failure mode if you take that route [S4].

## Splitting the claim across two stores adds recovery work

S4 evaluates keeping the claim record and the inventory record in **separate** datastores,
coordinated by a distributed lock: lock the affected inventory, create the claim record, decrement
inventory, release [S4]. It credits the upside — each concern can use the datastore that suits it,
a key-value store for inventory and a relational database for claims [S4] — and then names the
failure that has no cheap fix: if the service crashes after the claim is recorded but before
inventory is decremented, a later requester can be promised inventory already committed to someone
else, so you must sweep for these partial states and reverse them [S4].

The generalizable cost is that a claim spanning two stores converts an atomicity requirement into a
reconciliation job. S4's framing of when to avoid that: when atomicity is a requirement, it helps to
have the data colocated in an ACID datastore — managing transactions across multiple stores is
possible, but the added complexity and overhead is the thing being bought [S4]. See
`service-and-data-boundaries.md`.

S4's own consolidation is a single transaction at isolation level **SERIALIZABLE**, which it names
as what makes the whole claim atomic so that one of two concurrent requesters is rejected [S4]. It
names the cost of consolidating too: the scaling of the two concerns becomes partly coupled, and you
give up choosing the best datastore for each [S4].

## Disagreements between sources

**Where the hold should live.** S3 recommends an external lock store with a native TTL as its
preferred mechanism, accepting the extra dependency on the read path, and grades long-running
database locks as its bad option [S3]. S4 grades the arrangement of two datastores coordinated by a
distributed lock as merely *good* — citing crash recovery and deadlock — and grades a single
serializable database transaction as its *great* option [S4].

Both sources state a scope that bears on the difference: S3's claim must survive a multi-minute
payment flow [S3], while S4 declares payment handling out of scope entirely [S4], so the transaction
it commits is short. Neither source addresses the other's configuration, and this library does not
adjudicate between them.

## Defense in depth: the lock is an optimization, not the guarantee

The source's failure analysis is the sharpest reasoning in this concept. If the lock store goes
down, the user experience degrades — but **there is still never a double allocation**, because the
database enforces it with optimistic concurrency control or row-level locking [S3]. The
consequence is only that a user can be refused after entering payment details [S3].

And the source ranks that failure explicitly against the alternative: being refused occasionally
is a better outcome than the sweep-job design's failure mode, where a stalled job makes *all*
inventory appear unavailable [S3]. Compare failure modes, not just happy paths.

## The hold can expire mid-payment

If the TTL lapses while payment is in flight, another user can acquire the hold before the first
user's payment lands [S3]. The source's handling [S3]:

- The final database transaction fails for one of them, because optimistic concurrency lets only
  one write succeed — so correctness holds.
- The losing payment is refunded automatically.
- Set the TTL generously to make this rare, and better still, extend the hold when payment is
  initiated.

## Failure modes

- **Two users paying for one item**, when the claim is checked only at payment time [S3].
- **Items locked indefinitely** after a crash or an abandoned session, under long-running locks
  [S3].
- **Deadlock and lock contention** from holding database locks for minutes [S3].
- **Items unavailable after their hold expired**, when a sweep job is late or failed [S3].
- **All inventory appearing unavailable** when the sweep job fails outright [S3].
- **Ghost holds displayed forever**, when the read-path structure has no expiry of its own [S3].
- **A user refused after entering payment details**, when the hold store is unavailable or the
  hold expired mid-payment [S3].
- **Inventory promised twice after a partial crash**, when the claim record and the inventory record
  live in different datastores [S4].
- **Deadlock between overlapping multi-item claims**, each holding an item the other needs [S4].
- **A whole multi-item claim failing on one unavailable item**, which is correct but needs a
  meaningful error [S4].

## How to decide

- **Do not hold a database transaction open for a user-facing step.** The duration mismatch is
  the whole problem [S3].
- **Prefer deriving expiry at read time over storing it**, when you want a cleanup job whose
  delay is harmless [S3].
- **Reach for an external lock store when** you need automatic expiration the database cannot
  provide natively, and can accept an extra dependency on the read path [S3].
- **Keep the database-level guarantee regardless of which hold mechanism you choose** — the hold
  improves experience; concurrency control provides correctness [S3].
- **Colocate the data in one ACID store when atomicity is the requirement**, rather than
  coordinating a transaction across stores for the sake of picking the ideal store for each [S4].
- **Decide whether a partial claim is worth anything.** If the items are only useful together,
  all-or-nothing is the correct semantic rather than a limitation [S4].

## Not covered by sources

- How to choose the hold duration, beyond the ten-minute example.
- What happens if the lock store loses its keys entirely (rather than becoming unavailable), and
  whether holds are reconstructed.
- How to extend a hold safely without letting a client extend indefinitely.
- Whether the refund path itself can fail, and what reconciles it if it does.
- How the sorted-set read structure is kept correct if a lock is released early rather than
  expiring.
- What SERIALIZABLE isolation costs in throughput, or how often it forces retries under contention.
- How to order acquisitions to avoid deadlock on multi-item claims; both sources name the failure
  without giving an ordering rule.
- Whether a partially failed multi-item claim should ever be offered as a partial result.

## Sources

- **[S3]** Hello Interview — Design Ticketmaster —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster>
- **[S4]** Hello Interview — Design a Local Delivery Service like Gopuff —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/gopuff>
