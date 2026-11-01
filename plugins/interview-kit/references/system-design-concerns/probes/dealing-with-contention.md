# Probe Seeds — Dealing with Contention

Tashtit-authored scenarios derived from [S13]. Adapt them to the named attempt;
never speak the Concern or Looking for fields before the debrief.

Technical criteria come from the linked concept. This source establishes no
career-level thresholds.

## P1 — The count is right but ownership is wrong

- **Concern:** [Dealing with Contention](../concepts/dealing-with-contention.md#guard-the-actual-resource) — never spoken aloud.
- **Symptom:** Two users receive the same numbered resource even though the total remaining count stays nonnegative.
- **Looking for:** Guard the specific resource, not just aggregate capacity; gate dependent records on a successful conditional write. [S13]
- **Bar:** No seniority bar established by this source.
- **Follow-up if thin:** What exact row distinguishes the two claims?

## P2 — A failed update still produces a record

- **Concern:** [Dealing with Contention](../concepts/dealing-with-contention.md#guard-the-actual-resource) — never spoken aloud.
- **Symptom:** An update changes zero rows, yet its transaction commits a related record as though it succeeded.
- **Looking for:** Zero affected rows need not be an error. Make dependent writes conditional on success or explicitly roll back, keeping related database changes transactional. [S13]
- **Bar:** No seniority bar established by this source.
- **Follow-up if thin:** What does the application check before creating the dependent record?

## P3 — Two transfers stop each other

- **Concern:** [Dealing with Contention](../concepts/dealing-with-contention.md#read-decide-then-write) — never spoken aloud.
- **Symptom:** Two transactions each hold one account while waiting for the other account.
- **Looking for:** Use a globally consistent acquisition order across all participants, handle deadlock aborts, and distinguish lock-wait timeouts from cycles. [S13]
- **Bar:** No seniority bar established by this source.
- **Follow-up if thin:** Does always starting with the initiating account produce the same order?

## P4 — The value looks unchanged

- **Concern:** [Dealing with Contention](../concepts/dealing-with-contention.md#read-decide-then-write) — never spoken aloud.
- **Symptom:** A value is read, changes twice, and returns to its original amount before a stale writer checks it.
- **Looking for:** Explain ABA and a dedicated version that advances on every write; handle failed conditional updates rather than committing dependent work. [S13]
- **Bar:** No seniority bar established by this source.
- **Follow-up if thin:** Which evidence distinguishes no change from changes that cancel out?

## P5 — Separate updates break the shared rule

- **Concern:** [Dealing with Contention](../concepts/dealing-with-contention.md#cross-row-invariants) — never spoken aloud.
- **Symptom:** Two workers each see another worker available, then each removes itself; both transactions succeed and nobody remains available.
- **Looking for:** Identify the cross-row invariant and overlapping reads; use serializable execution with retries or guard a shared representation of that invariant. [S13]
- **Bar:** No seniority bar established by this source.
- **Follow-up if thin:** Are both writers changing the same row?

## P6 — The old owner wakes up

- **Concern:** [Dealing with Contention](../concepts/dealing-with-contention.md#reservations-across-a-wait) — never spoken aloud.
- **Symptom:** A reservation holder pauses past expiry, another request acquires the resource, then the original holder resumes.
- **Looking for:** A lease expiry does not stop an old process. Distinguish a stored reservation from transaction-scoped locking and do not claim that a plain TTL guarantees exclusivity. [S13]
- **Bar:** No seniority bar established by this source.
- **Follow-up if thin:** What does expiry change, and what does it fail to stop?

## P7 — More servers make no difference

- **Concern:** [Dealing with Contention](../concepts/dealing-with-contention.md#one-extremely-hot-resource) — never spoken aloud.
- **Symptom:** All users want one indivisible resource; extra application servers still pile up behind it.
- **Looking for:** Explain why sharding unrelated rows does not divide this conflict; consider requirement changes or per-resource sequential processing with throughput and failure limits. [S13]
- **Bar:** No seniority bar established by this source.
- **Follow-up if thin:** What bounds throughput if one worker processes every request?

## Coverage note

Score only the cited mechanisms in Looking for. Questions in the concept’s
Not covered by sources section have no answer key here. Do not infer a seniority
level from a deep dive or add mechanisms absent from the source.

## Sources

- **[S13]** Hello Interview — Dealing with Contention — <https://www.hellointerview.com/learn/system-design/patterns/dealing-with-contention> (user-supplied saved HTML, processed 2026-11-01).
