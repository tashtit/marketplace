# Level Expectations

What interviewers expect at each seniority level, as stated by sources. These are the bars the
interviewer and evaluator skills grade against.

The recurring axis across levels is **not knowledge but initiative**: the same concept appears
at multiple levels, distinguished only by whether the candidate raised it unprompted [S1].

## Why prompting is the axis

S1 states the distinction explicitly in its own wording:

- Mid-level: "**with some prompting**, you should recognize that a cache would help" [S1].
- Senior: articulate tradeoffs "**without much prompting**"; "**drive the conversation**" [S1].
- Staff+: discuss production concerns "**without being prompted**" [S1].

The same concept — caching — is a pass at mid-level when prompted and a miss at staff level if
it needed prompting [S1]. So *who raised it first* is the measurement, not whether it appears in
the final design.

This is why an evaluation that only inspects the finished artifact cannot grade level: the
artifact is identical either way.

S2 states the same axis in its own terms, and adds one clarification about what "prompted" means
at mid-level: the interviewer's probing question is expected, and the candidate is graded on
whether they can **reason through it via back and forth** — not on whether they arrive at the
answer alone [S2]. At staff+, S2 sets the ceiling on interviewer involvement rather than the
floor: "your interviewer should intervene only to focus, not to steer" [S2].

## S1 — identifier-mapping system (entry-level problem)

S1 describes this class of problem as entry-level while noting that does not make it trivial
[S1].

### Mid-level [S1]

- Produce a working high-level design covering the core create and retrieve flows.
- Understand the basic flow end to end: submit, generate identifier, store the mapping, resolve
  on retrieval.
- Recognize that identifier generation must **guarantee uniqueness**, and propose at least one
  reasonable approach (hashing or counter-based).
- Understand why the non-cacheable redirect is used — the source explicitly allows not knowing
  the status code number itself, as long as the reasoning is understood.
- Discuss basic database indexing.
- Recognize *with prompting* that a cache would help, given the read-heavy nature.

### Senior [S1]

Everything above, plus:

- **Drive the conversation** and proactively identify the key challenges: identifier generation
  at scale, fast lookups, horizontal scaling.
- Articulate the tradeoff between hashing (collision handling) and counters (coordination
  overhead) without much prompting.
- Discuss caching strategies **in detail, including invalidation for expired records**.
- Propose a database choice **and justify it**.
- Recognize that separating read and write services follows from the asymmetric workload.
- Understand how to scale a shared counter across multiple write instances.

### Staff+ [S1]

Everything above, plus:

- **See past the textbook solution** to real production concerns.
- Recognize the read-heavy nature **quickly, and structure the design accordingly from the
  start** — not as a later optimization.
- Proactively discuss multi-region deployment, counter range allocation, and **what happens
  during failover of the counter store** — unprompted, if the batching approach was taken.
- Understand the security implications of predictable identifiers and propose mitigations where
  relevant.
- Demonstrate **product thinking**: custom alias collision prevention, expiry cleanup
  strategies, and how the system would evolve as requirements change.
- Show you have thought about **operating and maintaining** the system at scale, not just
  solving the problem.

## S2 — large-payload storage and sync (easy-rated problem)

S2 rates this problem class **easy** [S2]. It frames the levels on a breadth/depth split with
explicit ratios, which S1 does not [S2].

### Mid-level [S2]

- **Breadth over depth — "mostly focused on breadth (80% vs 20%)"** [S2]. A high-level design
  meeting the functional requirements, where many components are abstractions you have only
  surface-level familiarity with.
- Expect the interviewer to **probe the basics** to confirm you know what each component does —
  "the interviewer is not taking anything for granted with respect to your knowledge" [S2].
- **A mixture of driving and taking the backseat.** Drive the early stages; the interviewer does
  not expect you to "proactively recognize problems in your design with high precision", and it
  is reasonable that they take over and drive the later stages [S2].
- **The stated bar:** clearly defined API endpoints and data model, and a high-level design
  functional for upload, download, and sharing [S2].
- The source explicitly **does not expect** knowledge of presigned URLs, transferring directly
  to blob storage, or chunking at this level [S2].
