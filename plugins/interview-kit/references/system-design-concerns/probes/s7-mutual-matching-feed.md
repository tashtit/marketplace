# Probe Seeds — S7

Question seeds for the `mock-design-interview` skill. Each seed is raw material, **not a
script**: the interviewer generates the actual wording live from the seed plus the candidate's
repo and transcript.

## How to read a seed

| Field | Meaning |
| --- | --- |
| **Concern** | The concept being probed. **Never say this out loud.** |
| **Symptom** | The observable situation to describe to the candidate. |
| **Looking for** | What a good answer contains. Grounded in a concept file, never invented. |
| **Bar** | The level at which this is expected unprompted, per `level-expectations.md`. |
| **Follow-up if thin:** | Where to push when the first answer is shallow. |

**The symptom is the question.** Describe what is observed and let the candidate name the cause.
The moment you name the concern, you have handed over the answer and the probe is spent.

---

## P1 — two yeses, no match

- **Concern:** `detecting-mutual-actions.md` — never spoken aloud
- **Symptom:** Support tickets report pairs of users who both said yes to each other within the same
  second, yet neither was ever told. Both actions are in the database.
- **Looking for:** The interleaving: both checks run before either write lands, so both miss [S7].
  The remedy is to make the write and the check one atomic step [S7]. A strong answer notes the
  alternative, a reconciliation pass, and that it trades consistency for availability [S7].
- **Bar:** Senior — S7 expects ensuring successful match creation to be discussed in detail at
  senior [S7].
- **Follow-up if thin:** Ask what has to be true about where the two records live for that atomic
  step to be cheap.

## P2 — the transaction that cannot reach

- **Concern:** `detecting-mutual-actions.md` — never spoken aloud
- **Symptom:** The candidate wraps the write and the check in a transaction. The store's
  transactions only work within one partition, and records are partitioned by the user who acted.
- **Looking for:** Recognition that the two directions sit on different partitions, and a key built
  from both IDs in sorted order so they share one [S7]. Strong answers name the costs: partitions
  grow, very active users create hot partitions, and old data needs cleanup [S7]. An alternative is
  an in-memory atomic operation under the same pair key, backed by the durable store [S7].
- **Bar:** Senior — S7 expects match creation to be discussed in detail at senior [S7].
- **Follow-up if thin:** Ask what is lost if the in-memory copy dies, and why that is acceptable.

## P3 — telling the first person

- **Concern:** `detecting-mutual-actions.md` — never spoken aloud
- **Symptom:** The person who completes a match sees it at once. The person who said yes three
  weeks earlier never finds out unless they open the app.
- **Looking for:** The second actor is told inline. The first actor is out of the flow and needs a
  push notification, which the source treats as an assumed external capability [S7].
- **Bar:** Mid-level — S7 expects a working high-level design for matching at this level [S7].
- **Follow-up if thin:** Ask which assumption they are making about the delivery mechanism, and
  whether they would state it.

## P4 — the feed that takes two seconds

- **Concern:** `fan-out-on-read-vs-write.md` — never spoken aloud
- **Symptom:** Opening the app takes about two seconds before the first card appears. The trace
  shows one query filtering users by age, preference and a latitude/longitude box.
- **Looking for:** The options graded in the source: an indexed search store queried in real time,
  feeds precomputed by background jobs, and the combination. The combination serves the precomputed
  feed at once and generates more as it runs low [S7]. Strong answers trigger the refresh before the
  feed runs out [S7].
- **Bar:** Senior — S7 expects senior candidates to call out the tradeoffs for feed building
  proactively [S7].
- **Follow-up if thin:** Ask what a very active user experiences under precomputation alone.

## P5 — the coordinate box

- **Concern:** `proximity-candidate-filtering.md` — never spoken aloud
- **Symptom:** The query that finds nearby users has an index on latitude and one on longitude.
  It still reads millions of rows for one dense city.
- **Looking for:** A geospatial index, which can fetch the records within an area efficiently,
  instead of range filters on raw coordinates [S7].
- **Bar:** Senior — S7 expects "some knowledge" of the type of index that could power the feed at
  senior. Supporting geospatial filtering at all is already a mid-level requirement [S7].
- **Follow-up if thin:** Ask where that index would live if the primary store does not provide one.

## P6 — the profile that moved away

- **Concern:** `fan-out-on-read-vs-write.md` — never spoken aloud
- **Symptom:** Users report cards for people who live in another city, and cards that do not match
  the age range they set this morning.
- **Looking for:** Precomputed entries go stale when a candidate's location or attributes change,
  or the user's own filters or location change [S7]. The stated mitigations are a strict TTL with a
  scheduled recompute, precomputing only for recently active users, and a background refresh when
  the user changes filters or location [S7].
