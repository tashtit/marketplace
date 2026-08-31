# Redundancy for Availability

Surviving the loss of a stateful dependency, when availability is stated as a requirement [S1].

## When it applies

- Availability is expressed as a target, for example 99.99% of the time [S1].
- A single stateful component is on the critical path of every request, so the question "but
  what if it goes down?" has no answer yet. The source treats this as a question always worth
  asking [S1].

## Why it matters

An availability target is a claim about the whole system, but the system is only as available as
its least redundant dependency. Naming the target is not the same as designing for it.

## Approaches and tradeoffs

**Replication.** Maintain multiple identical copies of the data on different servers, so that if
one goes down traffic can be redirected to another [S1]. The cost is that the primary must be
able to interact with any replica without issues, which the source describes as tricky to get
right and a source of operational overhead [S1].

**Backup.** Periodically snapshot the data and store it in a separate location [S1]. The source
attributes the same class of cost — additional design complexity and operational overhead [S1].

Replication addresses continuing to serve; backup addresses recovering data. The source
presents both under the same question without ranking them [S1].

## Related redundancy in this source

- **Horizontal scaling of stateless services** provides redundancy as a side effect of running
  multiple instances behind request routing [S1]. See `read-heavy-workloads.md`.
- **Managed failover for a shared coordination store**, along with the observation that losing
  some counter values on failover is acceptable when the requirement is uniqueness rather than
  continuity [S1]. See `shared-counter-coordination.md`.

## Availability versus consistency

The source states the preference as part of the requirements — availability is ranked above
consistency for this system — but does not develop the consequences [S1].

S2 makes the same ranking and supplies the criterion behind it: **prioritize consistency only if
every read must receive the most recent write**; otherwise availability wins [S2]. It contrasts a
system where a stale read produces an incorrect transaction against one where a few seconds of
staleness is merely a delay [S2]. So the ranking is decided by what a stale read *costs*, not by
which property sounds safer. See `requirements-scoping.md`.

Neither source develops what stale reads then look like in practice — see
`## Not covered by sources` below.

## Related durability requirement

S2 states recoverability as a non-functional requirement in its own right — the system should be
able to recover data that is lost or corrupted [S2] — treating recovery as a separate commitment
from staying available, which matches the replication/backup split above.

## Failure modes

- **Total unavailability** when the single stateful dependency fails and neither approach is in
  place [S1].
- **Primary/replica interaction bugs**, which the source flags as the specific difficulty of
  replication [S1].
- **Data loss between snapshots**, implied by backups being periodic [S1].

## Not covered by sources

- What the stated availability target implies in downtime budget, or how to verify it.
- What stale or conflicting reads become possible once availability is ranked first, and how the
  application should behave when they occur. S2 gives the criterion for making the ranking, not
  the consequences of having made it.
- Failover mechanics — detection, promotion, and client redirection.
- Backup frequency, restore time, or how a restore is tested.
- How to satisfy a stated recoverability requirement, as opposed to stating it.

## Sources

- **[S1]** Hello Interview — Design Bit.ly —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/bitly>
- **[S2]** Hello Interview — Design a File Storage Service Like Dropbox —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/dropbox>