- What it does expect: that when asked a probing question — its examples are *"You're uploading
  the file twice right now, how can we avoid that?"* and *"How can you show a user's progress
  while allowing them to resume an upload?"* — the candidate **can reason through the problem and
  come to a solution via some back and forth** [S2].

### Senior [S2]

- **"About 60% breadth and 40% depth"** — in-depth knowledge in areas of hands-on experience
  [S2].
- **Advanced system design:** using blob storage for large payloads, implementing a CDN for
  faster downloads, and discussing the tradeoffs of different choices with justification from
  experience [S2].
- **Articulating architectural decisions** — pros and cons, and their impact on scalability,
  performance, and maintainability [S2].
- **Problem-solving and proactivity:** anticipating challenges, suggesting improvements,
  identifying and addressing bottlenecks [S2].
- **The stated bar:** move quickly through the high-level design in order to spend time on the
  large-payload problem in detail; be **more proactive than a mid-level candidate**, thinking
  through several options and arriving at a reasonable solution [S2].
- Speaking directly to specific APIs such as multipart upload is **"not strictly required"**, but
  many candidates with file-upload experience will [S2].

### Staff+ [S2]

- **"About 40% breadth and 60% depth"** — the inverse of mid-level [S2].
- The framing is experience, not novelty: "while you may not have solved this particular problem
  before, you have solved enough problems in the real world to be able to confidently design a
  solution backed by your experience" [S2].
- **Breeze through the small stuff.** The interviewer already assumes REST APIs and data
  normalization, so cover them at a high level to leave time for what is interesting [S2].
- **"An exceptional degree of proactivity"** — identify and solve issues independently,
  anticipating problems rather than responding to them. The source's test is sharp: **"Your
  interviewer should intervene only to focus, not to steer."** [S2]
- **Practical application of technology:** your experience guides the conversation, showing how
  tools are configured in real-world scenarios [S2].
- **The stated bar:** delve deeply into the deep-dive topics, and possibly **steer the
  conversation** toward a topic you find particularly relevant; hold a solid understanding of
  tradeoffs between solutions and articulate them **"treating the interviewer as a peer"** [S2].

## S3 — high-contention reservation and booking (contention problem)

S3 uses the same breadth/depth ratios and the same three headings as S2, so those are not repeated
here; what follows is what S3 states distinctly [S3].

### Mid-level [S3]

- **Breadth over depth — "mostly focused on breadth (80% vs 20%)"** [S3], with many components
  being abstractions the candidate has only surface-level familiarity with.
- Expect the interviewer to **probe the basics** — its example is being asked what an API gateway
  does and how it works at a high level; "the interviewer is not taking anything for granted with
  respect to your knowledge" [S3].
- **A mixture of driving and taking the backseat.** Drive the early stages; the interviewer does
  not expect you to "proactively recognize problems in your design with high precision", so it is
  reasonable that they take over and drive the later stages while probing your design [S3].
- **The stated bar:** clearly defined API endpoints and data model, and a high-level design that
  is functional for **at least** the viewing and the booking requirements [S3].
- On the central contention problem, solving it with **"at least the 'Good Solution'"** — the
  status field, timeout, and sweep job — is sufficient [S3]. See
  `concepts/preventing-double-allocation.md`; the derived-status and distributed-lock solutions are
  *above* this bar.
- **"Any additional depth would be a bonus, but further deep dives wouldn't be expected"** [S3].

### Senior [S3]

- **"About 60% breadth and 40% depth"** — in-depth knowledge where you have hands-on experience
  [S3].
- **Advanced system design.** S3 is unusually specific about which knowledge is not optional here:
  knowing to use a **search-optimized data store** for the search requirement is **"essential"**
  [S3]. Understanding a **distributed lock** for the hold, and discussing detailed scaling
  strategies including sharding and replication, is also expected [S3].
- **The prompting hedge is explicit and narrower than at staff+:** on the scaling discussion,
  **"it's ok if this took some probing/hints from the interviewer"** [S3]. Needing a hint does not
  cost a senior candidate the bar on that topic.
