# Dependency Policy

This document is the rule for adding, updating, and removing any externally
sourced dependency in this repository. The published standard behind it ships
as the [dependency-standards plugin](../plugins/dependency-standards/); this
page states how Tashtit applies it to itself and how the gate is enforced.

## Normative language

`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` are used as described by
RFC 2119 and RFC 8174 when capitalized.

## Scope

The policy covers every component this repository declares from outside it:
npm packages, GitHub Actions and reusable workflows, and anything a script
downloads at build or run time. It applies to production, development, and
CI-only dependencies. A CI dependency is not lower risk: it runs inside the
pipeline, with the pipeline's token and network.

Tashtit's own baseline is that this repository stays dependency-light on
purpose. The validator, sync, and secret scan are dependency-free Node.js
scripts, and that MUST remain the default for new tooling.

## Adding a dependency is a blocking gate

A new dependency MUST NOT be declared until all of the following are answered
with evidence and committed in the same pull request:

1. **Need** — the problem, and why the platform, the standard library, or an
   existing dependency does not solve it.
2. **Fit** — at least one material alternative, including implementing it here,
   and why the candidate wins.
3. **Usage and health** — real numbers: dependents or downloads, release
   cadence, maintainer count, activity in the last twelve months. A
   single-maintainer or dormant project MUST be justified in writing.
4. **Provenance** — the published artifact is verified to come from the source
   repository it claims. The name MUST be checked character by character
   against that repository.
5. **License** — an SPDX identifier read from the distributed artifact, allowed
   by the table below, and compatible with this repository's Apache-2.0
   license.
6. **Security** — known advisories, install-time scripts, required
   capabilities, and the blast radius if the package were compromised.
7. **Control** — the immutable pin, the owner, and the exit plan.

The answers go in the pull request: the **Dependencies** section of the
template carries them, and the issue that proposed the dependency links the
discussion. This repository deliberately keeps no separate dependency
register — with a handful of dependencies, the pull request history is the
record, and a reviewer MUST NOT approve a dependency addition whose PR leaves
any of the seven answers missing.

`docs/quality-standard.md` and `CONTRIBUTING.md` already require an issue
before a substantial change; a new dependency MUST have one.

### Allowed licenses

| Class | Identifiers | Handling |
| --- | --- | --- |
| Permissive | 0BSD, Apache-2.0, BSD-2-Clause, BSD-3-Clause, CC0-1.0, ISC, MIT, Unlicense | Allowed. |
| Weak copyleft | MPL-2.0 | Allowed for unmodified use; modifications must be released under the same terms. |
| Strong copyleft | GPL-*, AGPL-*, LGPL-* | Not allowed. |
| Source-available | BUSL-1.1, SSPL, Elastic-2.0 | Not allowed; these are not open source. |
| Unclear | absent, custom, conflicting | Not allowed until resolved and re-reviewed. |

The same list is enforced on pull requests by the dependency review step in
CI. Changing it is a policy decision, so the list in this table and the one in
[`.github/workflows/ci.yml`](../.github/workflows/ci.yml) MUST be changed
together.

## Updating a dependency is a review gate

An update SHOULD land through the scheduled, grouped Dependabot pull requests
configured in [`.github/dependabot.yml`](../.github/dependabot.yml). Before
merging one, a reviewer MUST:

- read the changelog or commit range between the current and proposed
  versions;
- confirm the license, source repository, and owning account are unchanged;
- check what the update adds or removes transitively;
- for a major version, identify the breaking changes and do the migration in
  the same pull request;
- run `npm run validate` and `npm test` against the new version.

A security update MAY be merged ahead of a routine one, but MUST still be
reviewed against the advisory: confirm it affects a path this repository uses
and that the fix comes from the same maintainers.

What makes an update a soft gate is that nothing blocks the merge beyond this
review; the reviewer's approval on the update pull request is the record that
it happened.

## Pinning

- npm dependencies MUST be exact versions in `package.json`, installed with
  `npm ci` against the committed lockfile. `npm install` in CI is prohibited.
- Third-party GitHub Actions MUST be pinned to a full 40-character commit SHA.
- Actions published by GitHub itself MAY use an exact release tag such as
  `v7.0.1`, because this repository's CI holds no secrets, write permissions,
  or deployment authority. A movable major tag such as `v7` is never allowed.
- `npm run validate` enforces the action pinning rule.

## Removal

A dependency that is no longer used MUST be removed from the manifest and the
lockfile in one change. An unused dependency still contributes advisories,
license obligations, and install time.

## Enforcement

| Check | Where | Failure mode |
| --- | --- | --- |
| Vulnerable or non-allowlisted dependency introduced by a pull request | dependency review step in the `ci` job | Hard failure on the pull request |
| Actions pinned to an immutable reference | `scripts/validate.js` | Hard failure |
| Intake evidence for a new dependency | the PR template's Dependencies section, checked by the reviewer | Human review |
| Grouped, scheduled update pull requests | `.github/dependabot.yml` | Not a check |

The intake gate is enforced by review rather than by a script. Automation here
covers what a machine can actually decide — advisories, license identifiers,
and pinning — while need, alternatives, provenance, and trust are judgment
calls that a required template section puts in front of the reviewer.

The dependency review step in the `ci` job compares the base and head
dependency graphs, which exist only for a pull request, so it is skipped on
push and manual dispatch. It runs after validation and the unit tests, so a
denied dependency does not hide the other results.

The step also requires a public repository, or GitHub Advanced Security on a
private one; without either, GitHub returns a setup error. That prerequisite is
deliberately not guarded away with a condition. If this repository ever becomes
private without an Advanced Security license, the step MUST fail loudly and the
loss of coverage MUST be decided on, because a silently skipped supply-chain
check reads as a passing one.

## If the dependency count grows

This policy trades automation for low overhead because the repository declares
a handful of dependencies and intends to keep it that way. If that stops being
true — roughly, when a reviewer can no longer say from memory why each
dependency is here — revisit the decision to keep no machine-checked
dependency register. The dependency-standards plugin describes the committed
record shape and the validation that makes the intake gate a build failure
instead of a review convention.
