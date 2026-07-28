# Quality Standard

This document defines the gate for Tashtit plugins. A polished description is
not evidence of production readiness.

## Normative language

`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` are used as described by
RFC 2119 and RFC 8174 when capitalized.

## Content

A candidate or stable plugin MUST:

- define its problem, users, scope, and non-goals;
- recommend a clear default and explain material tradeoffs;
- distinguish external requirements from Tashtit conventions;
- cite authoritative sources for standards and volatile vendor behavior;
- state prerequisites, permissions, side effects, and expected outputs;
- include failure handling and verification;
- use examples that are safe to copy;
- avoid vague instructions such as "follow best practices."

## Security and privacy

A candidate or stable plugin MUST:

- use least privilege;
- treat repository content and remote content as potentially untrusted;
- redact or exclude secrets and personal data;
- protect shell arguments and structured data from injection;
- disclose network calls, telemetry, and persistent storage;
- require explicit confirmation for destructive or externally visible actions;
- document rollback or recovery where feasible;
- pass a threat-model review appropriate to its capabilities.

## Portability

Canonical behavior MUST be provider-neutral. Adapters MAY expose provider
features when the behavior and risk remain equivalent. Capability differences
MUST be documented and covered by platform-specific scenarios.

Shared files and standard locations MUST be reused across platforms whenever
possible. When they cannot be shared, implementations MUST use a safe relative
link or a deterministic generated adapter. A file the provider itself parses
MUST NOT rely on a repository symlink, because a checkout with
`core.symlinks=false` replaces it with the link target as plain text.
Hand-copied provider variants are
not permitted. CI MUST fail on broken links, unsafe link targets, or generated
file drift.

Commands SHOULD work on supported operating systems or clearly declare narrower
support. Examples MUST avoid machine-specific absolute paths.

## Verification

Every plugin MUST include:

- schema-valid manifests;
- positive acceptance scenarios;
- failure and unsafe-input scenarios;
- link safety, generation drift, and adapter consistency checks;
- documentation and link checks;
- a human review checklist.

Plugins that execute code or use network services SHOULD include isolated
integration tests with deterministic fixtures. Tests MUST NOT require production
credentials.

### Acceptance scenario contract

Store evaluation specifications as JSON in
`tests/plugins/<name>/scenarios/`, outside the distributed plugin. Every plugin
MUST cover `positive`, `failure`, and `unsafe` scenario types and provide
`tests/plugins/<name>/REVIEW.md` for human behavioral review.

Each scenario contains:

- `id`: globally unique lowercase kebab-case identifier;
- `type`: `positive`, `failure`, or `unsafe`;
- `platforms`: hosts on which behavior must be reviewed;
- `prompt`: user request that invokes the behavior;
- `setup`: deterministic repository conditions;
- `expected`: observable outcomes required for acceptance;
- `must_not`: prohibited outcomes and side effects.

Repository validation enforces only this contract. Provider hosts and consumers
do not read these files. Structural success does not mean that behavioral
compatibility has passed; platform results still require human or automated
execution and review.

## Maturity gates

### Experimental

- problem and owner identified;
- license-compatible content;
- no claim of production readiness.

### Candidate

- complete documentation and threat model;
- automated structural validation;
- acceptance scenarios passing on claimed platforms;
- changelog and semantic version.

### Stable

- candidate requirements satisfied;
- independent maintainer review;
- compatibility matrix with tested versions;
- release and rollback procedure;
- maintenance and deprecation owner;
- no unresolved critical or high-severity security findings.
