---
name: engineering-standards
description: Design, implement, or review production software changes against opinionated engineering standards for correctness, security, maintainability, testing, operations, and delivery. Use for implementation planning, code review, definition-of-done checks, risk assessment, and verification strategy.
---

# Engineering Standards

Apply a consistent production engineering bar without pretending that one
checklist replaces repository context or expert review.

## Precedence and scope

Follow explicit user requirements and repository-local standards. Use these
Tashtit conventions where the repository is silent. Identify conflicts and ask
only when the answer materially changes safety or architecture.

Do not expand a review request into edits. Do not claim compliance,
production-readiness, or security certification from checklist completion.

## Standard

### Understand the change

- Define the problem, users, observable behavior, non-goals, and failure modes.
- Trace affected boundaries: APIs, data, permissions, dependencies, operations,
  compatibility, and rollback.
- Prefer the smallest coherent design that satisfies known requirements.

### Correctness and interfaces

- Make invariants explicit and validate data at trust boundaries.
- Handle empty, malformed, duplicate, partial, concurrent, and timeout cases.
- Preserve backward compatibility or document an intentional migration.
- Keep errors actionable without exposing secrets or internal sensitive data.

### Security and privacy

- Use least privilege and safe defaults.
- Treat external, generated, and repository-controlled input as untrusted.
- Keep credentials out of source, output, logs, tests, and command arguments.
- Require explicit authorization for destructive or externally visible effects.
- Consider abuse, injection, authorization, data retention, and dependency risk.

### Maintainability

- Match established structure and naming; avoid speculative abstraction.
- Keep dependencies justified, pinned according to policy, and removable.
- Separate generated artifacts from canonical sources and validate drift.
- Document decisions that future maintainers cannot recover from the code.

### Verification

- Test behavior at the lowest useful level and important integrations at their
  real boundary.
- Cover the success path, realistic failures, unsafe input, and regressions.
- Keep tests deterministic; control time, randomness, network, and concurrency.
- Run relevant formatting, lint, type, build, test, and security checks.
- Report exact results and untested areas. Never describe an unrun check as
  passing.

#### Flaky tests

A flaky test passes and fails without a code change and destroys trust in the
suite. Detect and handle it deliberately.

- Detect: treat a test as suspect when it fails intermittently, only on CI, only
  under parallelism, or only in a specific order. Reproduce with repeated runs
  (a repeat/count flag or a loop) and record the observed failure rate rather
  than dismissing a single red run as noise.
- Diagnose the root cause before muting. Common sources are uncontrolled time,
  randomness, timezone, and locale; ordering or shared mutable state between
  tests; real network, filesystem, or clock dependencies; unawaited async work
  and race conditions; and fixed sleeps standing in for synchronization.
- Fix the cause: inject clocks and seeds, isolate state, await work explicitly,
  wait on conditions instead of sleeping, and stub external boundaries.
- Quarantine only as a temporary, tracked exception. A muted or skipped test
  MUST link an issue with an owner and a re-enable plan, and MUST NOT mask a
  real product bug. Never make a test pass by loosening an assertion until it no
  longer verifies the behavior.
- Do not retry to green blindly. If automatic retries are used, cap them, make
  retried failures visible, and never hide a consistently failing test behind
  retries.

### Operations and delivery

- Define configuration, observability, resource limits, timeouts, cleanup, and
  graceful degradation when applicable.
- Prefer backward-compatible deployment ordering and a practical rollback.
- Update runbooks, ownership, release notes, and metrics when behavior changes.

## Review output

Lead with findings ordered by severity. For each finding include evidence,
impact, and a concrete remediation. Separate blockers from recommendations and
questions. If there are no findings, state remaining uncertainty and validation
gaps instead of giving an unconditional approval.

## Definition of done

A change is done only when intended behavior is implemented, relevant failure
modes are handled, tests and required checks pass, security and operational
effects are understood, documentation is current, and the diff contains no
unrelated work.
