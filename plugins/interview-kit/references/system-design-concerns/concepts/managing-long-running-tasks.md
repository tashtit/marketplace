# Managing Long Running Tasks

## Acceptance and processing

- Separate quick validation and acknowledgment from expensive execution. Return a job ID, let workers consume a durable queue, and persist job status/results for polling or completion notifications. [S10]
- Web servers and workers scale independently and can use different hardware. This improves response time and fault isolation, but adds queues, eventual completion, status storage, and operational monitoring. [S10]
- Queue messages can carry job IDs while larger job details live in a database. Durability and operational burden matter: the source contrasts memory-first Redis queues with durable managed or broker alternatives, and notes replay and partition ordering in Kafka. [S10]
- Ordinary worker servers give control and support long tasks but cost idle capacity. Serverless suits spiky demand but imposes execution and environment limits; containers add orchestration complexity for more flexibility. [S10]

## Failures and duplicate work

- Detect abandoned jobs through the queue's failure-detection or visibility mechanism. Long intervals delay recovery; short ones add traffic or falsely suspect a paused worker. [S10]
- Bound retries and move repeatedly failing jobs to a dead-letter queue. Monitor it and investigate before replaying jobs; otherwise poison inputs consume capacity needed by healthy work. [S10]
- Use an operation identity to return an existing job rather than submitting duplicate work. Make execution itself safe to retry because a worker may fail after partial progress. [S10]

## Capacity and scheduling

- Bound queue depth and reject new work with a busy response when workers cannot keep up. Scale workers using queue depth rather than relying only on CPU. [S10]
- Separate fast and slow workloads into queues with appropriate worker pools, or split large jobs into smaller units, to reduce head-of-line blocking. [S10]
- Simple dependent jobs can enqueue their next step with enough context for independent retries. Complex branching and parallel dependencies justify an orchestrator; see [multi-step processes](multi-step-processes.md) for recovery and compensation. [S10][S11]

## Source limits

The submission example checks for an existing key before creating a job, but does not establish atomic admission under simultaneous submissions. Its pending-record/queue sequence also does not explain how an enqueue failure is recovered. These are gaps, not guarantees supplied by this article. [S10]

## Not covered by sources

- How should concurrent submissions atomically claim one operation identity?
- How should a pending database record be reconciled after enqueueing fails?
- How should cancellation interrupt an already running task?

## Sources

- **[S10]** Hello Interview — Managing Long Running Tasks — <https://www.hellointerview.com/learn/system-design/patterns/long-running-tasks> (user-supplied saved HTML, processed 2026-11-01).
- **[S11]** Hello Interview — Multi-step Processes — <https://www.hellointerview.com/learn/system-design/patterns/multi-step-processes> (user-supplied saved HTML, processed 2026-11-01).