- **Bar:** Senior — S7 expects awareness of when feed caches become stale at senior [S7].
- **Follow-up if thin:** Ask which of their mitigations are parameters an operator could change
  without a deploy.

## P7 — the search store falls behind

- **Concern:** `full-text-search.md` — never spoken aloud
- **Symptom:** The feed is built from a secondary store optimized for filtering. Newly registered
  users take a long time to appear in anyone's feed, and some deleted profiles keep showing up.
- **Looking for:** Keeping the secondary store in sync with the primary through change data capture
  [S7]. Strong answers batch writes into it according to the update rate, because it is optimized
  for reads, not writes [S7].
- **Bar:** Senior — S7 expects knowledge of feed-building tradeoffs and the index behind them at
  senior [S7].
- **Follow-up if thin:** Ask what the batching interval costs in freshness.

## P8 — "I already said no to her"

- **Concern:** `excluding-previously-seen-items.md` — never spoken aloud
- **Symptom:** Users report seeing someone again a few minutes after swiping on them. The
  history store is configured to favour availability.
- **Looking for:** Replica lag means recent actions are missing when the feed is built [S7]. The
  remedy is a cache of the K most recent actions, held on the client, which filters suggestions
  [S7]. A strong answer gives the reason for putting it on the client: a backend cache just to
  cover replication lag would be expensive. It also states the single-device assumption [S7].
- **Bar:** Mid-level — S7 requires a design that avoids re-showing items at this level [S7].
- **Follow-up if thin:** Ask what breaks if the user also uses a second device.

## P9 — the user with a million swipes

- **Concern:** `excluding-previously-seen-items.md` — never spoken aloud
- **Symptom:** Feed building is fast for most users but takes seconds for a small group with very
  long histories. The time is spent checking candidates against those histories.
- **Looking for:** A probabilistic membership filter for users past a history size. It never gives
  false negatives, so nothing is re-shown, but it gives some false positives, so a few candidates
  are never shown. Its error rate trades against space [S7]. A strong answer names the cost of
  keeping the filter updated and recoverable, and that the source itself says this skews
  somewhat "over-engineered" [S7].
- **Bar:** Staff+ — S7 expects exceptional staff candidates to go into detail on each topic [S7].
- **Follow-up if thin:** Ask which error the product can tolerate, and why.

## P10 — one store for everything

- **Concern:** `service-and-data-boundaries.md` — never spoken aloud
- **Symptom:** Profiles and swipes share one service and one database. Swipes write roughly a
  hundred times as often as profiles change, and the swipe table grows by hundreds of gigabytes a
  day.
- **Looking for:** Splitting the write-heavy path into its own service and store so it can scale and
  be optimized independently, with the volume estimate behind that [S7]. A strong answer names the
  consistency cost of a write-optimized store, and that the split is a judgement for this system,
  not a rule [S7].
- **Bar:** Senior — S7 expects senior candidates to articulate the pros and cons of architectural
  choices [S7].
- **Follow-up if thin:** Ask what the split costs for the operation that needs consistency.

## P11 — "next page"

- **Concern:** `cursor-pagination.md` — never spoken aloud
- **Symptom:** The feed endpoint carries page and offset parameters. Clients often request
  page 40 and get users they have already passed on.
- **Looking for:** Recognition that a generated recommendation feed needs no paging: the client
  calls the endpoint again for more [S7].
- **Bar:** Mid-level — S7 expects clearly defined API endpoints at this level [S7].
- **Follow-up if thin:** Ask what "page 40" means when the list is regenerated each time.

## Coverage note

Concerns S7 does **not** establish a bar for. Do not probe or score these from this source:

- **Picture upload, chat after matching, paid features.** Declared out of scope [S7].
- **Fake-profile protection, monitoring and alerting.** Declared out of scope [S7].
- **How matches are stored after creation.** S7 deliberately leaves this out [S7].
- **Push delivery internals.** S7 assumes an external service and says to state the assumption
  [S7].
- **Ranking or relevance of candidates.** S7 filters on preferences and distance but makes no claim
  about ordering [S7].
- **Trusting client-reported location.** S7 sends location from the client without discussing
  verification [S7].
- **Observability, rate limiting, multi-region deployment, disaster recovery.** Not discussed [S7].

Two scoping rules specific to this source:

- **Do not require the probabilistic filter.** S7 itself says the approach skews somewhat
  "over-engineered". P9 is graded on the reasoning, and its absence is not a miss below staff+ [S7].
- **S7's internal estimate is inconsistent** (100 vs 200 actions per user per day). Do not grade a
  candidate against either figure. Grade the method [S7].

## Sources

- **[S7]** Hello Interview — Design a Dating App Like Tinder —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/tinder>
