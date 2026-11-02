# Probe Seeds — Managing Long Running Tasks

Tashtit-authored scenarios derived from [S10]. Adapt them to the named attempt;
never speak the Concern or Looking for fields before the debrief.

Technical criteria come from the linked concept. Seniority is assessed only where
[level expectations](../level-expectations.md) explicitly supplies a bar.

## P1 — The request times out

- **Concern:** [Managing Long Running Tasks](../concepts/managing-long-running-tasks.md#acceptance-and-processing) — never spoken aloud.
- **Symptom:** A report takes minutes, and impatient clients submit it again while ordinary API requests slow down.
- **Looking for:** Acknowledge with a job ID, queue execution separately, track status, and separate worker scaling from request handling. [S10]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** What can the user do after the initial response?

## P2 — One input stops progress

- **Concern:** [Managing Long Running Tasks](../concepts/managing-long-running-tasks.md#failures-and-duplicate-work) — never spoken aloud.
- **Symptom:** Workers repeatedly fail on the same input while valid jobs wait.
- **Looking for:** Bound retries, isolate the job in a monitored dead-letter queue, and investigate before replaying. [S10]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** What happens after the retry budget is exhausted?

## P3 — The job ran twice

- **Concern:** [Managing Long Running Tasks](../concepts/managing-long-running-tasks.md#failures-and-duplicate-work) — never spoken aloud.
- **Symptom:** A worker stops after part of its work and a replacement repeats it; the user sees two side effects.
- **Looking for:** Explain safe retry of the work itself in addition to deduplicating submissions; do not claim the source proves atomic admission. [S10]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** Is returning an existing job ID enough once execution has started?

## P4 — Fast requests wait for hours

- **Concern:** [Managing Long Running Tasks](../concepts/managing-long-running-tasks.md#capacity-and-scheduling) — never spoken aloud.
- **Symptom:** Short tasks sit behind hours-long tasks and the waiting list keeps growing.
- **Looking for:** Separate workloads or split tasks, bound acceptance, and scale workers against queue depth. [S10]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** Which metric tells you accepted work is falling behind?

## Coverage note

Score only the cited mechanisms in Looking for. Questions in the concept’s
Not covered by sources section have no answer key here. Do not infer a seniority
level from an article heading, a deep dive, or the difficulty of this scenario.

## Sources

- **[S10]** Hello Interview — Managing Long Running Tasks — <https://www.hellointerview.com/learn/system-design/patterns/long-running-tasks> (user-supplied saved HTML, processed 2026-11-01).
