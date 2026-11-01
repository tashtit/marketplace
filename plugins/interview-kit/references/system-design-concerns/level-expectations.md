# Level Expectations

Only explicit seniority statements from the replacement pattern sources belong
here. Deep dives are technical answer criteria, not implicit seniority bars.
These statements do not establish a complete mid/senior/staff ladder for an
entire implementation. Do not generalize them across patterns.

## S9 — scaling writes

The source associates familiarity with hardware limits and making the case for
vertical capacity with staff+ candidates. It specifically expects staff-level
candidates to examine batching efficacy: a one-minute window offers no reduction
for entities receiving one event an hour. These are scoped observations, not a
global staff assessment. [S9]

## S11 — multi-step processes

- **Mid-level:** recognizing the need for a workflow engine and naming one is
  usually enough, according to the source. Preserve “usually”; this is not an
  unconditional requirement for every design. [S11]
- **Senior and staff:** defend the choice, walk through failure handling and
  compensation, and handle the article's deep dives. The source groups these
  levels; it supplies no separate staff threshold. [S11]

## S12 — real-time updates

The source says senior/staff candidates frequently discuss minimizing how much
connection state spreads through their architecture. It also values the
simplicity of polling in senior+ interviews when latency requirements permit it.
Neither observation separates senior from staff. [S12]

## No complete seniority ladder

S8 (scaling reads), S10 (long-running tasks), S13 (contention), and S14 (large
blobs) provide technical reasoning but no explicit mid/senior/staff thresholds. Their probes can
assess answer quality without assigning a source-backed career level. None of
these seven sources supplies a global prompted-versus-unprompted level bar. [S8][S10][S13][S14]

Report the demonstrated technical understanding and any scoped bar met. If the
user asks for an overall career level, state that the library cannot establish
one; do not invent thresholds or import the removed walkthrough expectations.

## Sources

- **[S8]** Hello Interview — Scaling Reads — <https://www.hellointerview.com/learn/system-design/patterns/scaling-reads>
- **[S9]** Hello Interview — Scaling Writes — <https://www.hellointerview.com/learn/system-design/patterns/scaling-writes>
- **[S10]** Hello Interview — Managing Long Running Tasks — <https://www.hellointerview.com/learn/system-design/patterns/long-running-tasks>
- **[S11]** Hello Interview — Multi-step Processes — <https://www.hellointerview.com/learn/system-design/patterns/multi-step-processes>
- **[S12]** Hello Interview — Real-time Updates — <https://www.hellointerview.com/learn/system-design/patterns/realtime-updates>
- **[S13]** Hello Interview — Dealing with Contention — <https://www.hellointerview.com/learn/system-design/patterns/dealing-with-contention>
- **[S14]** Hello Interview — Handling Large Blobs — <https://www.hellointerview.com/learn/system-design/patterns/large-blobs>
