# Probe Seeds — S1

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
| **Follow-up if thin** | Where to push when the first answer is shallow. |

**The symptom is the question.** Describe what is observed and let the candidate name the cause.
The moment you name the concern, you have handed over the answer and the probe is spent.

---

## P1 — Read volume versus lookup efficiency

- **Concern:** caching-the-read-path (vs point-lookup-indexing)
- **Symptom:** "Lookups are at 800ms p99. The key is indexed and the query plan confirms an
  index seek, not a scan. Database CPU is flat. Walk me through it."
- **Looking for:** recognition that indexing fixes scan cost, not volume; that the ceiling is
  disk IOPS (~100k) against a much higher request rate; that the next move is serving from
  memory, not more indexes [S1].
- **Bar:** senior unprompted; mid-level acceptable with prompting.
- **Follow-up if thin:** "The index is doing its job. So what is the actual limit you are
  hitting?" Then: "Roughly how much faster is memory than SSD, and why does that settle it?"

## P2 — Stale reads after expiry

- **Concern:** record-expiry ∩ caching
- **Symptom:** "A record is past its expiration. The database rejects it correctly. Users still
  get resolved to it for another few hours. Where would you look?"
- **Looking for:** cache TTL outliving the record's expiration; the fix is to set TTL to match
  or be shorter than the record's expiry so eviction is automatic [S1].
- **Bar:** senior — S1 names "cache invalidation for expired records" explicitly at senior [S1].
- **Follow-up if thin:** "Who else is holding a copy?" Then, if they reach for a purge
  mechanism: "Is there a way to make this self-correcting instead?"

## P3 — Duplicate identifiers under horizontal scale

- **Concern:** shared-counter-coordination
- **Symptom:** "The service ran fine on one instance. You scale to six and start seeing
  duplicate-key errors on insert. What happened?"
- **Looking for:** a counter local to each instance no longer produces globally unique values;
  needs a single source of truth with atomic increment-and-return [S1].
- **Bar:** senior [S1].
- **Follow-up if thin:** "What property does that shared store actually need? 'Fast' is not it."
  (Looking for atomic increment-and-return / single-threaded command processing [S1].)
- **Second follow-up:** "Now every write makes a network call. Defend that, or fix it."
  (Batched range allocation [S1].)

## P4 — Counter store failover

- **Concern:** shared-counter-coordination — failure behavior
- **Symptom:** "Your counter store fails over. It comes back having lost the last few hundred
  increments. How bad is that?"
- **Looking for:** the key distinction — the requirement is **uniqueness, not continuity**, so
  lost values are acceptable and gaps are harmless. Plus the database UNIQUE constraint as the
  ultimate safety net [S1].
- **Bar:** staff+, unprompted, if batching was used [S1].
- **Follow-up if thin:** "Does the design actually require consecutive values, or just distinct
  ones?"

## P5 — Enumeration of the keyspace

- **Concern:** unique-identifier-generation — predictability
- **Symptom:** "Someone has scraped every record you have ever created. They had no credentials
  and your auth is sound. How?"
- **Looking for:** sequential counters produce predictable identifiers, so iterating discovers
  everything; mitigate with a reversible transformation (e.g. XOR with a secret) before
  encoding — or a reasoned acceptance if the identifiers are meant to be public anyway [S1].
- **Bar:** staff+ [S1].
- **Follow-up if thin:** "What does your identifier reveal about the one issued before it?"

## P6 — Collision at scale

- **Concern:** unique-identifier-generation — collision handling
- **Symptom:** "Insert collisions were negligible in testing. At 40% keyspace occupancy they are
  frequent enough to show up in latency. Was that predictable?"
- **Looking for:** collision probability for the next identifier is `n / |S|`, so it grows with
  occupancy; higher entropy means longer identifiers, which fights shortness; collision checks
  add a database lookup per insert. The three-way tension between uniqueness, shortness, and
  efficiency [S1].
