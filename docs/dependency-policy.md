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
purpose. The validator, sync, secret scan, and dependency check are
dependency-free Node.js scripts, and that MUST remain the default for new
tooling.

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

The answers are recorded in [`dependency-registry.json`](../dependency-registry.json).
A record is not paperwork: it is the artifact a reviewer checks, and the thing
`npm run validate` requires.

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

The same list is enforced on pull requests by the `deps` CI job. Changing it is
a policy decision, so the list in this table and the one in
[`.github/workflows/ci.yml`](../.github/workflows/ci.yml) MUST be changed
together.

## Updating a dependency is a review gate

An update SHOULD land through the scheduled, grouped Dependabot pull requests
configured in [`.github/dependabot.yml`](../.github/dependabot.yml). Before
merging one, a reviewer MUST:

- read the changelog or commit range between the recorded and proposed
  versions;
- confirm the license, source repository, and owning account are unchanged;
- check what the update adds or removes transitively;
- for a major version, identify the breaking changes and do the migration in
  the same pull request;
- run `npm run validate` and `npm test` against the new version.

A security update MAY be merged ahead of a routine one, but MUST still be
reviewed against the advisory: confirm it affects a path this repository uses
and that the fix comes from the same maintainers.

The recorded version MUST be updated in the same pull request. Until it is,
`npm run validate` prints a warning naming the dependency, the recorded
version, and the declared one. The warning does not fail the build — that is
what makes an update a soft gate — but merging with the warning outstanding
means the update was not reviewed.

## Pinning

- npm dependencies MUST be exact versions in `package.json`, installed with
  `npm ci` against the committed lockfile. `npm install` in CI is prohibited.
- Third-party GitHub Actions MUST be pinned to a full 40-character commit SHA.
- Actions published by GitHub itself MAY use an exact release tag such as
  `v7.0.1`, because this repository's CI holds no secrets, write permissions,
  or deployment authority. A movable major tag such as `v7` is never allowed.
- `npm run validate` enforces the action pinning rule.

## Removal

A dependency that is no longer used MUST be removed from the manifest, the
lockfile, and the registry in one change. `npm run validate` fails on a record
with no matching declaration, so a stale record cannot linger.

## Enforcement

| Check | Where | Failure mode |
| --- | --- | --- |
| Every declared dependency has a reviewed record | `scripts/check-dependencies.js`, in `npm run validate` | Hard failure |
| No record without a declaration | same | Hard failure |
| Recorded version matches the manifest | same | Warning |
| Vulnerable or non-allowlisted dependency introduced by a pull request | `deps` job in CI | Hard failure on the pull request |
| Actions pinned to an immutable reference | `scripts/validate.js` | Hard failure |
| Grouped, scheduled update pull requests | `.github/dependabot.yml` | Not a check |

Run the repository check locally with:

```bash
npm run check:deps
```

The check reads committed files only. It cannot tell whether the recorded
evidence is true, so it never substitutes for the review — it only guarantees
that a reviewer was asked.

The `deps` CI job needs GitHub's dependency graph enabled for the repository.
If the job reports that the dependency graph is unavailable, enable it in
repository settings rather than deleting the job.

## Adding a record

Add one object to the `dependencies` array in `dependency-registry.json`,
sorted by `ecosystem` then `name`. Every field is required:

```json
{
  "ecosystem": "npm",
  "name": "example-package",
  "version": "1.4.2",
  "purpose": "What this repository needs it for, and why nothing already here does it.",
  "alternatives": [
    "The alternative considered, and why it lost."
  ],
  "adoption": "Dependents, release cadence, maintainer count, and the date the numbers were checked.",
  "provenance": "How the artifact was tied to its source repository, and how it is installed.",
  "license": "MIT",
  "source": "https://github.com/example/example-package",
  "reviewed_by": "@handle",
  "reviewed_on": "2026-08-09"
}
```

`ecosystem` is `npm` or `github-actions`. `version` MUST match the version the
manifest or workflow declares, exactly as declared — the npm version string, or
the action's `@` reference. Extending the registry to another ecosystem means
teaching `scripts/check-dependencies.js` to discover it, so that a declared
dependency can never sit outside the gate.
