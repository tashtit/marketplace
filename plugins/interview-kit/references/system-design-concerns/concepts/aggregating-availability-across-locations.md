# Aggregating Availability Across Locations

When a resource is physically distributed and the caller cares only about the total reachable to
them, the answer is a union computed per request rather than a stored quantity [S4].

## When it applies

- The same logical thing exists in several physical places, and the quantity a given caller can
  have is the sum across the subset reachable from them [S4].
- The reachable subset differs per caller, so no single stored total is correct for everyone. S4's
  requirement states availability as "the union of all inventory nearby" [S4].
- The aggregate is on a latency-sensitive read path — S4 targets end-to-end under **100ms**,
  explicitly so the result can back use cases like search [S4].

## The type-versus-instance distinction

S4 makes the modeling move that the whole aggregate depends on: separate the **type** of thing from
the **physical instance** of it, likening the pair to a class and an instance in object-oriented
programming [S4]. Callers browsing a catalog care about the type; the system must track where the
physical instances actually are [S4]. The instance entity is therefore defined as *a physical item
at a specific location* [S4].

Once that split exists, availability is a derived quantity: sum the instances to get the amount
available to a specific caller for a specific type [S4]. Neither entity stores it.

S4 also states the ordering heuristic for finding entities at all: start with the most concrete
physical or business nouns and work up to the more abstract ones, which is what keeps you from
missing an entity [S4]. And it notes the reason to get this right early — entities are the anchor
points of a REST API, so the resources follow from them [S4].

See `entity-granularity.md` for the neighbouring decision of when a concern deserves its own entity
at all.

## The two-step read

S4's read path resolves location first, then quantity [S4]:

1. **Narrow to the reachable locations.** Because every instance lives at a location, resolving
   locations first is a shortcut that avoids examining every instance in the system [S4]. See
   `proximity-candidate-filtering.md`.
2. **Query instances at those locations and union the result** [S4].

The transferable structure is that the location dimension is the selective one, so it goes first —
and S4 states the consequence for both halves: each step must be reasonably fast because the
end-to-end budget is what it is [S4].

## Pass the caller's location to the write path too

S4 sends location to *both* the availability call and the order call, and gives the reason: before
an order is processed, the system must confirm the resource is close enough to the caller to be
delivered inside the promised window [S4]. The read path's answer is not a durable authorization —
the constraint is re-checked when the claim is made.

## Aggregate cheaply by co-locating the descriptive data

S4 joins the instance table against the type table to attach names and descriptions before
returning the quantity, and is explicit that it keeps both in one database to make the work easier
[S4]. It is equally explicit that this is a simplification: in many systems the catalog is stored
separately from the availability data because the two have **different consumers and different
workloads**, and it would ideally be separated, with a search index added over the catalog [S4].

The transferable criterion is that consumer and workload divergence is what splits a catalog from
its inventory — not the fact that they are different nouns. See `full-text-search.md` for the
search index and `service-and-data-boundaries.md` for the general split decision.

## Pagination on the aggregate

S4 includes pagination in its availability API, for the stated reason of not overwhelming the
client with more data than it needs [S4].

## Failure modes

- **Storing a global total** when the reachable subset differs per caller, so the number is wrong
  for everybody [S4].
- **Scanning all instances** because the location dimension was not used to narrow first [S4].
- **Treating an availability read as a promise**, without re-checking reachability at claim time
  [S4].

## Not covered by sources

- Whether an aggregate should ever be materialized per region rather than computed per request.
- How to keep the union correct when an instance moves between locations.
- What the caller sees when the reachable set spans locations with different delivery windows.
- How to reconcile a read that aggregated across locations with a claim that must be atomic in one.
- How the type-versus-instance split behaves for fungible resources with no individual identity.

## Sources

- **[S4]** Hello Interview — Design a Local Delivery Service like Gopuff —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/gopuff>
