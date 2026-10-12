# Maintaining a Live Ranking

Serving a frequently refreshed, ordered top-N over scores that change as users act. Recomputing the
ranking from raw records on every read does not hold up [S6].

## When it applies

- Many users repeatedly request a ranked list, such as a leaderboard, during a live event, and the
  list should stay roughly current [S6].
- The ranking can be derived from records stored elsewhere, such as each user's successful
  submissions [S6].

## Defining the ranking first

The source defines the ranking precisely before designing for it: score by the number of distinct
problems solved, and break ties by time from the start of the event [S6]. *Distinct* matters,
because one user may submit several passing solutions to the same problem [S6].

## Approaches and tradeoffs

**Query and sort on every poll — graded bad** [S6]. On each client poll, query the stored results
for the event, group by user, and sort. Even after secondary indexing, the grouping and sorting happen
on every request [S6]. Challenges [S6]:

- Database load is high because of frequent queries, and latency grows with the number of users.
- The source's illustration is a query over a million records every 5 seconds for each polling user,
  which consumes significant compute. It calls this unsustainable at scale.

**A cached ranking refreshed on a timer — graded good** [S6]. A cache holds the current ranking and
is rebuilt from the database periodically. The source's example interval is 30 seconds. Polls read
the cache, not the database [S6]. Challenges [S6]:

- The ranking is only as fresh as the refresh interval, and clients still have to poll to see it.
- The source names a possibility of race conditions if the refresh frequency is too low.
- It still calls this a significant improvement that could suit smaller events.

**A score-ordered structure updated on write, read on poll — graded great** [S6]. When a result is
processed, the system updates both the database and an in-memory sorted structure keyed by event,
with the user as the member and their score as the value. Each poll reads the top N straight from
that structure with no expensive database query [S6]. *(Example: a Redis sorted set, updated with
`ZADD` and read with `ZRANGE … REV` [S6].)* The source gives these benefits: simpler than persistent
connections, near-real-time results, much less load on the main database, and enough scale for the
expected user base [S6].

## Paging the ranked list

The source sends the first pages of the ranking up front, for example the top 1,000, and fetches
later pages from the server as the client pages through [S6].

## Delivery cadence

Because the structure is cheap to read, the remaining question is how often clients ask. This is
covered in `propagating-changes-to-clients.md` [S6].

## Failure modes

- **Database overload during the event**, when every poll recomputes the ranking [S6].
- **Stale rankings**, bounded by the refresh interval of a periodically rebuilt cache [S6].
- **Race conditions** around the periodic rebuild [S6].
- **Counting duplicate passes as separate solves**, if the ranking does not count distinct items
  [S6].

## Not covered by sources

- What happens if the database write succeeds and the in-memory update fails, or the reverse.
- How the in-memory ranking is rebuilt after the store restarts.
- How a two-part score, such as count and then elapsed time, is encoded into one sortable value.
- What race conditions the periodic-refresh approach exposes, or how to prevent them.
- How the ranking is archived or removed after the event ends.

## Sources

- **[S6]** Hello Interview — Design a Coding Platform Like LeetCode —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/leetcode>
