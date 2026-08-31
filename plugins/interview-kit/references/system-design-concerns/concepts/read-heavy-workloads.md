# Read-Heavy Workloads

When a system's read volume vastly exceeds its write volume, the asymmetry should shape the
design rather than be discovered later [S1].

## When it applies

- Reads and writes are imbalanced by orders of magnitude. The source's example: roughly 1000
  reads for every 1 write [S1].
- The imbalance is structural, not incidental — records are created rarely and accessed
  frequently for the rest of their life [S1].

## Why it matters

The asymmetry significantly affects design decisions in areas including caching strategies and
database choice [S1]. The source treats recognizing the read-heaviness *from the start* as the
mark of a strong design, versus retrofitting it after building a symmetric system [S1].

Concretely, it changes what the bottleneck is. Once heavy read throughput is offloaded to a
cache, write throughput may turn out to be so low that database choice stops being interesting
— the source estimates ~100k new records per day, about 1 write per second, and concludes any
reasonable database will do [S1].

## Approaches and tradeoffs

**Separate the read path from the write path into independent services.** Because reads are
much more frequent than writes, splitting them lets each side scale independently according to
its own demand [S1]. This introduces a microservice architecture, with the attendant structure
[S1].

**Scale each side horizontally.** Add more instances of a service to distribute load across
multiple servers, handling a large number of requests per second without increasing the load on
any single one; incoming requests are routed to one of the instances [S1]. Note that horizontal
scaling of the *write* side is what breaks a shared counter — see
`shared-counter-coordination.md` [S1].

**Put the read path in memory.** See `caching-the-read-path.md`.

## Statelessness is the precondition for horizontal scaling

S3 makes the dependency explicit: the read service **is stateless, which is what allows it to be
scaled horizontally** by adding instances and load balancing between them [S3]. Horizontal scaling
is not a property you add to a service; it is a consequence of the service holding no
per-request state. S3 names round-robin and least-connections as the distribution algorithms, and
applies load balancing to every horizontally scaled tier including databases [S3].

The operational cost the source names: managing a large number of instances is complex, and
deployment and rollback procedures add to that burden [S3].

S3 states its asymmetry as **100:1** reads to writes, with a peak of **10 million users on one
record** producing tens of millions of concurrent requests — the figure its read path is sized
against [S3].

## Estimating the read load

The source works the arithmetic explicitly, and the method transfers:

1. Multiply active users by actions per user per day: 100M users × 5 = 500M reads per day [S1].
2. Divide by seconds in a day: 500M / 86,400 ≈ 5,787 reads per second [S1].
3. **Do not stop at the average.** That figure assumes even distribution across the day, which
   is unlikely — most traffic occurs during peak hours, so the system must be designed for
   spikes. The source multiplies by 100× to get ~600k reads per second as the design target
   [S1].

## Backing into the read volume from the write volume

S4 has no stated read figure, only a write one, and derives the reads from it — a useful technique
when the requirement given to you is the business number rather than the traffic number [S4]:

1. Start from the stated claim volume: 10M claims per day [S4].
2. Assume browsing per claim: roughly 10 pages viewed across search and landing pages before one
   item is claimed [S4].
3. Assume a conversion rate: only ~5% of visitors claim anything, the rest are browsing [S4].
4. Combine: `10M / 100k seconds/day * 10 / 0.05 = 20k queries/second` [S4].

Note the two moves worth keeping. S4 uses **100k seconds per day** rather than 86,400 — a
deliberate round number for mental arithmetic. And dividing by the conversion rate is what scales
the claim volume up to the population that produced it; multiplying by pages-per-visit scales it
again. Both assumptions are stated rather than hidden, which is what makes the result arguable.

S4's framing of *why* to do this: quantitative estimation at the point where you have spotted a
potential bottleneck gives everyone a shared set of numbers from which to weigh tradeoffs, and
demonstrates that the assumptions about the system are reasonable [S4]. The estimate is there to
make the bottleneck discussable, not to be precise.

The conclusion S4 draws is the ordinary one: 20k queries/second is sizeable enough that read scaling
has to be designed rather than assumed [S4]. It also characterizes the resulting shape — availability
queries vastly outnumber actual claims, while the underlying data updates only occasionally, which is
what makes aggressive caching with short TTLs the lever [S4]. See `caching-the-read-path.md` and
`partitioning-by-query-locality.md`.

## Separating a read path with a different query shape

S5 splits its read path off for a reason distinct from volume alone: the read workload is
**read-heavy and has very different query patterns** from the write paths, so separating it is what
lets it be designed for its own shape [S5]. Volume argues for more instances; a divergent query
pattern argues for a different service. See `service-and-data-boundaries.md`.

S5 also names the property that makes horizontal scaling of a write path trivial in the first
place: each host is **stateless because it is only writing to the database**, so capacity is added
by adding hosts [S5]. This corroborates S3's statelessness precondition from the write side rather
than the read side [S3][S5].

## Precomputing instead of scaling the read

Where the read is expensive because it *gathers* rather than because it is frequent, adding
capacity to the read tier is the wrong lever. S5's move is to do the assembly at write time and
reduce the read to a single lookup [S5] — see `fan-out-on-read-vs-write.md`. Its stated reason this
is available at all is that callers read constantly but write rarely, and that callers typically
consume only the first few entries, which is what makes precomputing a bounded result worthwhile
[S5].

## Failure modes

- **A single database instance struggling with the read volume even with optimized queries and
  indexing**, leading to increased response times and potential timeouts [S1].
- **Read load interfering with writes.** High read pressure might affect other database
  operations, such as record creation [S1].
- **Traffic concentrating on one record.** S3's peak case is not spread across the keyspace —
  everyone refreshes the *same* record at the moment it becomes interesting [S3].
- **Read load landing directly on the database** because the read path was built straight through
  to it, which S4 names as the load its deep dive exists to relieve [S4].
- **A read that is expensive because of how much it gathers, not how often it runs** — adding read
  capacity does not help when one request generates thousands [S5]. See
  `fan-out-on-read-vs-write.md`.

## Not covered by sources

- How to choose the peak-to-average multiplier (the source picks 100× without deriving it).
- How to measure the actual read:write ratio of an existing system.
- Whether read/write service separation is worth it below some scale threshold.
- How to make a service stateless when it currently is not.
- How to choose between round-robin and least-connections for a given workload.
- How to validate the browsing and conversion assumptions that a derived read estimate rests on.
- Whether a derived read estimate needs its own peak multiplier; S4 stops at the average.
- How different "different query patterns" must be before they justify a separate service rather
  than separate instances.

## Sources

- **[S1]** Hello Interview — Design Bit.ly —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/bitly>
- **[S3]** Hello Interview — Design Ticketmaster —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster>
- **[S4]** Hello Interview — Design a Local Delivery Service like Gopuff —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/gopuff>
- **[S5]** Hello Interview — Design Facebook's News Feed —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/fb-news-feed>
