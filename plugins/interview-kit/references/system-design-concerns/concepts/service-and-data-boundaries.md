# Service and Database Boundaries

Splitting services does not oblige you to split their data; the source argues the decision should
be made on coupling and transactional need rather than on a rule [S3].

## When it applies

You have decomposed a system into multiple services and are deciding whether each gets its own
datastore [S3].

## The source's position

The "database per service" rule is repeated often but is not hard-and-fast, and very large
companies do share databases across services where it makes sense [S3]. The source names three
conditions that together justified a shared database in its design [S3]:

- **The data is tightly coupled** — each entity's operations depend on the others (orders depend on
  items, items depend on their parent record).
- **ACID transactions are required** for the critical operation. In the source's system the claim
  path is exactly the operation that must be atomic — see `preventing-double-allocation.md` [S3].
- **Splitting would add complexity for no real benefit.**

The stated conclusion is a decision procedure, not a preference: weigh the tradeoffs and decide,
rather than parroting architectural dogma [S3].

## A second source, the same three conditions

S4 arrives at a shared database for the same reasons and adds the criterion that splits a *read*
workload off instead. Its conditions for keeping data together [S4]:

- **The transactional requirement.** When atomicity is a requirement, it helps to have the data
  colocated in an ACID store; managing a transaction across stores is possible but the complexity and
  overhead is the price [S4]. See `preventing-double-allocation.md`.
- **The coupling.** Its claim path reads inventory and writes claims in one transaction, so the two
  entities cannot be separated without reimplementing that atomicity [S4].

And the cost it names for consolidating: the scaling of the two concerns becomes partly coupled, and
you give up choosing the best store for each use case [S4].

## What justifies a split, in the same source

S4 keeps its transactional data together but states where it *would* split, and the criterion is not
transactional at all: a catalog is commonly stored separately from availability data because the two
have **different consumers and different workloads** [S4]. It says it would ideally separate them and
add a search index over the catalog, and that it colocated them only to keep the design simple [S4].

The pair of decisions inside one source is the useful part: atomicity pulls data together, while
divergent consumers and workloads push it apart. Neither is a rule about services.

## Why it matters

The transactional requirement is the load-bearing one. A design that needs a single atomic
transaction across two entities and puts them in separate databases has to reimplement atomicity
across a network — so the data boundary is downstream of the consistency requirement, not
independent of it [S3].

## Divergent query patterns as the split criterion

S5 splits a service off on the same criterion S4 gave for splitting *data*: the read path is
read-heavy and has **very different query patterns** from the write paths, so separating it out
makes sense [S5]. Read together with S4, divergent workload is the recurring reason to split and
atomicity is the recurring reason not to [S4][S5].

S5 also gives a case where colocation was chosen purely for exposition, and says so: it puts two
relations in separate tables while noting the platform's own recommended practice is a single-table
design, and that separate tables were used to keep the discussion clearer [S5]. The transferable
habit is labelling a simplification as a simplification, rather than defending it as a decision —
the same move S4 makes about its colocated catalog [S4][S5].

## Not covered by sources

- What would change the answer — at what scale or ownership boundary a split becomes worth it.
- How to migrate to separate databases later if the shared one becomes the constraint.
- How schema ownership and change management work when several services write one database.
- Whether the source's reasoning survives when only some of the three conditions hold.
- How to weigh divergent workloads against a transactional requirement when both apply to the same
  data.
- What "partly coupling the scaling" costs in practice, and when that coupling becomes the
  constraint.
- Whether a divergent query pattern justifies a separate datastore as well as a separate service.

## Sources

- **[S3]** Hello Interview — Design Ticketmaster —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster>
- **[S4]** Hello Interview — Design a Local Delivery Service like Gopuff —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/gopuff>
- **[S5]** Hello Interview — Design Facebook's News Feed —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/fb-news-feed>
