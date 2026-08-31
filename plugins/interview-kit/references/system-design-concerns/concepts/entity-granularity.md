# Entity Granularity

Deciding whether a concern deserves its own entity, or belongs as attributes of an existing one,
turns on whether something is shared across a group of records [S3].

## When it applies

At the data-modeling step, when the same information could plausibly be folded into a neighbouring
entity [S3].

## The decision criterion

The source considers folding order data into the individual item record, and states when the
separate entity earns its place: **when one transaction covers several items**, because then the
group has properties of its own — a shared payment status and a shared total [S3]. The
generalizable test is not "is this a different noun" but "does a group of these records share state
that has nowhere else to live".

## Store shared layout once, derive the view from it

The source keeps a layout structure on the parent entity — defined once per location — rather than
duplicating it onto each item [S3]. Individual item records carry only their own coordinates within
that layout and their own status [S3]. The client then **combines the layout with each item's
status** to render the interactive view [S3].

Two transferable points: shared structural data belongs on the entity it is a property of, not
copied onto its children; and a composed view can be assembled by the client from two separately
fetched pieces rather than being materialized server-side.

Note the coupling to `preventing-double-allocation.md`: once a hold lives outside the item record,
the status half of that composition needs another source [S3].

## Splitting the type from the physical instance

S4 supplies a second criterion for creating an entity rather than folding it in: when the abstract
thing a caller asks about and the concrete thing the system must track are not the same object, they
are two entities — S4 likens the pair to a class and its instances [S4]. Callers care about the type;
the system has to know where each physical instance actually is, so the instance entity is defined as
a physical item at a specific location [S4]. The quantity a caller can have is then derived by
summing instances, and belongs to neither entity — see
`aggregating-availability-across-locations.md`.

S4 adds an ordering heuristic for finding entities in the first place: begin with the most concrete
physical or business nouns and work up to the abstract ones, which is what keeps an entity from being
missed [S4].

## Making a relationship its own entity

S5 supplies the simplest criterion of the three, and it applies whenever a relationship carries
direction: it makes an **explicit entity for the link between two records**, rather than embedding
it on either side [S5]. Its stated reason for the explicitness is that the link is
**uni-directional** — one record relates to another without the reverse holding [S5].

Two transferable points:

- **Asymmetry is what forces the separate entity.** A symmetric relationship can plausibly live on
  either participant; a directed one has a distinct meaning in each direction and so has its own
  identity [S5]. See `bidirectional-relationship-queries.md` for how the two directions are then
  queried.
- **A link entity is where per-edge state goes.** S5 later attaches a policy flag to the link
  itself [S5], which would have nowhere to live had the relationship been an attribute.

S5's entity list is also notable for how short it is, and it says so: at this step a **short list
of names is sufficient**, and the value is in agreeing the terms rather than in the modeling [S5].

## Not covered by sources

- What to do when the shared layout itself changes after child records were derived from it.
- Whether the composed view should ever be assembled server-side instead.
- How to model an item whose status is meaningful in more than one grouping at once.
- When to normalize versus embed the layout structure.
- Whether the type/instance split is worth it for a resource whose instances have no individual
  identity.
- Whether a symmetric relationship should also be modeled as its own entity, or only a directed one.
- How much state a link entity can accumulate before it is a first-class record in its own right.

## Sources

- **[S3]** Hello Interview — Design Ticketmaster —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster>
- **[S4]** Hello Interview — Design a Local Delivery Service like Gopuff —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/gopuff>
- **[S5]** Hello Interview — Design Facebook's News Feed —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/fb-news-feed>
