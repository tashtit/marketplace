# Buffering Work Behind a Queue

Putting a queue between the request handler and the workers that do slow work. The queue absorbs
bursts and allows retries. In exchange, the request becomes asynchronous [S6].

## When it applies

- Each request triggers work that takes seconds, not milliseconds. The source describes this as the
  long-running tasks pattern: the API returns a job ID at once and background workers do the slow
  work, which prevents timeouts and lets the system scale [S6].
- Traffic may spike past what the workers can absorb at once [S6].
- Losing a request because a worker failed would be unacceptable [S6].

## What the queue buys

- **A buffer during peaks.** The request handler enqueues the work and the workers pull from the
  queue as they become free, so a spike does not overwhelm them [S6].
- **No lost work.** A spike or a worker failure does not drop a submission [S6].
- **Retries.** If a worker crashes or otherwise fails to finish, the item is requeued and tried
  again [S6].

## What it costs

**The flow becomes asynchronous.** The handler can no longer return the result in its response
[S6]. The source adds a status endpoint that looks up the work item and returns the result if it is
ready, or a "processing" marker if not, and has the client poll it every second [S6]. When the
worker finishes, it notifies the application server, which writes the result to the database and
updates any derived view, such as a cache [S6].

The source considers a persistent connection to avoid that poll and judges it unnecessary. It would
work, but it adds complexity when the polling interval is only a second [S6]. See
`propagating-changes-to-clients.md`.

## How to decide

The source makes a case against its own choice and records it [S6]:

- **It may be overengineering.** At the system's scale, the load could probably be handled without a
  queue [S6].
- **Predictable peaks weaken the case.** If users must register for an event in advance, you know
  when peak traffic will come and can scale workers ahead of it [S6].

It keeps the queue anyway, and its reason is **retries, not volume**: from a volume perspective the
queue is likely overkill [S6]. It closes by saying there is no single right answer and that weighing
the pros and cons is the point [S6].

In other words, the source names the justification that still holds after the obvious one,
throughput, falls away [S6].

## Interaction with worker scaling

The source introduces the queue as an addition to dynamic horizontal scaling of the workers, not as
a replacement for it [S6]. See `scaling-compute-bound-work.md`.

## Failure modes

- **Workers overwhelmed by a spike** when there is no buffer in front of them [S6].
- **Work silently lost** when a worker fails and nothing requeues it [S6].
- **Unnecessary complexity** when the volume never needed a buffer [S6].

## Not covered by sources

- How many times an item is retried, and what happens to an item that keeps failing.
- Whether a requeued item can run twice, and what that would do to stored results.
- How long a status record is kept, or what the client sees if the work never finishes.
- What delivery guarantee the queue must give for this use.
- How queue depth feeds back into scaling the workers.

## Sources

- **[S6]** Hello Interview — Design a Coding Platform Like LeetCode —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/leetcode>
