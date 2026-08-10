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
- [x] Generate each Codex plugin manifest instead of relying on symlinks.
- [x] Add CI validation for generated-adapter drift.
- [x] Validate the documented plugin catalog tables against the marketplace.
- [x] Add Markdown style and committed-credential validation.
- [ ] Add JSON Schema validation for canonical manifests.
- [x] Add scenario test conventions and a local structural test harness.
- [x] Gate maturity claims on recorded, version-pinned acceptance results.
- [ ] Add an evaluation runner that executes scenarios and records results
      automatically.
- [ ] Define release automation, provenance, checksums, and changelogs.
- [x] Publish the private security reporting channel.
- [ ] Publish maintainer ownership details.

## Phase 1: repository engineering

### Engineering standards

- [x] Definition-of-done and verification workflow.
- [x] Testing strategy and deterministic-test defaults.
- [ ] Flaky-test detection and handling.
- [x] Error handling, configuration, dependency, and API design defaults.
- [x] Security and privacy baseline for application changes.

### Repository onboarding

- [x] Structured repository discovery and architecture mapping.
- [x] Build, test, lint, and local-environment detection.
- [x] Risk, ownership, dependency, and operational-context inventory.
- [x] Generation of a reviewable onboarding report without repository changes.

### Git and pull requests

- [x] Branching, focused commits, and Conventional Commits.
- [x] Safe rebasing, conflict handling, and history-preservation rules.
- [x] Pull-request description, evidence, and reviewer handoff.
- [x] Guardrails for default branches, force pushes, and destructive recovery.

### GitHub Actions

- [x] Generic CI structure, required-check, concurrency, and timeout defaults.
- [x] Pull-request trust boundaries, least privilege, and secret handling.
- [x] Action pinning, reproducible installs, cache, and artifact guidance.
- [x] Isolated release, deployment, and ephemeral-preview rules.
- [ ] Execute and record acceptance scenarios across supported platforms.

### Repository settings

Shipped as the `repository-governance` plugin.

- [x] GitHub rulesets and protected-branch recommendations.
- [x] Required reviews, status checks, signed changes, and merge strategies.
- [x] CODEOWNERS, issue templates, security features, and dependency updates.
- [x] Audit-only mode before any settings mutation.
- [x] Policy-as-code examples with rollback instructions.

### Dependency intake

Shipped as the `dependency-standards` plugin, and applied to this repository by
the [dependency policy](dependency-policy.md).

- [x] Blocking intake gate for a new dependency: need, alternatives, usage and
      health, provenance, license, security exposure, and pinning.
- [x] Review gate for version updates, including bot-authored and security
      updates, and a removal rule.
- [x] Ecosystem evidence for npm, GitHub Actions, containers, and language
      package managers, plus license classes.
- [x] Repository dependency policy with review-enforced intake evidence and
      CI-blocked vulnerable or non-allowlisted dependencies.

### Code style and maintainability

- [ ] Language-neutral readability and change-scope guidance.
- [ ] TypeScript/JavaScript, Python, Go, and Java profiles.
- [ ] Formatting versus semantic linting boundaries.
- [ ] Generated-code and vendored-code handling.

## Phase 2: production operations

### Logging and observability

- [x] Structured event schema and severity semantics.
- [x] Correlation, trace, request, and tenant identifiers.
- [x] Redaction, data classification, and retention guidance.
- [x] Error taxonomy, sampling, cardinality, and cost controls.
- [x] OpenTelemetry alignment and verification scenarios.

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
