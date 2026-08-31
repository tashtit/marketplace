# Capacity Estimation Before Choosing Technology

Doing the arithmetic on data size and throughput first, so the technology choice becomes a
consequence rather than a guess [S1].

## When it applies

- A scale target has been stated ("support 1B records and 100M daily active users") and a
  storage or infrastructure decision follows from it [S1].
- You are about to reach for a distributed or sharded system because the numbers *sound* large
  [S1].

## Why it matters

The estimate determines whether a problem exists at all. The source's worked example concludes
that a scale target that sounds demanding is "well within the capabilities of modern SSDs," and
that a single conventional database instance is sufficient — sharding is named as the fallback
*if* a hardware limit is hit, not the starting point [S1].

The same arithmetic dissolves the database-selection question entirely: with heavy reads
offloaded to a cache and writes at roughly 1 per second, the source concludes "most will work
here" and that any reasonable database technology will do [S1].

## Method

**Size the data.** Sum the per-row cost of each field, then round up for metadata you have not
enumerated. The source's example: ~8 + ~100 + ~8 + ~100 + ~8 bytes ≈ 200 bytes per row, rounded
to 500 bytes to account for additional metadata such as creator and analytics ids [S1]. Multiply
by row count: 500 bytes × 1B rows = 500GB [S1].

**Bound the growth.** Identify what caps the dataset. In the source's case the number of URLs on
the internet is the maximum bound, so growth is expected to be modest [S1]. A bounded dataset
justifies a simpler design than an unbounded one.

**Size the write throughput.** Convert a daily figure to per-second: ~100k new records per day
is ~1 row per second [S1].

**Size the read throughput, including spikes.** See `read-heavy-workloads.md` for the full
method; the key step is not stopping at the daily average [S1].

**Derive a missing figure from the one you were given.** When the requirement states a business
volume but not a traffic volume, work outward from it using stated assumptions about behaviour —
S4 converts a daily claim count into queries per second via pages-per-visit and a conversion rate
[S4]. The full arithmetic is in `read-heavy-workloads.md`. S4's guidance on *when* to do this: reach
for estimation at the moment you have spotted a potential bottleneck, so the tradeoff discussion has
shared numbers underneath it [S4].

**Round the constants that only feed mental arithmetic.** S4 uses 100k seconds per day rather than
86,400 [S4]. The estimate's job is to be the right order of magnitude, and a figure you can divide in
your head is worth more than one you cannot.

**Size a derived structure before adopting it.** S5 gut-checks a precomputed structure before moving
on, and the arithmetic is the shape to copy: 10 bytes per identifier × 200 identifiers = 2KB per
record, × 2B records = 4TB, which it judges "quite reasonable for a modern system" [S5]. The point
is the ordering — the sizing happens *before* the structure is accepted, not after it is built.

**Convert bytes into money per unit.** S5 offers this as a rule of thumb: ask what a given user,
tenant, or item costs **in dollars** [S5]. Its own application is the comparison, not the figure —
2KB of storage is a fraction of a cent per month against revenue of roughly $100 per user per year
[S5]. A per-unit cost compared against per-unit revenue answers "is this reasonable" in a way that a
total in terabytes does not.

**Size the transfer time, not just the storage.** When a single operation moves a large payload,
the duration of that operation is itself a design input. S2's worked example: 50GB over a 100Mbps
connection is `50GB × 8 bits/byte / 100Mbps = 4000 seconds`, then
`4000 / 60 / 60 ≈ 1.11 hours` [S2]. The arithmetic is what converts "large file" into "exceeds
every timeout in the path" — see `large-file-transfer.md`. S2 frames this as arithmetic worth
doing on the spot, at the moment the constraint appears [S2].

## Choosing the technology afterward

The source's guidance, once the numbers show the workload is unremarkable: pick whichever
technology you have the most hands-on experience with; if you have none, default to a
well-understood relational database [S1]. Familiarity is a legitimate selection criterion when
the requirements do not discriminate between options [S1].

S2 reaches the same conclusion from the query pattern rather than from volume: loosely
structured records with few relations and a single dominant access path make a document store a
solid fit, while noting a relational database would work just as well and that the choice is not
worth dwelling on [S2]. Two sources, two routes, one conclusion — when the workload does not
discriminate, the choice is not load-bearing.

## Failure modes

- **Adopting distribution or sharding for a dataset a single instance handles**, paying
  complexity for nothing [S1].
- **Sizing on the average and being overwhelmed at peak** [S1].
- **Choosing a database on reputation** when the workload does not distinguish the candidates
  [S1][S2].
- **Discovering only at implementation time that a single operation takes hours**, because
  transfer duration was never estimated [S2].
- **Leaving the behavioural assumptions implicit** in a derived estimate, so the result cannot be
  argued with [S4].
- **Adopting a derived structure without sizing it first**, so its storage cost surfaces after it is
  built [S5].

## Not covered by sources

- Index, replica, and backup overhead on top of raw row size.
- How much headroom to leave over the computed figure.
- When to revisit the estimate as real traffic arrives.
- Cost estimation in currency, as opposed to bytes and operations per second. S5 gives a per-unit
  rule of thumb but not a method for infrastructure cost.
- What bandwidth figure to assume for a real user population, as opposed to a single stated
  connection speed.
- How to sanity-check a derived estimate against reality when no measured traffic exists yet.

## Sources

- **[S1]** Hello Interview — Design Bit.ly —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/bitly>
- **[S2]** Hello Interview — Design a File Storage Service Like Dropbox —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/dropbox>
- **[S4]** Hello Interview — Design a Local Delivery Service like Gopuff —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/gopuff>
- **[S5]** Hello Interview — Design Facebook's News Feed —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/fb-news-feed>
