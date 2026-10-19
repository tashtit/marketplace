# Propagating Changes to Clients

Getting a change made in one place onto every other client that holds a copy [S2].

## When it applies

- The same state exists locally on multiple clients and authoritatively on a server, so changes
  have to travel in both directions [S2].
- Clients need to learn about remote changes they did not make [S2].
- A client is waiting for server-side state that changes over time, such as a live ranking or the
  result of work it submitted [S6].

## The two directions are different problems

**Local to remote.** A client-side agent watches for local changes using OS file system event
APIs, queues what changed, and sends it with updated metadata [S2]. The remote copy is treated
as the source of truth, and the source's reason for pushing changes promptly is downstream: other
clients cannot learn there is something to pull until the authoritative copy reflects it [S2].

**Remote to local.** Each client has to find out that something changed. This is the direction
that needs a delivery mechanism [S2].

## Approaches and tradeoffs

**Polling.** The client periodically asks whether anything changed since its last sync, and the
server queries for records the client watches whose update timestamp is newer [S2]. Simple, but
slow to detect changes and wasteful of bandwidth when nothing changed [S2].

**Server push over a persistent connection.** The server holds an open connection and pushes
notifications as changes occur — real-time, but more complex [S2].

**Hybrid: push with polling as a safety net.** The source's choice, and the reasoning generalizes
beyond this system [S2]:

- One persistent connection **per device or session, not per record** — the connection carries
  change notifications for everything the user can see [S2].
- Push gives near-instant propagation [S2].
- Persistent connections drop and messages get missed, so the client also polls on a slower
  cadence — the source's example is every few minutes — to catch anything it missed [S2].

The polling fallback is what makes the guarantee eventual consistency rather than best-effort:
push is the fast path, polling is the one that cannot silently lose an event [S2].

**Unidirectional server-sent events.** S3 names a one-directional server-to-client channel as
the appropriate mechanism when only the server has anything to say — the client needs no send
capability, so the simpler protocol is preferred over a bidirectional one [S3]. Its use case is
keeping a shared view of contended state current without the user refreshing [S3]. It reiterates
the choice for pushing queue-position updates: unidirectional is simpler, bidirectional works if
you anticipate needing two-way traffic [S3].

## When polling is enough

S6 gives the case for polling alone. Many candidates propose persistent connections to deliver a
live ranking. The source says this is not wrong, but it is overkill given a modest number of users
and an acceptable 5-second delay [S6]. Plain polling every few seconds, against a structure that is
cheap to read, balances freshness against simplicity and can be scaled up later if needed [S6]. See
`live-ranking.md`.

It reaches the same verdict for a client waiting on submitted work. A status endpoint polled every
second is enough. A persistent connection would work but adds complexity that a one-second interval
does not justify [S6]. See `asynchronous-work-queue.md`.

**Polling cadence is a tunable, not a fixed choice.** If the interval turns out to be too frequent,
it can be changed. S6 suggests progressive polling: faster when freshness matters most, for example
every 2 seconds in the last minutes of an event, and slower otherwise, for example every 10 seconds
[S6].

S6 describes the staff-level skill here as knowing the more complex option and being clear about why
it is likely overkill for this system [S6]. Read with S2, the conditions differ, not the reasoning.
S2 needs changes on many devices to converge and adds push for near-instant propagation [S2]. S6
states a tolerable delay and a small user base, so polling clears its bar [S6].

## When faster push stops helping

S3 supplies the limit of this whole approach. Where contention is extreme, pushing changes
faster makes the interface churn — the view fills up almost instantly and the experience becomes
disorienting rather than merely stale [S3]. At that point the answer is not a better delivery
mechanism but restricting who enters the flow; see `admission-control.md` [S3]. The source
frames this explicitly as a case where the better solution is the less technically sophisticated
one [S3].

## Designing the change query

The pull side is a single endpoint returning changes since a caller-supplied timestamp, where
each event carries the record id, the kind of change (created, updated, deleted), and the updated
metadata [S2]. Passing the timestamp is what lets the client fetch only what it missed [S2].

This endpoint serves both mechanisms — it is the polling path and the recovery path after a
dropped connection.

## Conflict resolution

When two clients edit the same record, the source resolves with **last write wins**: the most
recent edit is the one saved [S2]. It notes, while placing versioning out of scope, that one
would typically not overwrite the only copy — instead write a new copy (or just the new chunks)
and advance a version number and pointer on the metadata [S2].

## Efficiency of the transfer itself

Sync reuses chunking: when a record changes, transfer only the chunks that changed rather than
the whole payload [S2]. See `large-file-transfer.md`, including why fixed-size chunk boundaries
undermine this.

## Failure modes

- **A dropped persistent connection silently missing change events**, which is the specific
  failure the polling fallback exists to cover [S2].
- **Slow detection and wasted bandwidth** under polling alone [S2].
- **A lost edit under last-write-wins**, implied by the source's note that you would not
  overwrite the only copy [S2].
- **An interface that churns faster than a user can act on it**, when push rate outpaces
  comprehension [S3].

## Not covered by sources

- How the client's "last sync" timestamp is maintained, or what happens if it is wrong or lost.
- Whether change events are ordered, or what the client does if it applies them out of order.
- How "most recent" is determined for last-write-wins — whose clock decides.
- How many persistent connections a server can hold, or how the push side scales.
- How a client that has been offline for a long time catches up.
- At what contention level push stops being sufficient — S3 gives the symptom, not a threshold.
- At what user count or delay tolerance S6's case for polling alone stops holding.
- How a progressive polling schedule is chosen or switched at run time.

## Sources

- **[S2]** Hello Interview — Design a File Storage Service Like Dropbox —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/dropbox>
- **[S3]** Hello Interview — Design Ticketmaster —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster>
- **[S6]** Hello Interview — Design a Coding Platform Like LeetCode —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/leetcode>
