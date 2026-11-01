# System Design Pattern Library

The interview answer key, extracted from complete Hello Interview pattern articles
supplied as saved HTML. It is plain data, not a selectable skill. Each concept
preserves source reasoning; probe symptoms are Tashtit-authored adaptations, not
quotations or source-defined interview questions.

## Concept index

| Concept | Consider it when | Sources |
| --- | --- | --- |
| [Scaling Reads](concepts/scaling-reads.md) | High read volume, expensive queries, or repeated access to the same data | S8 |
| [Scaling Writes](concepts/scaling-writes.md) | Write throughput exceeds a component’s capacity, traffic bursts, or a hot key dominates | S9 |
| [Managing Long Running Tasks](concepts/managing-long-running-tasks.md) | Work takes seconds or minutes, needs specialized hardware, or blocks the request tier | S10 |
| [Multi-step Processes](concepts/multi-step-processes.md) | Several services or human steps must coordinate through failures, retries, and long waits | S11 |
| [Real-time Updates](concepts/realtime-updates.md) | Users need timely events or shared state changes rather than occasional refreshes | S12 |
| [Dealing with Contention](concepts/dealing-with-contention.md) | Concurrent writers compete for the same resource or violate a shared invariant | S13 |
| [Handling Large Blobs](concepts/large-blobs.md) | Large uploads or downloads burden application servers or need resumability | S14 |

## Sources processed

Tags S1–S7 are retired with the removed walkthrough library. They MUST NOT be
reused. The replacement starts at S8 so historical citations cannot silently
refer to a different article. The next available tag is S15.

| Tag | Source | Date | Concepts touched |
| --- | --- | --- | --- |
| S8 | [Scaling Reads](https://www.hellointerview.com/learn/system-design/patterns/scaling-reads) | 2026-11 | scaling-reads |
| S9 | [Scaling Writes](https://www.hellointerview.com/learn/system-design/patterns/scaling-writes) | 2026-11 | scaling-writes |
| S10 | [Managing Long Running Tasks](https://www.hellointerview.com/learn/system-design/patterns/long-running-tasks) | 2026-11 | managing-long-running-tasks |
| S11 | [Multi-step Processes](https://www.hellointerview.com/learn/system-design/patterns/multi-step-processes) | 2026-11 | multi-step-processes |
| S12 | [Real-time Updates](https://www.hellointerview.com/learn/system-design/patterns/realtime-updates) | 2026-11 | realtime-updates |
| S13 | [Dealing with Contention](https://www.hellointerview.com/learn/system-design/patterns/dealing-with-contention) | 2026-11 | dealing-with-contention |
| S14 | [Handling Large Blobs](https://www.hellointerview.com/learn/system-design/patterns/large-blobs) | 2026-11 | large-blobs |

## Input verification

All seven requested patterns have been processed from complete article bodies
across the user-supplied saved-file versions. No patterns remain pending.
Filename mismatches were resolved using the main heading, body, and canonical
URL, rather than assigning claims to the filename's subject.

| Pattern | Saved input used |
| --- | --- |
| Scaling Reads | Initial file named Multi-step Processes; its body is Scaling Reads |
| Scaling Writes | File named How to scale writes; the file named How to scale reads duplicates this article |
| Managing Long Running Tasks | File named Managing Long Running Tasks |
| Multi-step Processes | Initial file named Dealing with Contention, before it was replaced; its body is Multi-step Processes |
| Real-time Updates | File named Real-time Updates |
| Dealing with Contention | Corrected file named Dealing with Contention |
| Handling Large Blobs | Corrected file named Handling Large Blobs |

The current files named How to scale reads and Multi-step Processes still contain
Scaling Writes and Scaling Reads respectively. Replacing the Contention save did
not change S11's provenance: it cites the complete earlier article body already
processed, not the later file at the same path. References are paraphrased
extractions, not copies of the downloaded HTML.

## Excluded material

For each processed source, navigation, marketing, player controls, quizzes,
reader comments, and linked walkthroughs were excluded. No linked problem
breakdowns were mined.

### Rejected from S8

- Collaborative editing algorithms: only a use-case signal; no mechanism taught.
- Absolute freshness from a cached version pointer: no pointer-freshness protocol supplied.

### Rejected from S9

- A guarantee of lossless dual writes: the migration outline does not explain partial-write recovery.
- Universal database throughput or flush settings: product-specific illustrative figures are not capacity guarantees.

### Rejected from S10

- Atomic duplicate admission: the example separates lookup and insertion without resolving races.
- Automatic recovery of pending records after enqueue failure: no recovery protocol stated.

### Rejected from S11

- Exactly-once network delivery: the source distinguishes repeat attempts from side-effect safety.
- Reconciliation against an unqueryable external provider: no mechanism supplied.

### Rejected from S12

- CRDT, operational-transform, and vector-clock algorithms: named without sufficient explanation.
- General networking tutorial: background outside this pattern's focused answer key.

### Rejected from S13

- Cross-store transactions and multi-writer replication algorithms: explicitly outside the article's scope.
- Exclusive action guaranteed by a TTL lease: the source explicitly describes overlapping holders after a pause.
- ABA detection from comparing all business fields: the source does not explain the case where every compared field returns to its original value.

### Rejected from S14

- Universal upload-size thresholds and provider part-size limits: illustrative, provider-dependent details rather than guarantees.
- Uniform support for signed size/type conditions across every upload API: not established by the article.
- Duplicate-event processing and immediate revocation: no mechanism supplied.

## Assessment resources

- [Probe seeds](probes/): one file per pattern, named `<pattern>.md` without a
  source-number prefix. Select relevant patterns, potentially more than one per
  attempt. Citations retain source tags and each file starts its probes at P1.
- [Level expectations](level-expectations.md): only source-stated, narrowly scoped seniority observations.
- [Evaluation rubric](rubric.md): Tashtit convention for implementation evidence, not a source-defined seniority ladder.
