# Changelog

## 0.4.0 - 2026-08-09

- Expression handling in `run` scripts is now explicit: bind the value to an
  `env:` entry and read it as a quoted `"${VARNAME}"`, never `${{ env.VARNAME }}`,
  which is substituted into the script text the same way a raw context
  reference is.
- Added a reference section covering safe and unsafe `run` forms, the
  provenance drift that makes a workflow-level `env` read unsafe over time,
  the `pwsh` and `cmd` equivalents, and where expressions remain correct.
- Credential persistence is now a per-checkout decision to state either way:
  every `actions/checkout` sets `persist-credentials` explicitly, an unstated
  setting is a review finding, and a `true` names the step that needs it.
- Extended the review checklist with both rules.

## 0.3.0 - 2026-08-08

- Added job-naming and workflow-shape conventions: short lowercase job
  identifiers, no job-level `name`, and explicit per-job `timeout-minutes`.

## 0.2.1 - 2026-08-08

- Skill description now defers scored, read-only maturity audits to the
  maturity plugin's `evaluate-ci-workflow`, so overlapping "audit our GitHub
  Actions" requests route deterministically.
- Corrected the README maturity claim, which still advertised 0.1.0.

## 0.2.0 - 2026-08-06

- Added credential-persistence guidance: check out with
  `persist-credentials: false` unless a later step in the same job must
  authenticate as the repository, and declare `persist-credentials: true`
  explicitly when it does.
- Added scalar quoting guidance covering YAML type coercion in `with:`, `env:`,
  and runtime-version fields.
- Extended the review checklist with scalar quoting and credential persistence.

## 0.1.0 - 2026-07-29

- Added opinionated GitHub Actions CI, artifact, release, and deployment rules.
- Added trust-boundary, permissions, action-pinning, secret-lifecycle, and safe
  ephemeral-preview guidance.
- Added positive, failure, and unsafe acceptance scenarios.
