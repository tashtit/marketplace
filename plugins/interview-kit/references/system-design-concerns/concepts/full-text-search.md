# Full-Text Search on a Relational Store

Searching free text by wildcard forces a full table scan; escaping that costs either a
specialized index inside the database or a separate search-optimized store that must then be
kept in sync [S3].

## When it applies

- Users search records by keywords appearing anywhere in a name, description, or similar text
  field [S3].
- The records live in a relational database chosen for other reasons — the source's system needs
  ACID transactions elsewhere, so the search requirement arrives on top of an existing store
  [S3].
- There is a latency target on search that the naive query will not meet [S3].

## Why the naive query fails

A leading-wildcard pattern match requires a full table scan, because no ordinary index can be
used to satisfy it — and this gets worse as the record count grows [S3]. The source's example
query is a pattern match on both name and description joined by `OR` [S3].

## Approaches and tradeoffs

**Conventional indexes plus query tuning.** Index the columns that search queries actually filter
on — the source names entity name, date, performer name, and location [S3]. Alongside that:
inspect execution plans, avoid selecting all columns, bound result sets with a limit, and prefer a
union over an `OR` when combining conditions [S3].

Limits the source states [S3]:

- **Standard indexes are weak for partial string matches** — searching a fragment rather than the
  whole value — which is what pushes you toward full-text capability.
- Indexes **increase storage and slow writes**, since every insert or update may have to update
  an index.
- Finding the right number of indexes against diverse query patterns is itself a balancing act.

**Full-text indexes inside the database.** Mature relational engines have their own full-text
search facilities, which make searching for a specific word far faster than a wildcard scan [S3].
The source is careful that these are not the same engine as a dedicated search product — they do
not use the same underlying library [S3]. Costs: extra storage, potentially slower to query than
a standard index, and harder to maintain because they need special handling both in queries and in
database upkeep [S3].

**A dedicated full-text search engine.** A search engine built on **inverted indexes** — mapping
each unique word to the records containing it — is what makes it efficient at locating text, and
suits complex queries and high traffic volume [S3]. It also buys **fuzzy search**: tolerance for
typos and spelling variants, which the source says would be very difficult to achieve with SQL
alone [S3].

The costs are integration costs, not query costs [S3]:

- The search index must be **kept synchronized** with the system of record. The source's mechanism
  is change data capture — capturing inserts, updates and deletes in the database and replicating
  them into the search index for real-time or near-real-time sync [S3].
- Synchronization is complex and needs a reliable mechanism to keep the two consistent [S3].
- Operating the search cluster adds infrastructure complexity and cost [S3].

## How to decide

The source escalates in order — index and tune, then in-database full-text, then a separate
engine — which frames the separate engine as what you adopt when you need capabilities the
database cannot offer (notably fuzzy matching) rather than as the default [S3]. Note also that the
source treats reaching for a search-optimized store as *essential* knowledge at senior level for
this class of problem; see `level-expectations.md` [S3].

## Failure modes

- **Full table scans** on wildcard text queries [S3].
- **Missed matches on partial words** when relying on standard indexes [S3].
- **Write slowdown and storage growth** from over-indexing [S3].
- **Search index drift** from the system of record when synchronization is unreliable [S3].

## Not covered by sources

- How to detect and repair drift between the search index and the system of record.
- What to serve while the search engine is unavailable.
- How to tune relevance or ranking of results.
- Whether full-text indexes inside the database can carry fuzzy matching.
- The write-path cost of change data capture on the source database.

## Sources

- **[S3]** Hello Interview — Design Ticketmaster —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster>
