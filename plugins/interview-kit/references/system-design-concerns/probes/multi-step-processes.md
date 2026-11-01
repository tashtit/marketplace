# Probe Seeds — Multi-step Processes

Tashtit-authored scenarios derived from [S11]. Adapt them to the named attempt;
never speak the Concern or Looking for fields before the debrief.

Technical criteria come from the linked concept. Seniority is assessed only where
[level expectations](../level-expectations.md) explicitly supplies a bar.

## P1 — Paid but unfinished

- **Concern:** [Multi-step Processes](../concepts/multi-step-processes.md#recognize-the-coordination-problem) — never spoken aloud.
- **Symptom:** A process dies after payment and inventory confirmation, before dispatch. Restarting loses its place.
- **Looking for:** Durable progress, safe retries, and either forward resumption or compensations; explain that compensations themselves can fail. [S11]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** What survives the process, and how does the replacement choose its next step?

## P2 — Success without a receipt

- **Concern:** [Multi-step Processes](../concepts/multi-step-processes.md#recovery-semantics) — never spoken aloud.
- **Symptom:** An external action succeeds but its completion report never reaches the coordinator.
- **Looking for:** Repeated attempts are possible; idempotency and reconciliation handle ambiguous effects. A local key check alone cannot make an external effect atomic. [S11]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** What should a retry do with an operation still marked in progress?

## P3 — A deployment changes the sequence

- **Concern:** [Multi-step Processes](../concepts/multi-step-processes.md#change-history-and-waiting) — never spoken aloud.
- **Symptom:** Thousands of executions are paused midway when a new required step is deployed.
- **Looking for:** Version old/new workflows or explicitly migrate compatibly with history; distinguish replay engines from pinned state-machine definitions. [S11]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** Which version resumes an execution that passed this point yesterday?

## P4 — Waiting consumes the fleet

- **Concern:** [Multi-step Processes](../concepts/multi-step-processes.md#change-history-and-waiting) — never spoken aloud.
- **Symptom:** Approvals can take weeks and the design holds a worker open for each one.
- **Looking for:** Persist waiting state and use signals plus durable timers; pass identifiers rather than large payloads through history. [S11]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** How does a callback find the execution after its original host disappears?

## Coverage note

Score only the cited mechanisms in Looking for. Questions in the concept’s
Not covered by sources section have no answer key here. Do not infer a seniority
level from an article heading, a deep dive, or the difficulty of this scenario.

## Sources

- **[S11]** Hello Interview — Multi-step Processes — <https://www.hellointerview.com/learn/system-design/patterns/multi-step-processes> (user-supplied saved HTML, processed 2026-11-01).
