# Requirements Scoping

Separating what a system must do from how it must behave, and deciding deliberately what is out
of scope [S1].

## When it applies

- At the start of a design, before any component or technology is chosen [S1].
- Whenever a feature is proposed that is adjacent to the core purpose but not part of it [S1].

## Why it matters

Scope decides everything downstream. The source's guidance is to concentrate on the top three or
four features and not get distracted by "bells and whistles" [S1] — and its own scope choices
are what make the rest of its design tractable.

## Method

**Separate functional from non-functional requirements.** Functional requirements are the tasks
the system performs. Non-functional requirements are specifications about *how* the system
operates — attributes such as scalability, latency, security, and availability [S1].

**Express non-functional requirements as specific benchmarks**, not adjectives. The source's
framing is explicit on this: they are "often framed as specific benchmarks — such as a system's
ability to handle 100 million daily active users or respond to queries within 200 milliseconds"
[S1]. Its own list follows that form: a stated uniqueness guarantee, a latency bound (< 100ms),
an availability target (99.99%), and a scale target (1B records, 100M daily active users) [S1].

A benchmark is testable; "should be fast" is not.

**Rank competing attributes.** The source states a preference between two non-functional
attributes directly — availability over consistency — rather than claiming both [S1][S2].

S2 supplies the criterion the ranking should turn on: **prioritize consistency over availability
only if every read must receive the most recent write; otherwise the system breaks** [S2]. Its
two worked cases show the test being applied — a trade executed in one region must be visible
before a related trade elsewhere proceeds, so consistency wins; a stored file that a distant user
cannot see for a few seconds is fine, so availability wins [S2]. The discriminator is whether a
stale read causes incorrect behavior, not how undesirable staleness feels.

**Cap the extremes the system must handle.** S2 states a maximum payload size as a
non-functional requirement [S2] — and that single number is what forces the design of the
transfer path. See `large-file-transfer.md`.

**Identify the workload asymmetry at requirements time.** The read:write imbalance is called out
as part of the requirements discussion, before any component exists, because it will
significantly affect later design decisions [S1]. See `read-heavy-workloads.md`.

**Declare what is below the line.** Name the excluded features explicitly and justify the
exclusion: the source's reason is that they add complexity to the system without being core to
the basic functionality [S1]. Exclusions it makes include authentication and account management,
analytics, real-time analytics consistency, and advanced security features such as spam and
malicious-content filtering [S1].

**Treat exclusions as negotiable, not settled.** The source's stance is that out-of-scope items
are things you would discuss with your interviewer to determine whether they belong in the
design [S1] — in a real project, the equivalent is confirming exclusions with whoever owns the
requirements rather than deciding silently.

**Mark optional functional requirements as optional.** The source's core requirements include
two explicitly optional capabilities [S1], which keeps them in view without making them
load-bearing.

## Ranking availability and consistency per operation, not per system

S3 splits the CAP decision *within* one system: availability for the read paths (viewing and
searching), but strong consistency for the claim path, because two users must never be sold the
same item [S3]. The transferable point is that "is this system AP or CP" can be the wrong
granularity — the unit of the decision is the operation, and a system can legitimately want both.

The rest of the design follows from that split: the consistent operation is what justifies ACID
transactions and a shared datastore (see `service-and-data-boundaries.md`), while the available
operations are what justify caching and horizontal scaling [S3].

S3 also quantifies its non-functional requirements at this stage rather than later: a read:write
ratio of **100:1**, a search latency target of **under 500ms**, and a peak of **10 million users
on a single item** [S3]. All three are the figures the later deep dives are measured against —
which is what makes them requirements rather than aspirations.

S4 splits the same way and states the split as its two core non-functional requirements: reads
should be fast (**<100ms**), and the claim path should be strongly consistent so that two callers
cannot purchase the same physical item [S4]. It attaches a *reason* to its latency number that is
worth keeping — the bound exists to support use cases like search, so the figure is derived from a
downstream consumer rather than chosen for feel [S4]. Its scale requirements are stated in the same
breath: support for **10k locations** and **100k item types**, at an order of **10 million claims per
day** [S4].

## Naming the emphasis of the problem

S4 does something the other sources do not: after listing scope, it states in one sentence where the
emphasis of the design lies — aggregating availability across local sites, and allowing claims
without double booking [S4]. It contrasts this explicitly with a neighbouring problem where the
catalog and search would be the interesting part instead [S4].

The transferable practice is that scope lists say what is in and out, but not what is *central*.
Naming the emphasis is what stops a design from spending its effort on an in-scope but peripheral
concern.

S5 states the emphasis as a plan for where the time goes: it names the hard part up front, then says
it will **move quickly through the base requirements in order to have time to dive deep there**
[S5]. Naming the emphasis is therefore not only a scoping act but a budgeting one — the hard part is
identified so the easy parts can be deliberately rushed.

S5 also names the failure this budgeting prevents, as an observed pattern rather than advice: a very
common failure mode is getting **lost in the weeds of one scaling problem before having a mostly
complete design** [S5]. Its rule is to cover the breadth of the requirements before going into
depth on any of them — while still moving quickly [S5]. The companion move is stating the
inadequacy out loud: S5 deliberately builds a naive solution first, saying plainly that it will not
scale and that the scaling problems will be solved separately [S5].

## Quantifying a requirement so it discriminates between architectures

S5 gives the sharpest statement of *why* benchmarks over adjectives, and it is about the design
rather than about testability: attaching quantities to non-functional requirements is what lets you
make decisions later, because **a single-digit-millisecond system requires a dramatically different
architecture than a "fast" system that may take a second** [S5]. The number's job is to rule
architectures out.

