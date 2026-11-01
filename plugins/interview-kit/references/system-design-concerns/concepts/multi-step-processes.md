# Multi-step Processes

## Recognize the coordination problem

- A sequence of service calls can lose progress after a crash, receive a callback on another host, or fail after earlier steps committed. Persisting progress alone still leaves work claiming, retries, and recovery to implement. [S11]
- Sagas commit local steps independently and use compensating actions when later steps fail. This permits temporary inconsistency; compensations can also fail and require retries, idempotency, and a human recovery path. [S11]
- Holding a distributed transaction open through long waits blocks participants and cannot include external services that do not participate in its protocol. [S11]

## Choreography or orchestration

- Choreography has workers react to durable events and emit the next events. It suits independent services and moderate complexity, but the implicit flow becomes difficult to inspect and change as contracts proliferate. [S11]
- Log consumers commit progress after handling events so replacements can resume. Handoffs can repeat processing, so workers need idempotency; adding workers is bounded by the partition count. [S11]
- Orchestration centralizes the sequence and its visibility. A workflow engine supplies durable progress and recovery, at the cost of another system to operate or a managed service's constraints. [S11]

## Recovery semantics

- In Temporal, deterministic workflow decisions replay against recorded activity results. External calls belong in activities, which must tolerate repeat attempts when the engine cannot tell whether an attempt finished. The server schedules and records work; worker processes run application code. [S11]
- Managed state-machine systems can persist the current execution position rather than replay application code. Their authoring and recovery models differ even when they serve similar coordination needs. [S11]
- An activity's successful side effect and its completion report are separate events. Recording IN_PROGRESS and COMPLETED around an external action narrows ambiguity but does not make the action atomic with the record; ambiguous attempts need reconciliation rather than blind repetition. [S11]

## Change, history, and waiting

- Version workflows so old executions retain their definition, or use replay-compatible migration logic. In-flight changes need explicit handling; a deployment alone does not safely insert a step into every running process. [S11]
- Keep large payloads outside workflow history and pass identifiers. Long-lived histories can hand current state to a new execution, such as Temporal Continue-as-New, without carrying the entire prior history. [S11]
- Signals and durable timers support human or webhook waits without holding a worker thread. Address the right execution by workflow ID. [S11]
- A single async task can use a queue instead; ordinary CRUD and high-frequency simple operations generally do not justify workflow-engine overhead. [S11]

## Not covered by sources

- How should reconciliation work when an external provider cannot report whether it performed an action?
- How should compensation conflicts between concurrent workflows be resolved?

## Sources

- **[S11]** Hello Interview — Multi-step Processes — <https://www.hellointerview.com/learn/system-design/patterns/multi-step-processes> (user-supplied saved HTML, processed 2026-11-01).
