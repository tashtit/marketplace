# Scaling Compute-Bound Work

When each request does substantial CPU work, capacity is limited by compute rather than by request
handling. The arithmetic decides between a bigger machine and more machines [S6].

## When it applies

- The request-handling tier scales horizontally without difficulty, but the work behind it is
  CPU-intensive [S6].
- A burst of demand, such as a timed event or a popular item, could overwhelm the workers doing that
  work [S6].

## Do the arithmetic first

The source's worked estimate shows the method [S6]:

- Assume a peak of 10k concurrent submissions, each running about 100 test cases.
- Assume 100ms per test case, which the source calls conservative; in practice most finish in
  10–50ms. A worst-case submission therefore takes about 10s, although typical ones fall within the
  5-second target.
- 10k × 100 = 1M test cases × 100ms = 100,000 CPU-seconds, which is over 27 hours on one core.
- Finishing that load within one minute needs about **1,667 cores**.

The conclusion comes from comparing that figure with what one machine offers. The largest instance
types top out at a few hundred vCPUs, so a single machine cannot do it [S6]. See
`capacity-estimation.md` for the general method.

## Approaches and tradeoffs

**Vertical scaling — graded bad** [S6]. Run the workers on a larger instance. This is the simplest
way to add capacity, but the source rejects it for two reasons [S6]:

- The arithmetic above exceeds what any single machine provides.
- Vertical capacity is hard to change dynamically, so a large and expensive machine sits mostly idle
  between peaks.

**Dynamic horizontal scaling — graded great** [S6]. Run several worker instances per runtime and
spread work across them. An auto-scaling group adds or removes instances according to traffic, CPU
use or memory [S6]. The only significant downside the source names is **over-provisioning**: running
too many instances wastes resources and money. It judges this manageable because cloud providers make
scaling up and down easy [S6].

**Horizontal scaling with a queue in front — also graded great** [S6]. The same approach, with a
buffer between the request handler and the workers. See `asynchronous-work-queue.md`.

## Scaling ahead of a known peak

If users must register for an event, you know when peak traffic will come and can scale the workers
up in advance [S6].

## Failure modes

- **Sizing on one machine** when the estimate needs more cores than any instance offers [S6].
- **Paying for idle peak capacity**, when vertical scaling cannot follow demand [S6].
- **Over-provisioning** under auto-scaling [S6].

## Not covered by sources

- What metric and threshold should trigger scaling, and how fast new instances must start.
- How to keep worker start-up time from eating the latency budget during a sudden spike.
- How to bound the cost of auto-scaling during an unexpected or abusive surge.
- How per-runtime worker pools are sized when demand differs between runtimes.

## Sources

- **[S6]** Hello Interview — Design a Coding Platform Like LeetCode —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/leetcode>
