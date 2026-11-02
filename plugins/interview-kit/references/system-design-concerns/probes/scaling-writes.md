# Probe Seeds — Scaling Writes

Tashtit-authored scenarios derived from [S9]. Adapt them to the named attempt;
never speak the Concern or Looking for fields before the debrief.

Technical criteria come from the linked concept. Seniority is assessed only where
[level expectations](../level-expectations.md) explicitly supplies a bar.

## P1 — A quiet shard and a busy shard

- **Concern:** [Scaling Writes](../concepts/scaling-writes.md#distribute-work-deliberately) — never spoken aloud.
- **Symptom:** Adding database nodes leaves one node overloaded and most nearly idle.
- **Looking for:** Inspect key distribution and common read locality before choosing a new partition key; explain routing. [S9]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** How many nodes must the most common read contact?

## P2 — Accepted but never finished

- **Concern:** [Scaling Writes](../concepts/scaling-writes.md#bursts-and-sustained-overload) — never spoken aloud.
- **Symptom:** The service accepts requests quickly, but pending writes grow every hour even after a traffic spike ends.
- **Looking for:** A queue hides sustained capacity shortage; acceptance is not database completion. Explain capacity and whether requirements allow delay or selective rejection. [S9]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** What must be true for the backlog to drain?

## P3 — A batch with no savings

- **Concern:** [Scaling Writes](../concepts/scaling-writes.md#reduce-the-number-of-writes) — never spoken aloud.
- **Symptom:** A minute of buffering adds delay but barely reduces database operations.
- **Looking for:** Batch benefit depends on per-entity event density; replayability determines the crash risk of buffering acknowledged work. [S9]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** How many repeated updates reach one entity inside that minute?

## P4 — One counter saturates a node

- **Concern:** [Scaling Writes](../concepts/scaling-writes.md#reduce-the-number-of-writes) — never spoken aloud.
- **Symptom:** One item receives more increments than an entire database node can process.
- **Looking for:** Split an aggregatable value across subkeys, combine reads, and keep readers aware of the split; explain read amplification. [S9]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** Would the same approach preserve an indivisible profile update?

## Coverage note

Score only the cited mechanisms in Looking for. Questions in the concept’s
Not covered by sources section have no answer key here. Do not infer a seniority
level from an article heading, a deep dive, or the difficulty of this scenario.

## Sources

- **[S9]** Hello Interview — Scaling Writes — <https://www.hellointerview.com/learn/system-design/patterns/scaling-writes> (user-supplied saved HTML, processed 2026-11-01).
