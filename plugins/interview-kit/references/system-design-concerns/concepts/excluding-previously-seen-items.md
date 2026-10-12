# Excluding Items a User Has Already Acted On

When a user works through a stream of suggestions, anything they have already acted on must be
filtered out. Re-showing it suggests the action was not recorded, or annoys the user with something
they already declined [S7].

## When it applies

- The system generates a stream of candidates for a user, and each candidate should be shown only
  once [S7].
- The record of past actions grows with every action the user takes [S7].
- The store holding those actions may lag across its replicas [S7].

## Approaches and tradeoffs

**Query the action history and check membership — graded bad** [S7]. When the feed is built, query
the user's past actions and drop any candidate that appears in them. Partitioning the history by the
acting user makes this query cheap [S7]. Challenges [S7]:

- In a system that favours availability, recent actions may not yet have reached every replica, so
  some can be missed and those items re-shown.
- For a user with a long history, the membership check gets steadily more expensive.

**Add a cache of recent actions, held on the client — graded great** [S7]. Keep the backend
membership check and add a cache of recent actions to cover replication lag. The source places that
cache **on the client** [S7]:

- A backend cache whose only job is to hold data that has not yet reached every replica would be
  expensive [S7].
- The client is part of the system. It can keep the K most recent actions and filter any suggestion
  that matches [S7].
- This depends on a stated assumption: the user uses the app on one device [S7].

The challenge that remains is long histories, where the membership check still slows as the user
acts more [S7].

**Add a probabilistic membership filter for heavy users — graded great** [S7]. The source says this
skews somewhat "over-engineered" but calls it a legitimate use [S7]. Once a user's history grows
past a size that makes caching it unwieldy or checking it slow, build and cache a Bloom filter for
that user and use it while filtering [S7]:

- **No false negatives.** An item the user did act on is never treated as unseen, so nothing is
  re-shown [S7].
- **Some false positives.** An item the user never acted on may be treated as seen, so a few
  candidates are never shown [S7].
- **The error rate is tunable** and trades against space, balancing false positives, storage and
  filtering speed [S7].

Its challenge is operating the filter cache. Each filter must be updated and recovered if the cache
fails. A filter can be rebuilt from the action history, but rebuilding at scale after a node outage
would be expensive [S7].

## Interaction with prefetching

The client-side cache also helps when a user is about to run out of suggestions. *Example:* with 200
prefetched items, at about item 150 the client asks the backend to build a new feed, fetches it when
it is ready, and filters out anything the user acted on in the meantime [S7]. See
`fan-out-on-read-vs-write.md` for how the feed itself is built.

## Failure modes

- **Re-showing an item the user already acted on**, because of replica lag [S7].
- **Membership checks that slow as history grows** [S7].
- **Items never shown**, from a probabilistic filter's false positives [S7].
- **Expensive filter rebuilds** after losing the cache that holds them [S7].

## Not covered by sources

- How to choose K for the client cache, or the history size at which the probabilistic filter takes
  over.
- What happens when the single-device assumption does not hold.
- How the probabilistic filter is updated as new actions arrive.
- Whether false positives should be corrected over time, and how.

## Sources

- **[S7]** Hello Interview — Design a Dating App Like Tinder —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/tinder>