- **Articulating architectural decisions** — pros and cons, and their impact on scalability,
  performance, and maintainability, with the tradeoffs justified [S3].
- **Problem-solving and proactivity:** anticipating challenges, suggesting improvements,
  identifying and addressing bottlenecks, ensuring reliability [S3].
- **The stated bar:** **speed through the initial high-level design** to spend time on, in detail,
  optimizing search, solving the no-double-booking problem (**"landing on a distributed lock or
  other quality solution"**), and **"even have a discussion on handling popular events"** [S3].

### Staff+ [S3]

- **"About 40% breadth and 60% depth"** [S3], framed as experience rather than novelty: you may
  not have solved this problem before, but have solved enough real problems to design a solution
  backed by that experience [S3].
- **Know which technologies to use in practice, not just in theory**, drawing on past experience
  to explain how they would be applied [S3]. **Breeze through the small stuff** — REST APIs, data
  normalization — since the interviewer already assumes it [S3].
- **"An exceptional degree of proactivity"** — identify and solve issues independently,
  anticipating problems rather than only responding to them [S3].
- **The stated bar:** **diving deep into at least 2-3 key areas**, showing not just proficiency
  but **"innovative thinking and optimal solution-finding abilities"** [S3].
- **The measure S3 gives for this level is about the interviewer, not the candidate:** a crucial
  indicator is the level of insight brought, and "a good measure for this is if the interviewer
  comes away from the discussion having gained new understanding or perspectives" [S3].

## S4 — geographically distributed availability and claiming (read-scaling problem)

S4 uses the same breadth/depth ratios and the same headings as S2 and S3, so those are not repeated
here; what follows is what S4 states distinctly [S4]. Like S2, S4 rates its own problem class
**easy** [S4], which is context for how modest its bars are.

### Mid-level [S4]

- **Breadth over depth — "80% breadth and 20% depth"** [S4].
- **A high-level design that meets the functional requirements is the deliverable**, and S4 is
  explicit that **"the optimality of your solution will be icing on top rather than the focus"**
  [S4].
- Expect the interviewer to **probe the basics** to confirm you know what each component does — its
  example is being asked which indexes are available to you if you name a particular datastore; the
  interviewer "will not be taking anything for granted with respect to your knowledge" [S4].
- **A mixture of driving and taking the backseat**, with the same wording as S3: drive the early
  stages, but the interviewer does not expect you to "proactively recognize problems in your design
  with high precision" and may drive the later stages [S4].
- **The stated bar:** clearly defined API endpoints and data model, and **both** routes built — the
  availability read and the claim write [S4].
- **On a candidate choosing a "Bad" solution, the interviewer expects a good discussion but not
  that the candidate immediately jumps to a great (or sometimes even good) solution** [S4]. This is
  a *lower* bar than S3 sets on its central problem, where at least the good solution was required.

### Senior [S4]

- **"About 60% breadth and 40% depth"** — in-depth knowledge where you have hands-on experience
  [S4].
- **Advanced system design, stated as recognition rather than knowledge.** S4 names the two things
  that **"should jump out to experienced engineers"** on this problem: **read volume** and
  **trivial partitioning** [S4]. The expectation is having reasonable solutions for them — see
  `concepts/read-heavy-workloads.md` and `concepts/partitioning-by-query-locality.md`.
- **Articulating architectural decisions** — pros and cons and their impact on scalability,
  performance, and maintainability, with the tradeoffs justified [S4].
- **Problem-solving and proactivity:** anticipating challenges, suggesting improvements,
  identifying and addressing bottlenecks, ensuring reliability [S4].
- **The stated bar:** **speed through the initial high-level design** so the time goes to
  optimizing the critical paths — specifically, optimized solutions for **both** the atomicity of
  the claim path **and** the scaling of the read path [S4].

### Staff+ [S4]

- **"About 40% breadth and 60% depth"**, framed as "been there, done that" expertise [S4].
- **Know which technologies to use in practice, not just in theory** [S4]. **Breeze through the
  small stuff** — S4 names REST APIs and data normalization — since the interviewer already assumes
  it, so the time goes to what is interesting [S4].
- **"An exceptional degree of proactivity"** — identify and solve issues independently, anticipating
  problems and implementing preemptive solutions rather than only responding [S4].
- **Practical application of technology:** your experience should guide the conversation, showing how
  tools are configured in real-world scenarios to meet specific requirements [S4].
- **Complex problem-solving and decision-making**, weighing scalability, performance, reliability,
  and maintenance [S4].
- **Advanced design and scalability under high load**, including distributed systems, load
  balancing, and caching strategies [S4].
- **The stated bar:** **diving deep into at least 2-3 key areas**, with **unique insights for at
  least a couple of follow-up questions of increasing difficulty** [S4].
- **The same interviewer-side measure as S3:** a crucial indicator is the insight brought, measured
  by whether the interviewer comes away having gained new understanding or perspectives [S4].

## S5 — social feed generation (fan-out problem)

S5 uses the same breadth/depth ratios and headings as S2, S3 and S4, so those are not repeated here;
what follows is what S5 states distinctly [S5]. S5 rates its own problem class **medium** [S5],
a step above S2's and S4's **easy** [S2][S4].

### Mid-level [S5]

- **"80% vs 20%" breadth over depth**, with the acknowledgement that many components will be
  **abstractions you have only surface-level familiarity with** [S5]. S5 is the source that states
  this most plainly: surface familiarity is expected at this level, not hidden.
- **Probing the basics**, with the same wording as S4 — the interviewer is **"not taking anything
  for granted with respect to your knowledge"** and may ask what a named component does and how it
  works at a high level [S5].
- **A mixture of driving and taking the backseat**: drive the early stages, but you are not
  expected to **"proactively recognize problems in your design with high precision"**, so the
  interviewer may take over and drive the later stages [S5].
- **The stated bar:** clearly defined API endpoints and data model, plus a high-level design that is
  functional and meets the requirements [S5].
- **On solution tiers:** the candidate **may have some of the "Good" solutions**, and would **not be
  expected to cover all the possible scaling edge cases in the deep dives** [S5]. This sits between
  S4 (a "Bad" solution is tolerable given a good discussion) and S3 (at least the "Good" solution
  was required) — a third distinct calibration of the same axis [S3][S4][S5].

### Senior [S5]

- **"About 60% breadth and 40% depth"**, with depth expected where you have hands-on experience
  [S5].
- **One named body of knowledge is called essential:** **"knowing approaches for handling fan-out
  is essential"** [S5]. This is the second source to mark a specific topic essential at senior
  rather than merely expected [S3][S5]. See `concepts/fan-out-on-read-vs-write.md`.
- **Iteratively diagnose performance bottlenecks and suggest improvements** — stated as an iterative
  activity, not a one-off identification [S5].
- **Articulating architectural decisions**: pros and cons and their impact on scalability,
  performance, and maintainability, with the tradeoffs justified [S5].
- **Problem-solving and proactivity**: anticipating challenges, identifying and addressing
  bottlenecks, optimizing performance, ensuring reliability [S5].
- **The stated bar:** **speed through the initial high-level design** in order to discuss **at least
  2 of the deep dives in detail**, and **proactively surface some of the potential issues** around
  fan-out and performance bottlenecks [S5].

### Staff+ [S5]

- **"About 40% breadth and 60% depth"**, framed as having solved enough problems in the real world
  to design a solution backed by experience even for a problem you have not seen [S5].
- **Breeze through the small stuff** — S5 names REST APIs and data normalization, the same examples
  as S4 — because the interviewer already assumes it [S4][S5].
- **"An exceptional degree of proactivity"**, including **preemptive** solutions rather than only
  responses, and the same ceiling on interviewer involvement as S2: the interviewer **"should
  intervene only to focus, not to steer"** [S2][S5].
- **Practical application of technology**: knowing which technologies to use in practice, with
  experience guiding the conversation [S5].
- **Complex problem-solving and decision-making**, weighing scalability, performance, reliability,
  and maintenance [S5].
- **Advanced design and scalability under high load**, including distributed systems, load
  balancing, and caching strategies [S5].
- **The stated bar:** **likely cover all of the deep dives — and/or some the source did not
  enumerate** — surface potential issues, and **talk about performance tuning** [S5]. The
  "and/or some that we haven't enumerated" clause is the distinct part: at this level the enumerated
  list is a floor, not the scope.

## Using these bars

- **Grade the highest bar cleared, not the concepts touched.** Staff+ requires the read-heavy
  recognition to shape the design from the start; discovering it late is senior behavior even
  if the end state matches [S1].
- **A prompted answer scores at the level where prompting is permitted**, not at the level where
  the concept appears [S1].
- **Absence of a concern is not automatically a miss.** S1 qualifies two staff items with "if
  relevant" and "if you took the counter batching approach" — a concern that does not apply to
  the design cannot be graded against it [S1]. S2 does the same with "not strictly required" for
  naming specific APIs [S2].
- **Match the bar to the problem class.** The S1, S2, S3, S4 and S5 bars are stated for their own
  problem classes and their concrete "The Bar for…" bullets do not transfer; the breadth/depth
  ratios and the prompting axis do [S1][S2][S3][S4][S5].
- **Weigh the bar against the problem's stated difficulty.** S4 rates its own problem easy and sets
  a correspondingly forgiving mid-level bar — tolerating a "Bad" solution given a good discussion —
  where S3 required at least its good solution on the equivalent concern [S3][S4]. A bar is relative
  to the problem it was written for. S5 also rates itself medium, and its mid-level tolerance sits
  between the two: some of the "Good" solutions, and no requirement to cover every scaling edge
  case [S5]. Note that stated difficulty does not by itself predict the bar — S3 and S5 share the
  same rating but state different tolerances [S3][S5].
- **Note where a source names a specific solution tier as the bar.** S3 is the first source to
  grade a *named* solution as sufficient at a level ("at least the 'Good Solution'") and to call
  one piece of knowledge "essential" at senior [S3]. Where a source does this, the tier is the
  bar — do not silently promote a better solution into a requirement. S5 does both as well, naming
  fan-out approaches "essential" at senior [S5].
- **Treat an enumerated deep-dive list as a floor at staff+, not a scope.** S5 expects a staff
  candidate to cover the deep dives "and/or some that we haven't enumerated" [S5], and S4 sets its
  staff bar on the *number* of areas rather than on which ones [S4]. Covering the listed items
  completely is therefore not automatically a staff+ performance.

## Not covered by sources

- Bars for problem classes other than identifier-mapping systems, large-payload storage,
  high-contention reservation, geographically distributed availability, and social feed generation.
- How much weight each bullet carries relative to the others, or how many misses drop a level.
- What distinguishes staff from principal.
- How to grade a candidate who exceeds a bar on one axis and misses on another.
- How to measure the breadth/depth ratios S2 and S3 state, or what to do when a candidate hits
  the ratio but misses the stated bar.
- Which topics the senior-level "some probing/hints is ok" allowance covers beyond scaling, and
  whether it applies at staff+ at all.
- How an interviewer judges "innovative thinking", or whether gaining new understanding is
  required rather than indicative.
- How a problem's stated difficulty should adjust the bars quantitatively; S4 labels itself easy
  without saying what that changes.
- Whether S4's tolerance of a "Bad" solution at mid-level extends to its central claim path or only
  to its deep dives.
- How the difficulty ratings (easy, medium) map onto how much the bars should move; S5 labels
  itself medium without saying what that changes, and S3 shares that rating while stating a
  stricter tolerance.
- Which of S5's deep dives count toward the senior "at least 2" requirement, or whether any two
  suffice.
- What "surface-level familiarity" with a component looks like when probed, as opposed to
  insufficient knowledge.

## Sources

- **[S1]** Hello Interview — Design Bit.ly —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/bitly>
- **[S2]** Hello Interview — Design a File Storage Service Like Dropbox —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/dropbox>
- **[S3]** Hello Interview — Design Ticketmaster —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster>
- **[S4]** Hello Interview — Design a Local Delivery Service like Gopuff —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/gopuff>
- **[S5]** Hello Interview — Design Facebook's News Feed —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/fb-news-feed>
