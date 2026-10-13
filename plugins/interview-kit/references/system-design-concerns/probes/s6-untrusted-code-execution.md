# Probe Seeds — S6

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

## P1 — the submission that took the service down

- **Concern:** `untrusted-code-execution.md` — never spoken aloud
- **Symptom:** One user's submission stalled the whole API tier for several minutes. During that
  window no other request, including plain page loads, was served. The submission itself was a few
  lines long.
- **Looking for:** Recognition that the submitted code ran in the same place as the service, with
  the three risks the source names: security (malicious code reaching data or the host),
  performance (CPU-intensive work), and isolation (a crash takes the service down with it) [S6]. A
  good answer moves execution into an isolated environment [S6].
- **Bar:** Mid-level — S6 expects the need for security and isolation to be understood at this
  level [S6].
- **Follow-up if thin:** Ask what else that same code could have done besides slowing things down.

## P2 — choosing where the code runs

- **Concern:** `untrusted-code-execution.md` — never spoken aloud
- **Symptom:** The team is comparing three candidate runtimes for submissions. One isolates
  strongly but takes a long time to start each instance. One starts quickly but shares the host
  kernel. One scales itself but is sometimes slow on the first request after a quiet period.
- **Looking for:** The tradeoffs of VMs (heavy and slow to start, lifecycle cost), containers
  (lighter and faster to start, shared kernel needs hardening and resource limits, reusable per
  runtime), and serverless functions (automatic scaling, cold starts, resource limits) [S6]. The
  choice should be justified by stated conditions. The source picks containers because it expects
  little variance in volume and wants to avoid cold-start latency [S6].
- **Bar:** Senior — S6 expects the candidate to compare all three and justify the choice [S6].
- **Follow-up if thin:** Ask what would have to change about traffic for the choice to flip.

## P3 — the submission that phoned home

- **Concern:** `untrusted-code-execution.md` — never spoken aloud
- **Symptom:** A security review finds that a submission opened an outbound connection, another
  wrote files that a later run read, and a third ran until it was killed by hand.
- **Looking for:** The hardening measures: a read-only code directory with a disposable output
  location, CPU and memory bounds, an explicit timeout tied to the latency target, no network
  access, and restricted system calls [S6]. Naming them at a high level is enough unless pushed
  [S6].
- **Bar:** Senior — S6 places the detailed discussion of secure, isolated execution at senior
  [S6].
- **Follow-up if thin:** Ask how the timeout relates to the response-time requirement.

## P4 — the leaderboard that slows everything

- **Concern:** `live-ranking.md` — never spoken aloud
- **Symptom:** During a timed event, database CPU climbs steadily as more participants join, and
  every other page gets slower. The busiest query groups and sorts all results for the event, and it
  runs several times per second.
- **Looking for:** Recognition that recomputing the ranking on each poll does not scale [S6]. A
  good answer progresses from a periodically refreshed cached ranking (fresh only to the refresh
  interval) to a score-ordered in-memory structure updated whenever a result is written and read
  directly on each poll [S6].
- **Bar:** Senior — S6 expects senior candidates to anticipate bottlenecks in their own design
  [S6].
- **Follow-up if thin:** Ask what the cached version gives up and what that costs users near the end
  of the event.

## P5 — "make the leaderboard live"

- **Concern:** `propagating-changes-to-clients.md` — never spoken aloud
- **Symptom:** A product manager wants the ranking to feel live. Users already see it update
  every five seconds, and nobody has complained about the delay. A teammate has started building a
  persistent-connection service for it.
- **Looking for:** A case that polling a cheap-to-read structure is enough, given a modest user
  count and an acceptable delay, and that a persistent connection is not wrong but is overkill
  [S6]. A strong answer treats cadence as a tunable, for example polling faster near the end of the
  event and slower otherwise [S6].
- **Bar:** Staff+ — S6 names knowing the complex option and explaining why it is overkill as the
  staff-level balance [S6].
- **Follow-up if thin:** Ask what would have to be true before the persistent connection paid for
  itself.

## P6 — 1,667 cores

- **Concern:** `scaling-compute-bound-work.md` — never spoken aloud
- **Symptom:** The plan for an event is to move the execution workers onto the largest instance
  available. Expected peak: ten thousand submissions at once, each with around a hundred test cases.
- **Looking for:** The arithmetic: submissions × test cases × time per case, converted to cores for
  a target window, compared with the few hundred vCPUs of the largest instance [S6]. A good answer
  also names the idle-capacity cost of a large machine between peaks, and moves to dynamic
  horizontal scaling, with over-provisioning as its stated risk [S6].
- **Bar:** Senior — S6 expects senior candidates to address bottlenecks and justify tradeoffs [S6].
- **Follow-up if thin:** Ask them to state the per-case time they assumed and how conservative it
  is.

## P7 — submissions lost in a spike

- **Concern:** `asynchronous-work-queue.md` — never spoken aloud
- **Symptom:** At the start of an event, some users see their submissions spin and then vanish. The
  logs show workers that crashed mid-run, and the submissions they held were never retried.
