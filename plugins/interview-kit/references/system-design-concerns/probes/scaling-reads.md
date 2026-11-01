# Probe Seeds — Scaling Reads

Tashtit-authored scenarios derived from [S8]. Adapt them to the named attempt;
never speak the Concern or Looking for fields before the debrief.

Technical criteria come from the linked concept. Seniority is assessed only where
[level expectations](../level-expectations.md) explicitly supplies a bar.

## P1 — Growing lookups

- **Concern:** [Scaling Reads](../concepts/scaling-reads.md#start-with-the-query) — never spoken aloud.
- **Symptom:** Lookup latency rises with dataset size; the query plan scans most rows.
- **Looking for:** Start with query-pattern indexes and inspect the plan; explain composite-index order. [S8]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** What does the engine read to answer one lookup?

## P2 — One popular item

- **Concern:** [Scaling Reads](../concepts/scaling-reads.md#failure-and-overload-cases) — never spoken aloud.
- **Symptom:** One in-memory node times out while almost all requests ask for the same item.
- **Looking for:** Distinguish coalescing backend fetches from distributing hot-key read traffic; explain replicated-key memory and invalidation costs. [S8]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** Does combining misses reduce the traffic for cache hits?

## P3 — The expiry cliff

- **Concern:** [Scaling Reads](../concepts/scaling-reads.md#failure-and-overload-cases) — never spoken aloud.
- **Symptom:** At the same minute every hour, origin queries spike and requests fail.
- **Looking for:** Explain concurrent rebuilds and compare serialized rebuilds, early refresh, and scheduled refresh with their costs. [S8]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** What does a request do while a rebuild is running?

## P4 — An update stays invisible

- **Concern:** [Scaling Reads](../concepts/scaling-reads.md#replicas-partitions-and-caches) — never spoken aloud.
- **Symptom:** An entity changes but users still see its older value through several serving layers.
- **Looking for:** Use the freshness requirement; explain versioned entity keys and current-version discovery, or explicit invalidation and its propagation limits. [S8]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** How does a reader learn which version is current?

## Coverage note

Score only the cited mechanisms in Looking for. Questions in the concept’s
Not covered by sources section have no answer key here. Do not infer a seniority
level from an article heading, a deep dive, or the difficulty of this scenario.

## Sources

- **[S8]** Hello Interview — Scaling Reads — <https://www.hellointerview.com/learn/system-design/patterns/scaling-reads> (user-supplied saved HTML, processed 2026-11-01).
