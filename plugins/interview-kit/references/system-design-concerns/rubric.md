# Evaluation Rubric

How to score whether a concern was handled well. One generic scale, applied to any concept in
this library. Concept files deliberately carry **no** per-level anchors of their own: a source
that never stated what "level 4 caching" looks like cannot support one, and inventing it would
break the library's citation guarantee. Judge the evidence against the scale below.

## The scale

**0 — Not considered.** No evidence anyone noticed the concern. The code is silent, the
history is silent, the conversation is silent. Not the same as "decided against."

**1 — Mentioned.** The concern is named — a comment, a TODO, a line in a design note, a
sentence in the conversation — but no tradeoff was weighed and nothing follows from it.
`// TODO: probably need caching here` is a 1.

**2 — Reasoned about.** Tradeoffs were weighed against the actual requirements and a
decision was recorded with a reason. **A deliberate "not needed" scores a full 2, and is
the correct ceiling when the requirements don't justify the mechanism.** "Writes are ~1/sec
so a single primary is fine; revisit above 500/sec" is a 2 and should not be penalized for
not being a 3.

**3 — Implemented.** A correct mechanism exists in the code, on the real path, and handles
the obvious cases. Correct means it actually does the job: a cache that is read before the
database and written after, not a cache client that is instantiated and never used.

**4 — Tested.** Validated by something that would fail if the mechanism broke — a test
asserting a second identical request does not create a second row, a test asserting the
second read is a cache hit, a load test showing the p99 target met. The test must be
capable of failing; asserting a 200 response proves nothing about the mechanism.

**5 — Strong judgment.** Everything in 4, plus:

- validated under realistic conditions (real data volumes, concurrency, or load — not a
  single happy-path call),
- failure behavior is explicit and handled (dependency down, timeout, partial write),
- the solution is **scoped to the requirements** — no gold-plating, and the reasoning for
  where the line was drawn is available,
- limits are known and stated ("this holds to ~10k rps; beyond that the counter becomes the
  bottleneck and we'd shard ranges").

A 5 is rare and is not "used more technology." An over-engineered, untested,
multi-region-by-default design is closer to a 1 than a 5.

## Distinguish these four cases explicitly

Every evaluation must say which of these applies:

1. **Did not notice the issue** → 0. The problem is present in the workload and nothing
   addresses or acknowledges it.
2. **Noticed and correctly declined** → 2, capped there, not penalized. Requirements did
   not justify the mechanism and the reasoning is sound.
3. **Implemented correctly** → 3, or 4 with a real test.
4. **Implemented and validated under realistic conditions** → 5.

Also flag the failure mode the scale does not capture directly: **implemented but not
needed**. Score the implementation on its merits, then note the unjustified complexity as a
judgment deduction. A correct cache in front of a table that gets 3 reads a day is not good
engineering.

## Evidence hierarchy

Strongest to weakest. Prefer the strongest available; never score above what the evidence
supports.

1. **Runtime evidence** — load test output, latency percentiles, metrics/dashboards, logs
   from failure injection, profiler output.
2. **Tests** — unit/integration/property/concurrency tests that exercise the mechanism and
   can fail. Read the assertions, not the test names.
3. **Source code on the real path** — the mechanism is wired into the code that actually
   serves traffic. Trace the call, don't trust the file name.
4. **Schema, migrations, and configuration** — indexes, constraints, unique keys, TTLs,
   replica config. Strong evidence for data-layer concerns specifically.
5. **Architecture and structure** — service boundaries, queues, deployment topology.
6. **Git history** — commit messages and PR descriptions showing a decision and its reason;
   a revert showing a tradeoff was tested and rejected.
7. **Design notes and comments** — real but weak; claims of behavior, not behavior.
8. **Conversation/agent history** — shows reasoning happened; supports a 1 or 2, cannot
   alone support a 3+.

## Anti-patterns in scoring

- **Dependency ≠ implementation.** `redis` in the manifest → caching = 5 is invalid. Find
  the read path.
- **Name ≠ behavior.** A file called `RateLimiter.ts`, a class called `IdempotentHandler`,
  or a test called `it('is idempotent')` proves nothing. Read the body.
- **Config ≠ effect.** A TTL constant that no code reads. A replica that nothing fails over
  to. An index in a migration that the query planner can't use because the query wraps the
  column in a function.
- **Happy-path test ≠ validation.** One request returning 200 does not test idempotency,
  concurrency, or cache correctness.
- **Complexity ≠ sophistication.** Unjustified components lower the score.
- **Absence of a technology ≠ absence of the concern.** A single well-chosen index may
  fully satisfy latency requirements. That's a good outcome, not a gap.

## Reporting format

Per concern, keep it to a few lines:

```text
Concern: caching
Score: 2 (reasoned about, correctly declined)
Case: noticed and declined
Evidence: PR #14 description sizes reads at ~40/day and rejects a cache;
          index on lookup column added in migration 0007 instead
Gap to next level: none warranted — a cache is not justified at this volume
```

Always include a "gap to next level" line, and be willing to write "none warranted."
