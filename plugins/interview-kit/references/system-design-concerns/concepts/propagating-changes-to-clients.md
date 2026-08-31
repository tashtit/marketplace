# Propagating Changes to Clients

Getting a change made in one place onto every other client that holds a copy [S2].

## When it applies

- The same state exists locally on multiple clients and authoritatively on a server, so changes
  have to travel in both directions [S2].
- Clients need to learn about remote changes they did not make [S2].

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

## Sources

- **[S2]** Hello Interview — Design a File Storage Service Like Dropbox —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/dropbox>
- **[S3]** Hello Interview — Design Ticketmaster —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster>