- **Bar:** senior — the hashing/counter tradeoff is expected without much prompting [S1].
- **Follow-up if thin:** "What is your bounded retry strategy, and what happens when it is
  exhausted?" (S1 gives 3–5 retries with a salt, then fall back or error [S1]. Note S1 does not
  say what to do after exhaustion — do not grade beyond that.)

## P7 — Unrevocable client state

- **Concern:** client-cached-responses
- **Symptom:** "You need to repoint a mapping. Some clients keep going to the old target and
  never hit your server at all. What did you do earlier that caused this?"
- **Looking for:** a cacheable (permanent) response let clients stop asking; mutable or
  expirable mappings require the non-cacheable form, which also preserves per-request
  visibility [S1].
- **Bar:** mid-level for the reasoning — S1 explicitly permits not knowing the status code
  number [S1].
- **Follow-up if thin:** "What did you give up in exchange for those clients not calling you?"

## P8 — Sizing before technology

- **Concern:** capacity-estimation
- **Symptom:** "You are asked to support a billion records. Your first instinct is to reach for
  something distributed. Talk me out of it."
- **Looking for:** per-row sizing summed and rounded for metadata, times row count, compared
  against what one instance handles; identifying what bounds growth; sharding as a fallback if a
  hardware limit is hit, not a starting point [S1].
- **Bar:** senior — "propose a reasonable database choice and justify it" [S1].
- **Follow-up if thin:** "Now size the write throughput per second. Does the database choice
  still matter?" (Looking for: at ~1 write/sec it does not, so pick what you know [S1].)

## P9 — Designing from the asymmetry

- **Concern:** read-heavy-workloads
- **Symptom:** "Give me the read-to-write ratio for this system. When did you first work it out
  — before or after you chose the architecture?"
- **Looking for:** the asymmetry recognized early enough to shape the design, separate scaling of
  read and write paths, and awareness that it drives caching and database decisions [S1].
- **Bar:** **staff+** — S1 requires recognizing read-heaviness quickly and structuring the design
  accordingly *from the start* [S1]. Reaching it late is senior behavior.
- **Follow-up if thin:** "Your daily average is ~5.8k reads/sec. What do you actually design
  for?" (Looking for peak multiplication, not the average [S1].)

## P10 — Availability of a single stateful dependency

- **Concern:** redundancy-for-availability
- **Symptom:** "You have committed to 99.99%. One database, one instance. Does the number hold?"
- **Looking for:** replication (serve through the loss) versus backup (recover the data), and
  honesty that both add operational overhead and primary/replica interaction risk [S1].
- **Bar:** senior.
- **Follow-up if thin:** "Which of those two keeps you serving, and which just keeps your data?"
- **Note:** S1 states "availability > consistency" without developing it. If the candidate goes
  there, **do not grade the answer** — see `## Not covered by sources` in
  `redundancy-for-availability.md`.

## P11 — Custom identifiers colliding with generated ones

- **Concern:** unique-identifier-generation — namespace collision
- **Symptom:** "A user claims a custom identifier today. In eight months your generator produces
  that exact string. What happens, and how would you have prevented it?"
- **Looking for:** keeping the two from competing — prefix generated identifiers with a character
  custom ones cannot use, or separate namespaces entirely [S1].
- **Bar:** staff+ — S1 lists custom alias collision prevention as product thinking [S1].

## P12 — Deduplication as a product decision

- **Concern:** unique-identifier-generation — determinism
- **Symptom:** "Two users submit the same input. Should they get the same identifier back?"
- **Looking for:** that this is a product decision, not a storage optimization — separate expiry
  dates, independent analytics, and different custom aliases all require multiple identifiers per
  input; deduplication trades those away for storage efficiency [S1].
- **Bar:** staff+ (product thinking).
- **Follow-up if thin:** "What does a shared identifier prevent the second user from doing?"

---

## Coverage note

These seeds cover the concepts S1 developed. S1 is an entry-level problem and says nothing about
idempotency, rate limiting, observability, or asynchronous processing — **do not probe those**,
and do not let a candidate's failure to mention them affect a score. Add seeds only when a source
establishes the bar.

## Sources

- **[S1]** Hello Interview — Design Bit.ly —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/bitly>
