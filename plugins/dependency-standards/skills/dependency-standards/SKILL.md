---
name: dependency-standards
description: Evaluate, approve, pin, update, and remove third-party dependencies in any ecosystem before they enter a codebase. Use when adding or replacing a library, package, GitHub Action, container base image, or other external component; when reviewing a pull request that adds a dependency or a bot-authored version update; when checking a candidate's real usage, maintenance health, provenance, or license; or when defining a dependency policy, allowlist, pinning rule, or intake record. Applies a blocking gate to a new dependency and a lighter evidence check to an update.
---

# Dependency Standards

A dependency is a permanent transfer of trust and maintenance cost to someone
outside the repository. Availability is not a reason to adopt one.

## Precedence and scope

Follow explicit user requirements and repository-local dependency policy. Use
these Tashtit conventions where the repository is silent. When repository
policy is stricter, the repository wins.

This standard covers every externally sourced component the build, test,
runtime, or automation depends on: language packages, CI actions and reusable
workflows, container base images, system packages, binaries and installers
fetched by scripts, IaC modules, plugins and extensions, and hosted services
called at build time. Ecosystem-specific evidence lives in
[references/intake.md](references/intake.md).

Do not add, upgrade, or remove a dependency as an unrequested side effect of
another change. Report the finding and let the maintainer decide.

## Two gates

**Adding a new dependency is a blocking gate.** Every check below is answered
with evidence before the dependency is declared, and the answers are recorded
in the repository. An unanswered check is a stop, not a risk to accept
silently.

**Updating an existing dependency is a review gate.** The dependency is already
trusted, so the work is proportional to what changed: read the diff of what you
are pulling in, confirm the trust facts still hold, and re-record them. A
security update may ship first and be reviewed in the same pull request; it is
never exempt from review.

## Hard gate: adding a dependency

Answer all seven with evidence. Record the answers with the change.

### 1. Need

State the problem in one sentence and why the platform, the standard library,
or an already-present dependency does not solve it. Prefer no dependency when
the required behavior is small, stable, and well understood; prefer a
dependency when the domain is genuinely hard to get right — cryptography, TLS,
date and timezone handling, parsers, protocol clients.

Reject a dependency that exists to avoid writing a few lines of obvious code.
Its real cost is the transitive tree, the update stream, and the trust.

### 2. Fit

Name at least one material alternative, including "implement it here", and say
why the candidate wins. Compare on behavior, supported platforms and runtime
versions, API stability, install and build weight, transitive dependency count,
and how hard the dependency is to remove later.

Prefer the option with the smallest transitive tree and the clearest exit.

### 3. Usage and health

Adoption is evidence that defects surface and get fixed, not proof of quality.
Gather actual numbers rather than impressions: download or dependent counts,
release cadence, commit and issue activity in the last twelve months, number of
maintainers, open critical issues, and whether the last release predates the
current runtime.

Treat as blocking until justified in writing: a single maintainer with no
succession, no release in twelve months while the ecosystem moved, an issue
tracker where security reports go unanswered, or a pre-1.0 package used on a
critical path.

### 4. Provenance and trust

Verify you are getting the artifact you think you are, from who you think.
Confirm the package name character by character against the source repository
it claims — typosquatting and dependency confusion rely on nobody looking.
Check that the published artifact is built from that repository (provenance
attestation, signed release, or reproducible build), that maintainer accounts
require multi-factor authentication where the registry exposes it, and whether
ownership was transferred recently.

Reject a package whose registry page links to no source, whose source
repository does not contain the published code, or that is newly transferred to
an unknown owner. Prefer a namespace you already trust over a same-named
package in a public namespace.

### 5. License

Identify the license as an SPDX identifier from the distributed artifact, not
from a badge. Confirm it is compatible with the repository's own license and
distribution model, and that it does not impose obligations the project cannot
meet — copyleft reciprocity in a proprietary distribution, network-use clauses
in a hosted service, attribution requirements nobody will honor, or a
source-available license that is not open source at all.

Stop on an absent, ambiguous, custom, or dual license whose terms have not been
read, or on a transitive dependency with a stronger license than the direct
one.

### 6. Security and supply chain

Check known vulnerabilities in the candidate and its tree, whether it executes
install-time scripts, what capabilities it needs at runtime (filesystem,
network, process spawning, native code), and whether it phones home. Weigh the
blast radius of a compromise: a build-time or CI dependency runs with the
permissions of the pipeline, which is often broader than production.

Prefer a dependency that runs without install scripts and needs no elevated
capability. Where the ecosystem supports it, install with scripts disabled.

### 7. Control

Decide, before adopting, how the dependency is pinned, updated, and removed.
Pin to an immutable reference — a lockfile entry, an exact version, a digest,
or a full commit SHA — so the build is reproducible and an upstream change
cannot alter it silently. Assign an owner, subscribe to its advisories, and
write down the exit: the alternative to switch to, or the code that would
replace it, if the project is abandoned or compromised.

### Record the decision

Commit the answers next to the code as a dependency record: ecosystem, name,
pinned version, purpose, SPDX license, canonical source URL, adoption and
health evidence, how provenance was verified, alternatives considered, and who
approved it on what date. A record that exists only in a pull-request comment
is lost by the next review.

Enforce it mechanically where possible: a check that fails when a declared
dependency has no record makes the gate real instead of aspirational.

## Soft gate: updating a dependency

An update is not automatically safe. Before merging, including for a bot-opened
pull request:

- read the changelog or commit range between the pinned and proposed versions,
  and treat "no release notes" as a reason to read the diff;
- confirm the license, source repository, and owning account did not change;
- check what the update adds or removes transitively, not just the top-level
  version bump;
- for a major version, find the breaking changes and the migration steps before
  merging, never after;
- re-run the project's own tests and checks against the new version rather than
  trusting the upstream badge.

Update the recorded pinned version in the same pull request so the record and
the manifest never disagree.

Apply a security update promptly, but still confirm that the advisory affects a
path this project uses, that the fixed version is the minimal upgrade, and that
the fix comes from the same maintainers as before. A compromised package's
first move is often a patch release.

Prefer grouped, scheduled, automated update pull requests over ad-hoc manual
bumps: they keep the diff small, the review cadence predictable, and the
security backlog visible.

## Removal

A dependency that is no longer imported must be removed from the manifest,
lockfile, and record in the same change. An unused dependency still contributes
vulnerabilities, license obligations, and install time.

## Review output

When reviewing a change that adds or updates a dependency, lead with the
blocking findings. For each, name the check that failed, the evidence, and the
concrete remediation. Separate blockers from recommendations. Never state that
a dependency is safe, trusted, or vetted because a check was skipped; report
what was verified and what was not.

## Definition of done

A dependency change is done when the need and alternatives are stated, usage
and health are evidenced, provenance is verified, the license is identified and
compatible, security and capability exposure are understood, the version is
pinned to an immutable reference, the record is committed, the project's checks
pass, and the diff contains no unrelated dependency movement.
