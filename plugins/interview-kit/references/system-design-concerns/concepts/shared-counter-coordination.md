# Shared Counter Coordination

When a design depends on a single monotonically increasing value but runs on many instances,
that counter becomes a coordination problem [S1].

## When it applies

- A correctness property depends on every instance agreeing on the next value of a shared
  counter — the source's case is guaranteeing globally unique identifiers [S1].
- A service that was correct as a single instance is about to be scaled horizontally. The
  source frames this as a "significant issue" *introduced by* horizontal scaling, not present
  before it [S1].

## Why it matters

Horizontal scaling routes each request to an arbitrary instance [S1]. If each instance keeps
its own counter, values are reused across instances and the uniqueness guarantee — the entire
reason for choosing a counter — is lost [S1]. The counter needs a single source of truth
accessible to all instances [S1].

## Approaches and tradeoffs

**Centralized atomic counter.** Keep the counter in one shared store that all instances call.
The source's justification for its specific choice is worth keeping because it is a reasoning
pattern rather than a product recommendation: the store is single-threaded, meaning it processes
one command at a time, which eliminates race conditions; and it offers an atomic increment that
returns the new value in a single operation. Two simultaneous callers therefore always receive
different values — if one gets 1000, the other gets 1001 [S1].

The property being purchased is *atomic increment-and-return*. That, not the product name, is
what makes a store suitable here [S1].

**Cost objection and its answer.** Adding a network round-trip to every write looks expensive
but probably is not: network requests are fast, and the overhead is negligible compared to the
other operations in the request [S1].

**Batch allocation, if you do want to reduce the round-trips** [S1]:

1. Each instance requests a batch of values (the source uses 1000 at a time).
2. The store atomically increments by the batch size and returns the start of the range.
3. The instance serves values locally from its range without contacting the store.
4. When the range is exhausted, it requests another.

This reduces load on the shared store and improves performance by cutting network calls, while
still maintaining uniqueness across all instances [S1].

**Regional range partitioning.** For multi-region deployments, allocate disjoint ranges per
region (region A gets 0–1B, region B gets 1B–2B) to avoid cross-region coordination entirely.
Writes go to the local region's counter while reads are served globally from distributed caches
[S1].

## Availability of the counter

The counter becomes a dependency of every write, so it needs its own availability story:
managed failover of the shared store is the source's answer, and a single instance handling
100k+ operations per second far exceeds typical write rates, especially with batching [S1].

## Failure modes

- **Lost values on failover.** If the store fails before replicating the latest counter, some
  values are lost. This is acceptable *only because the requirement is uniqueness, not
  continuity* — a distinction worth making explicitly for any counter-based design [S1].
- **Duplicate identifiers surviving into the database**, for which the database's UNIQUE
  constraint is the ultimate safety net [S1]. See `unique-identifier-generation.md`.
- **Gaps in the sequence from unexhausted batches**, implied by batch allocation: an instance
  that dies mid-batch takes its remaining range with it [S1].

## Not covered by sources

- How to size the batch (1000 is given as an example, not derived).
- What happens to in-flight batches when an instance is deployed or crashes.
- How regional ranges are re-allocated when a region's range is exhausted or a region is added.
- Whether alternatives to a centralized counter (e.g. coordination-free schemes) apply.

## Sources

- **[S1]** Hello Interview — Design Bit.ly —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/bitly>
