# Cursor Pagination Over an Ordered Result

When a client walks through a long ordered result a page at a time, the position can be carried as
a value from the ordering itself rather than as an offset [S5].

## When it applies

- The result set is ordered by a monotonic attribute, and the client consumes it in that order.
  S5's case is reverse chronological — newest first — so a caller paging forward is always moving
  toward older entries [S5].
- The client needs an "infinite scroll"-like experience, which means the system must know what has
  already been seen and be able to pull the next set quickly [S5].

## The method

S5's observation is that "what the caller has already seen" **can be described concisely**: a
single value marking the boundary of what they have consumed [S5]. Because consumption follows the
sort order, that one value is enough to locate the resumption point [S5].

- **The cursor is the boundary value, not a page number.** S5 uses the timestamp of the oldest
  entry looked at so far, and each page returns N entries older than it [S5].
- **The API carries page size and cursor, and returns the items plus the next cursor** [S5], so
  the client never computes the position itself.
- **The cursor is optional on the first call** [S5] — its absence means "from the beginning".

## Why the index has to agree with the cursor

The cursor is only cheap if the store can seek to it. S5's read path works because the index it
already had — records sorted by the creating entity, with the ordering attribute as the sort key —
lets it return only entries beyond the cursor directly [S5]. See `point-lookup-indexing.md`.

The transferable form: a cursor over an attribute that is not the sort key of an available index
is an offset scan wearing a cursor's clothing.

## Deep pagination is usually not a requirement

S5 makes an unusually direct product claim, and it is what licenses a bounded precomputed result:
callers asking to page dozens of pages deep is a fair question, but **most systems simply do not
support it**, because real users are not doing it [S5]. Its own comparison is that few people page
many screens into a search engine's results [S5].

The consequence for the design is that the deep tail can be served by a slower fallback path
rather than by the optimized one — see `fan-out-on-read-vs-write.md` for the bounded precomputed
result this permits, and the fallback to the underlying tables when a caller exhausts it [S5].

## Failure modes

- **Paginating on an attribute with no supporting index**, turning each page into a scan [S5].
- **Sizing the fast path for depths real callers never reach**, paying for a tail that does not
  exist [S5].
- **A caller reaching the end of a bounded precomputed result** with no fallback path defined
  [S5].

## Not covered by sources

- What happens when new entries arrive above the cursor while a client is paging.
- Whether ties on the cursor attribute can drop or duplicate an entry, and how to break them.
- How to page an ordering that is not monotonic, or one that can be re-sorted.
- Whether the cursor should be opaque to the client rather than a readable value.
- How to detect that a caller has crossed from the fast path onto the fallback.

## Sources

- **[S5]** Hello Interview — Design Facebook's News Feed —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/fb-news-feed>
