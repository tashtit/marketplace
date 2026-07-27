# Roadmap

The roadmap is ordered by prerequisites and user value. Dates are intentionally
omitted until maintainers establish delivery capacity.

## Phase 0: trustworthy foundation

- [x] Define positioning, governance, security policy, and quality standard.
- [x] Define the canonical payload and provider-adapter architecture.
- [x] Seed Claude Code, Codex, and Copilot marketplace locations.
- [x] Add dependency-free JSON, catalog, manifest, and local-link validation.
- [x] Use the standard Claude marketplace as canonical catalog metadata.
- [x] Share the Claude/Copilot marketplace instead of duplicating it.
- [x] Generate the Codex marketplace from the canonical catalog.
- [x] Add CI validation for generated-adapter drift.
- [ ] Add JSON Schema, Markdown, and secret validation.
- [ ] Add scenario test conventions and a local test harness.
- [ ] Define release automation, provenance, checksums, and changelogs.
- [ ] Publish maintainer and private security contact details.

## Phase 1: repository engineering

### Engineering standards

- [ ] Definition-of-done and verification workflow.
- [ ] Testing pyramid, deterministic tests, and flaky-test handling.
- [ ] Error handling, configuration, dependency, and API design defaults.
- [ ] Security and privacy baseline for application changes.

### Repository onboarding

- [ ] Structured repository discovery and architecture mapping.
- [ ] Build, test, lint, and local-environment detection.
- [ ] Risk, ownership, dependency, and operational-context inventory.
- [ ] Generation of a reviewable onboarding report without repository changes.

### Git and pull requests

- [ ] Branching, focused commits, and Conventional Commits.
- [ ] Safe rebasing, conflict handling, and history-preservation rules.
- [ ] Pull-request description, evidence, and reviewer handoff.
- [ ] Guardrails for default branches, force pushes, and destructive recovery.

### Repository settings

- [ ] GitHub rulesets and protected-branch recommendations.
- [ ] Required reviews, status checks, signed changes, and merge strategies.
- [ ] CODEOWNERS, issue templates, security features, and dependency updates.
- [ ] Audit-only mode before any settings mutation.
- [ ] Policy-as-code examples with rollback instructions.

### Code style and maintainability

- [ ] Language-neutral readability and change-scope guidance.
- [ ] TypeScript/JavaScript, Python, Go, and Java profiles.
- [ ] Formatting versus semantic linting boundaries.
- [ ] Generated-code and vendored-code handling.

## Phase 2: production operations

### Logging and observability

- [ ] Structured event schema and severity semantics.
- [ ] Correlation, trace, request, and tenant identifiers.
- [ ] Redaction, data classification, and retention guidance.
- [ ] Error taxonomy, sampling, cardinality, and cost controls.
- [ ] OpenTelemetry alignment and verification scenarios.

### Production snippets

- [ ] Redis connection lifecycle, pooling, timeouts, and TLS.
- [ ] Retry, exponential backoff, jitter, and idempotency.
- [ ] Cache-aside, stampede protection, and invalidation.
- [ ] Database and HTTP client connection management.
- [ ] Health checks, graceful shutdown, and readiness.

Snippets are reference implementations, not paste-only fragments. Each MUST
document supported versions, failure behavior, resource cleanup, security,
observability, tests, and operational tradeoffs.

## Phase 3: enterprise controls

- [ ] Plugin bill of materials and provenance.
- [ ] Permission and external-data inventory.
- [ ] Offline and restricted-network behavior.
- [ ] Organization policy packs and exception records.
- [ ] Compliance mapping without claiming certification.
- [ ] Compatibility test matrix across supported agent versions.

## Optional platform expansion

- [ ] Validate Cursor packaging, submission, update, and removal contracts.
- [ ] Add Cursor adapter generation and behavioral scenarios.
- [ ] Evaluate additional platforms against the criteria in
  [compatibility.md](compatibility.md).

## Out of scope for now

- A large catalog of lightly reviewed prompts.
- Vendor-specific marketing or paid placement.
- Claims of compliance certification.
- Automatically changing repository or organization settings without an
  explicit audit, confirmation, and rollback plan.
