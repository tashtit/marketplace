# Querying a Relationship From Both Sides

When a many-to-many relationship is stored inside one side's record, the query from the other
side has no efficient path [S2].

## When it applies

- A relationship is embedded as a list on one entity — the members of a group, the users a record
  is shared with — and it reads well in that direction [S2].
- A real query arrives from the other direction: "give me every record that lists *me*" [S2].

## Why it matters

The embedded list is only indexable from the side that owns it. The source's case: fetching a
user's own records is an indexed lookup on the owner field, but fetching records shared *with*
them requires scanning the shared-with list of every record [S2]. The relationship is symmetric;
the storage is not.

## Approaches and tradeoffs

**Embed the list on one side.** Simple and effective for the direction it was written for, and
the source calls it a good start [S2]. The reverse query is the defect [S2].

**Add a cache of the inverse mapping.** Keep the embedded list and additionally maintain a
mapping from the other entity to its records, so the reverse query becomes a key-value lookup
[S2].

- **The cost is keeping two representations in sync** [S2].
- The source's own mitigation weakens the case for the approach: it suggests holding the inverse
  mapping in the same database and updating both inside a transaction [S2] — at which point it is
  a second table, not a cache.

**Normalize into a join table.** Create a table keyed by the pair, so the reverse query selects
the rows for that entity, and the embedded list can be dropped entirely — removing the
synchronization problem rather than managing it [S2].

- The source's schema: a composite primary key over both ids, with the querying side as the
  partition key and the other as the sort key in a wide-column store, or a composite primary key
  in a relational one [S2].
- **The tradeoff is a slightly less efficient query** — an index lookup rather than a simple
  key-value get — and the source's judgment is that this is likely worth it to eliminate the sync
  requirement [S2].

## How to decide

The decision axis the source uses is **which cost you would rather carry**: a marginally slower
query, or the standing obligation to keep two copies of one relationship consistent [S2].

## A secondary index instead of a second copy

S5 reaches the join-table shape directly and then solves the reverse direction with an index rather
than a second representation [S5]. Its schema is the relation itself: the acting side as the
partition key and the target side as the sort key, with a **secondary index carrying the reverse
pair** — target as partition key, actor as sort key [S5].

The three queries this makes available are the transferable part, because they cover the whole
surface of a many-to-many relationship [S5]:

| Question | Access |
| --- | --- |
| Does A relate to B? | Point lookup on both keys [S5] |
| Everything A relates to | Range query on the partition key [S5] |
| Everything that relates to A | Range query on the secondary index's partition key [S5] |

Note this is the same move as "add a cache of the inverse mapping" above, minus the sync problem
S2 objected to: the store maintains the reverse structure, so there is no second write to keep
consistent [S2][S5].

## When the relationship needs a graph store

S5 models a many-to-many relationship explicitly as a graph and then argues against using a graph
database for it, giving a criterion rather than a preference [S5].

- **What graph stores are for:** traversals and comprehensions that step between nodes — reaching
  friends-of-friends, or building an embedding for a recommendation system [S5].
- **What does not need one:** a relationship queried only one or two hops out, which a plain
  key-value store can model directly [S5].
- **The cost it names is operational, not functional:** choosing the purpose-built store invites
  the question of how you scale it [S5]. Where the simple store suffices, that question never
  arises.

## Marking a relationship with per-edge policy

An edge can carry more than its endpoints. S5 stores a flag on the relationship row indicating
that this particular edge is excluded from precomputation, which is what lets a background worker
skip it [S5]. The transferable point is that the relationship table is the natural home for policy
that applies to *one* pairing rather than to either entity — see `fan-out-on-read-vs-write.md`.

## Failure modes

- **Scanning every record to answer the reverse query** [S2].
- **Divergence between the embedded list and its inverse copy** when the two are updated
  separately [S2].
- **Reaching for a graph store for a one-hop relationship**, taking on its scaling question for no
  traversal benefit [S5].

## Not covered by sources

- What the reverse-lookup cost actually is at scale, beyond "slow" versus "slightly less
  efficient".
- Whether the join table needs an index in the other direction as well, for the original query.
- How to migrate from an embedded list to a join table once records already exist.
- What the secondary index costs on the write path, given that every relationship write now
  maintains two structures.
- Where the hop count is that justifies a purpose-built graph store.
- Whether a range query over a very large relationship set needs pagination of its own.

## Sources

- **[S2]** Hello Interview — Design a File Storage Service Like Dropbox —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/dropbox>
- **[S5]** Hello Interview — Design Facebook's News Feed —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/fb-news-feed>
