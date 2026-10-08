# Excluding Previously Processed Candidates

A candidate generator should account for actions already taken so the client does not present the same candidate again [S6].

## Approaches and tradeoffs

Querying an actor's past actions and filtering candidates by a membership check is straightforward when the history is partitioned by actor, but the returned history and membership work grow as that actor's history grows [S6]. If action writes have not reached every replica, a feed built from a lagging replica can still repeat a recently processed candidate [S6].

The source proposes a client-side cache of the most recent K actions to filter out those recent repeats while the backend checks older persisted history [S6]. Its premise is that the actor uses only one device; a server-side short-term cache merely to cover replication lag would be costly [S6]. The client can request more candidates before exhausting a prefetched list and filter out candidates it has processed in the meantime [S6].

## Not covered by sources

- What changes when the actor uses multiple devices?
- How large should K be, and how is a long history checked without returning all its identifiers?
- How are repeats prevented when both the client cache and the backend history are unavailable?

## Sources

- **[S6]** Hello Interview — Design a Dating App Like Tinder —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/tinder>
