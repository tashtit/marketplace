# Probe Seeds — S6

Question seeds for the `mock-design-interview` skill. Each seed is raw material, not a script.

| Field | Meaning |
| --- | --- |
| **Concern** | Concept being probed; never spoken aloud. |
| **Symptom** | Observable situation presented to the candidate. |
| **Looking for** | Source-backed content expected in an answer. |
| **Bar** | Seniority expectation stated by the source. |
| **Follow-up if thin** | Where to push after a shallow answer. |

## P1 — both actions recorded, neither result delivered

- **Concern:** `atomic-reciprocal-actions.md` — never spoken aloud
- **Symptom:** Two people act on each other at nearly the same moment. Both writes appear in storage, but neither receives the result that usually appears immediately after the second action.
- **Looking for:** Identify the check-before-write race and keep the reciprocal check and write atomic on one pair-derived key; discuss delayed reconciliation as a tradeoff if immediate feedback is not required [S6].
- **Bar:** Senior — S6 expects detailed discussion of successful reciprocal-result creation [S6].
- **Follow-up if thin:** Ask what happens when the two actions are stored on separate partitions.

## P2 — fast first list, delayed next list

- **Concern:** `personalized-candidate-generation.md` — never spoken aloud
- **Symptom:** Opening an app shows candidates immediately, but a fast-moving user reaches the end of the list and waits for the next batch.
- **Looking for:** Combine a precomputed initial list with indexed real-time candidate queries, starting refresh while a few entries remain; weigh staleness and search-index synchronization [S6].
- **Bar:** Senior — S6 expects scalable list management and proactive tradeoff analysis [S6].
- **Follow-up if thin:** Ask what changes when the viewer moves or changes filters before consuming the list.

## P3 — recent actions appear again

- **Concern:** `excluding-processed-candidates.md` — never spoken aloud
- **Symptom:** A person sees entries they already dismissed just after requesting a fresh list, although the server accepted each action.
- **Looking for:** Explain replica lag and the cost of filtering against an ever-growing history; use recent client-side action history to filter newly received candidates, given the source's one-device assumption [S6].
- **Bar:** Mid-level — S6 expects a solution that avoids re-showing acted-on candidates [S6].
- **Follow-up if thin:** Ask how the answer changes if the person switches devices.

## P4 — apparent search results drift behind updates

- **Concern:** `personalized-candidate-generation.md` — never spoken aloud
- **Symptom:** A profile update is visible in the primary store but candidates in search still reflect its old location and preferences.
- **Looking for:** Recognize lag between primary data and the separate indexed store; consider change data capture and batching writes only where update rate calls for it [S6].
- **Bar:** Senior — S6 expects recognition of stale results and the index powering the list [S6].
- **Follow-up if thin:** Ask what would happen if an indexing update failed.

## Coverage note

This source does not establish a bar for exactly-once notification delivery, multi-device reconciliation, failed index-update recovery, or a concrete safe transaction implementation. Do not probe or score those concerns.

## Sources

- **[S6]** Hello Interview — Design a Dating App Like Tinder —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/tinder>