Its own requirements follow that form — availability preferred over consistency with a **stated
staleness tolerance of up to 1 minute**, a latency bound of **< 500ms** covering both the write and
the read, and a scale target of **2B users** [S5]. The staleness tolerance is the load-bearing one:
it is what later licenses moving work off the request path entirely [S5]. See
`fan-out-on-read-vs-write.md`.

S5 also states a requirement as the *absence* of a bound — unlimited relationships in both
directions [S5] — which is what makes its fan-out problem exist at all. An explicitly unbounded
requirement is a design constraint, not a missing one.

## Negotiating the product instead of the architecture

S5 raises an option the other sources do not: when a requirement is what makes the problem hard, ask
whether the **product** can be adjusted rather than the system [S5]. Its examples are a cap on the
number of relationships per entity, or a deliberately different experience for the extreme cases,
and it notes that production systems commonly do exactly this [S5]. Its own justification is a
user-impact argument: the tail user with an extreme number of relationships is unlikely to notice
their content arriving a couple of minutes late [S5].

The transferable form is that a constraint presented as fixed may be a product decision, and the
cheapest fix for an extreme case is sometimes to exclude it from the guarantee rather than to
engineer for it.

## Deferring a decision explicitly

S5 adds a tactic for keeping the sequencing honest under time pressure: rather than either
over-specifying a component or silently skipping it, say you will **come back to it if there is
time**, and move on [S5]. It applies this to the internal structure of its main record, in order to
protect time for the harder parts [S5].

The reasoning it attaches is about signalling: time spent on the obvious parts is not just time
lost, it also suggests an inability to **distinguish the complex pieces from the trivial ones**,
which S5 calls a critical skill [S5]. Where sources disagree slightly in emphasis: S1 says
concentrate on the top few features [S1], while S5 says the ordering of effort itself carries
information.

## Working through the requirements in order

S2 adds a sequencing rule for the design that follows: build up the design one functional
requirement at a time, then use the non-functional requirements to drive the deeper passes [S2].
Requirements are not just a gate before design; they are the order the design gets built in.

S4 states the same sequence as a deliberate default and gives the reason to depart from it: when the
requirements are straightforward, design first for the functional requirements *without much concern
for scale*, then reintroduce the non-functional concerns one at a time in the deeper passes [S4]. It
also names the step before that — briefly deciding what approach to take, rather than starting to
draw [S4], and its own order within the functional pass: enumerate the nouns, define the API from
them, then lay out the components [S4]. See
`aggregating-availability-across-locations.md` for the entity-ordering heuristic S4 uses.

S5 corroborates both the sequence and the reason for the ordering: it works its functional
requirements **in order**, saying that for this problem — and many — the requirement order provides
a natural structure [S5]. It gives the same reason as S4 for starting from entities: they give you
a **set of terms to use for the rest of the design**, and they surface the data model the later
requirements will need [S5].

S4 warns against the opposite failure at the API step: pushing extraneous detail into the interface
early, which it calls a common mistake because it burns time without changing the design [S4].

S5 makes the complementary move at the same step — deliberately leaving the internal structure of
its main record undefined for now, in order to protect time for the harder parts [S5].

## Treating exclusions as assertions

S4 adds a stance on *how* exclusions get agreed. Out-of-scope items usually surface as a question
("do we need to handle this?"), and the source's guidance is that it is acceptable to assert an
exclusion — to state you are leaving a concern out for now — and be corrected if the assertion is
wrong [S4]. The transferable version is that an explicit, visible assumption is cheaper than an
open question, because it can be contradicted; a silent one cannot.

Its own exclusions are payment handling, routing and delivery, catalog and search, cancellations and
returns, privacy and security, and disaster recovery [S4].

## Failure modes

- **Designing for unstated requirements**, adding complexity nothing asked for [S1].
- **Non-functional requirements too vague to verify**, when stated without benchmarks [S1].
- **Discovering a workload asymmetry after the architecture is fixed** rather than during
  requirements [S1].
- **Ranking consistency first out of caution**, when no read actually requires the most recent
  write [S2].
- **Applying one consistency ranking to a whole system**, when different operations have opposite
  requirements [S3][S4].
- **Stating a latency target with no downstream consumer to justify it**, so the number cannot be
  defended [S4].
- **Spending the design on an in-scope but peripheral concern**, because the emphasis was never
  named [S4].
- **Over-specifying the API before the design exists**, burning effort on detail that changes
  nothing [S4].
- **Getting lost in one scaling problem before the design is broadly complete** [S5].
- **Engineering for an extreme case that the product could simply exclude** from the guarantee
  [S5].
- **Stating a latency target loosely enough that it rules no architecture out** [S5].

## Not covered by sources

- How to elicit requirements when no one states them.
- How to revisit scope once implementation is underway.
- How to resolve conflicts between two stated non-functional targets.
- How to apply S2's consistency test when only *some* reads must see the latest write.
- How to reconcile a per-operation consistency split when one operation reads data the other
  writes.
- How to tell a central requirement from a peripheral one when the source does not state the
  emphasis.
- When the design-functional-first default should be abandoned for a scale-first approach.
- How to tell which requirement is negotiable as a product decision rather than an engineering one.
- How to choose a staleness tolerance, as opposed to being handed one.

## Sources

- **[S1]** Hello Interview — Design Bit.ly —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/bitly>
- **[S2]** Hello Interview — Design a File Storage Service Like Dropbox —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/dropbox>
- **[S3]** Hello Interview — Design Ticketmaster —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster>
- **[S4]** Hello Interview — Design a Local Delivery Service like Gopuff —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/gopuff>
- **[S5]** Hello Interview — Design Facebook's News Feed —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/fb-news-feed>
