# Admission Control Under Demand Spikes

When demand for a contended resource far exceeds what the flow can serve, the useful move is to
restrict who is allowed in rather than to make the interface faster [S3].

## When it applies

The source's trigger is a specific user-experience breakdown, not a capacity metric: for
extremely popular events the displayed availability goes stale almost instantly, and users
repeatedly select an item only to be told it is gone [S3]. Pushing updates faster does not fix
this — it makes the display churn so quickly that the experience becomes disorienting [S3].

That is the diagnostic. Real-time push is the right answer when the display merely lags; it is the
wrong answer when the underlying contention means most users cannot succeed regardless of what
they see [S3]. See `propagating-changes-to-clients.md` for the push mechanisms themselves.

## Approach

**A virtual waiting queue in front of the contended flow.** Users are held before they can even
reach the selection interface, so the queue controls the rate at which users enter the flow —
preventing overload and improving the experience at the same time [S3]. The source's mechanism
[S3]:

- On requesting the page, the user is placed in a queue and a persistent connection is established
  to their client for position updates. Unidirectional server-to-client push is the simpler choice
  since only the server has anything to say, though a bidirectional protocol works if you
  anticipate needing it.
- The queue is ordered by timestamp in an in-memory store.
- Users are dequeued from the front periodically, or on a trigger such as items being sold, and
  notified over their connection that they may proceed.
- **Admission is enforced server-side, not just signalled.** The dequeued user is marked as
  admitted in a set with a time-to-live, and the service handling claims checks that set before
  allowing any claim request, rejecting users who did not come through the queue [S3].

That last step is what makes it admission control rather than a UI queue: the gate is checked at
the write path, so bypassing the front end does not bypass the restriction [S3].

**It is worth making the queue an operator-controlled switch.** The source describes it as
admin-enabled, applied for exceptionally high demand rather than always on [S3].

## Challenges

Long waits cause frustration, especially when estimated wait times are inaccurate or the queue
moves slower than expected [S3]. The stated mitigation is the same persistent connection: continuous
feedback on queue position and estimated wait [S3].

## Why this counts as a harder answer than a faster interface

The source frames this delta explicitly as the gap between a good and an excellent answer, noting
that the better solution is sometimes not the more technically sophisticated one [S3]. The
transferable point: when contention is the root cause, shaping demand beats optimizing the path
that serves it.

## Failure modes

- **A stale interface that churns** when the real-time push rate exceeds what a user can follow
  [S3].
- **Users repeatedly refused** after selecting an item, when everyone is admitted at once [S3].
- **Abandonment from long or misestimated waits** [S3].

## Not covered by sources

- How to compute an accurate estimated wait time.
- What dequeue rate to choose, or how to derive it from throughput.
- What happens to a user's queue position if their connection drops.
- Whether the queue itself becomes a contention point at extreme scale.
- How to prevent one user from occupying multiple queue positions.

## Sources

- **[S3]** Hello Interview — Design Ticketmaster —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster>
