# Proximity Candidate Filtering

When the accurate way to decide whether something is "near enough" is expensive, filter the
candidate set with a cheap geometric approximation first and score only the survivors [S4].

## When it applies

- A request must be matched against a set of fixed locations, and the matching predicate is a
  real-world cost — travel time rather than distance [S4].
- The requirement is stated in the expensive unit. S4's functional requirement is delivery within
  **1 hour of drive time**, which straight-line distance does not measure [S4].
- The accurate answer comes from an external service, so each evaluation carries a network call
  [S4].

## Why straight-line distance is not the answer

Geometric distance is a proxy that fails in ways the domain cares about. S4 names them: a location
may be close in miles but far in drive time when a river or a border sits between, and traffic and
road conditions shift travel time independently of distance [S4]. Its stated conclusion is that a
simple threshold query gives you candidates "as the crow flies," which does not satisfy a
requirement expressed in drive time [S4].

S4 also notes the arithmetic itself has grades: Euclidean distance is the basic version, and the
Haversine formula is the more sophisticated one because it accounts for the curvature of the Earth
[S4]. Neither closes the gap to travel time. A second failure S4 names for the naive threshold is
that it ignores having several locations within one city [S4].

## Why evaluating every candidate is also not the answer

The opposite extreme — call the travel-time estimator once per known location and keep the ones
under the bound — is correct but wasteful. S4's objection is that it makes far too many queries to
the external service, and that most of the locations being evaluated are not close enough to ever
plausibly qualify [S4]. The cost is paid on candidates whose answer was never in doubt.

## The two-stage shape

S4's preferred solution composes the two rejected ones [S4]:

1. **Prune with the cheap predicate.** Take a fixed radius chosen as the most optimistic value the
   expensive predicate could possibly return — S4 uses 60 miles as the furthest one could drive in
   an hour — and keep only candidates inside it [S4].
2. **Score the survivors with the expensive predicate.** Pass the restricted candidate set to the
   external estimator to produce the final answer [S4].

The load-bearing detail is *how the radius is chosen*. Because it is the optimistic bound on the
accurate predicate, the prune cannot discard a candidate that would have qualified — it is a
filter that only removes certain negatives. A radius chosen for convenience rather than as a bound
would silently drop valid results.

## Caching the slow-changing candidate set

The set being filtered is reference data, and S4 exploits that: because the locations rarely change
— they are buildings — the service syncs the table into its own memory periodically, on the order
of every 5 minutes [S4]. This appears in both the rejected and the accepted solution, so the
in-memory sync is independent of the two-stage structure [S4].

The transferable point is that a slow-changing dimension on a hot read path does not need to be
queried per request; the acceptable staleness window is set by how fast the data actually changes.

## Interaction with the rest of the read path

Resolving the nearby set is only the first half of the read; see
`aggregating-availability-across-locations.md` for what happens once the candidates are known, and
`delegating-external-operations.md` for the external-dependency framing.

## Failure modes

- **Answering a drive-time requirement with a distance query**, so results are wrong wherever
  geography and roads diverge [S4].
- **Exhausting an external service's capacity** by evaluating candidates that could never qualify
  [S4].
- **Ignoring density**, treating several locations in one city as interchangeable [S4].

## Not covered by sources

- How to pick the prune radius when the expensive predicate has no clean optimistic bound.
- What to do when the external estimator is slow, unavailable, or rate-limited at request time.
- Whether the estimator's results can themselves be cached, and keyed on what.
- How to keep the prune correct when conditions change the optimistic bound (a highway closure).
- How the periodic in-memory sync behaves while it is refreshing, or when it fails.
- Whether spatial indexing structures would replace the radius prune; S4 names neither.

## Sources

- **[S4]** Hello Interview — Design a Local Delivery Service like Gopuff —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/gopuff>
