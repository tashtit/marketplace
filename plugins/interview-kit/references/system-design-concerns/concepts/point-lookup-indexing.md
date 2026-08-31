# Point-Lookup Indexing

Making single-record lookups by key fast as the table grows into millions or billions of rows
[S1].

## When it applies

- The dominant query is "find the one row matching this key" [S1].
- Row count is growing into the millions or billions, where an unindexed lookup becomes
  incredibly slow [S1].
- Response time for that lookup is directly user-facing [S1].

## Why it matters

Without optimization the database must check every row to find a match — a full table scan
[S1]. The source's framing of the fix is a useful mental model: an index is like a book's table
of contents or a library's card catalog, providing a way to find something without flipping
through every page. In database terms it is a separate, sorted structure of the key with a
pointer to where the full row lives in the main table, letting the database use efficient search
methods instead of scanning [S1].

The result is finding an exact match almost instantly rather than searching through millions of
rows [S1].

## Approaches and tradeoffs

**Index the lookup key.** Most relational databases use B-tree indexes by default, giving
O(log n) lookup time, which is very efficient for large datasets [S1].

**Make the lookup key the primary key.** This automatically creates an index *and* enforces
uniqueness, so you get indexing and data integrity together, with queries on that field
optimized [S1]. Where the key must be unique anyway, this collapses two requirements into one
decision [S1].

## Write-side cost of an index

S3 states the other side of the trade: while indexes improve query performance, they also increase
storage requirements and slow down writes, because each insert or update may require the index to
be updated too [S3]. It frames the number of indexes as a balance to be struck against overall
database performance, particularly when query patterns are diverse [S3].

S3 also notes the specific case where a standard index does not help: **partial string matches**,
searching a fragment rather than a whole value, which requires full-text capability instead — see
`full-text-search.md` [S3].

## Indexing for a range, not a point

S5 adds the case where the index exists to return *many* ordered rows rather than one. Its stated
problem: an index on one table allowed a set of related keys to be found quickly, but the table
holding the actual records had no index for looking up records **belonging to a set of keys** [S5].
Its fix is a secondary index whose partition key is the owning entity and whose **sort key is the
creation timestamp**, which returns that entity's records already in chronological order [S5].

Two transferable points:

- **The index is chosen from the join you are about to perform**, not from the table in isolation.
  Having an index on one side of a two-step read and not the other is what makes the second step
  the bottleneck [S5].
- **Putting the ordering attribute in the sort position makes the ordering free**, and is what lets
  a cursor seek directly to a position in it — see `cursor-pagination.md` [S5].

S5 is also explicit about what this does *not* fix: the index makes each per-entity query fast, but
a request that must issue thousands of them is still slow, which is a fan-out problem rather than
an indexing one [S5]. See `fan-out-on-read-vs-write.md`.

## Limits of indexing

Indexing fixes lookup *efficiency*, not read *volume*. The source is explicit that even with
optimized queries and indexing, a single database instance may struggle with high read
throughput, and that the remaining bottleneck is disk: a typical SSD handles around 100,000
IOPS, which is fast but finite [S1]. Modern SSDs have significantly narrowed the gap — disk I/O
is slower than memory but not prohibitively slow [S1].

When the problem is volume rather than scan cost, the next move is caching, not more indexes.
See `caching-the-read-path.md`.

## Failure modes

- **Full table scans** on queries whose key is not indexed [S1].
- **Increased response times and potential timeouts** when read volume exceeds what a single
  indexed instance can serve [S1].
- **Contention with other operations.** High read load can affect other database operations,
  such as writes [S1].
- **Write slowdown and storage growth** from maintaining too many indexes [S3].
- **Indexing one side of a two-step read and not the other**, so the second step scans [S5].
- **Treating a fan-out problem as an indexing problem**, when each individual query is already fast
  [S5].

## Not covered by sources

- When a non-B-tree index type is the better choice.
- Composite or covering indexes, and multi-column query patterns. S3 names a compound index as a
  mitigation for filtering on two columns but does not explain how one is chosen.
- How to verify an index is actually being used by a given query.
- What a secondary index costs on the write path in practice, beyond "writes are slower".

## Sources

- **[S1]** Hello Interview — Design Bit.ly —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/bitly>
- **[S3]** Hello Interview — Design Ticketmaster —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster>
- **[S5]** Hello Interview — Design Facebook's News Feed —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/fb-news-feed>