- **Looking for:** A buffer between the request handler and the workers that absorbs spikes,
  prevents loss, and allows a failed item to be requeued and retried [S6]. A good answer accepts
  that the flow becomes asynchronous and adds a status endpoint the client polls [S6].
- **Bar:** Senior — S6 expects senior candidates to address system reliability [S6].
- **Follow-up if thin:** Ask what the client sees between submitting and getting a result.

## P8 — is the buffer worth it?

- **Concern:** `asynchronous-work-queue.md` — never spoken aloud
- **Symptom:** The candidate's design has a buffer in front of the workers. Measured peak traffic
  is a fraction of worker capacity, and every event requires registration days in advance.
- **Looking for:** An honest weighing. On volume, the buffer is probably overengineering, and known
  peaks allow scaling ahead [S6]. Retries on worker failure can still justify it [S6]. The source
  says there is no single right answer and that the weighing is what matters [S6].
- **Bar:** Staff+ — S6 expects staff candidates to keep the system simple, with a path to scale,
  and to know why the more complex option is likely overkill [S6].
- **Follow-up if thin:** Ask which justification survives if the volume argument is removed.

## P9 — the same test, eleven times

- **Concern:** `cross-runtime-test-harness.md` — never spoken aloud
- **Symptom:** Adding one problem takes a week, because its expected results have to be written
  again for every supported language. Last month, two languages disagreed on the expected output of
  the same case.
- **Looking for:** One language-neutral test set per problem, a standard serialization per data
  structure, and a per-language harness that deserializes inputs, calls the user's code, and
  compares the result [S6].
- **Bar:** Senior — S6 expects senior candidates to explain how test cases actually run [S6].
- **Follow-up if thin:** Ask how a tree would be passed to a function written in two different
  languages.

## P10 — the user who solved everything in one second

- **Concern:** `client-authority-and-verification.md` — never spoken aloud
- **Symptom:** The top of the ranking shows a user credited with solves at times before the event
  started, and another with submissions recorded under someone else's account.
- **Looking for:** Identity taken from the session or token rather than from request parameters,
  and timestamps generated by the server, because client data can be manipulated [S6].
- **Bar:** Mid-level — S6 expects clearly defined API endpoints at this level and calls
  client-supplied identity or timestamps a red flag [S6].
- **Follow-up if thin:** Ask which fields in each request the server could work out for itself.

## P11 — a team of four, five services

- **Concern:** `service-and-data-boundaries.md` — never spoken aloud
- **Symptom:** A small team runs a system with a few hundred thousand users split across five
  separately deployed services. Most of the team's time goes into keeping the deployments in step.
- **Looking for:** Recognition that, for a small system, a single deployable unit may fit better,
  because the overhead of several services is not worth it [S6].
- **Bar:** Staff+ — S6 asks staff candidates for a very simple system free of overengineering [S6].
- **Follow-up if thin:** Ask what would have to grow before splitting paid off.

## P12 — designing for traffic that never comes

- **Concern:** `requirements-scoping.md` — never spoken aloud
- **Symptom:** The requirements give a user base in the hundreds of thousands and a catalog of a
  few thousand items. The proposed design has persistent connections, a buffer in front of every
  tier, and separate services for each noun.
- **Looking for:** Using the small stated scale as a design input that licenses simpler choices
  [S6], and checking that each requirement has an endpoint and each endpoint has a defined data
  flow before going deep [S6].
- **Bar:** Staff+ — S6 asks for a very simple system with a clear path to scale [S6].
- **Follow-up if thin:** Ask which component they would remove first and what would tell them to
  add it back.

## Coverage note

Concerns S6 does **not** establish a bar for. Do not probe or score these from this source:

- **Authentication, user profiles, payments, analytics, social features.** Declared out of scope
  [S6].
- **Fault tolerance, backups, CI/CD, secure purchase transactions.** Declared out of scope as
  non-functional requirements [S6].
- **Database engine choice.** S6 names one with only a thin reason and says either kind would work
  [S6].
- **Pagination method.** S6 pages lists but gives no reasoning for its scheme [S6].
- **Consistency.** S6 ranks availability over consistency but never develops what that means for
  its design [S6].
- **Retry limits, duplicate execution, and dead-lettering.** S6 names retries as the reason for its
  queue but says nothing about how they are bounded [S6].
- **Observability, rate limiting, multi-region deployment.** Not discussed [S6].

Two scoping rules specific to this source:

- **Do not penalize the absence of a buffer in front of the workers.** S6 calls it a judgement call
  with no right or wrong answer [S6]. Score the weighing, not the presence of the component.
- **S6 says it does not usually ask this problem at staff+** [S6]. Treat the staff-level seeds above
  as conditional, and grade them only when the interview was explicitly run at that level.

## Sources

- **[S6]** Hello Interview — Design a Coding Platform Like LeetCode —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/leetcode>
