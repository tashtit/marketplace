# GitHub Actions reference

Use this reference for platform-defined behavior and detailed review
decisions. The normative defaults in `SKILL.md` are Tashtit conventions unless
this file identifies a GitHub requirement.

## Contents

- [Source basis](#source-basis)
- [Trigger and checkout decisions](#trigger-and-checkout-decisions)
- [Permissions and credentials](#permissions-and-credentials)
- [Action and reusable-workflow pins](#action-and-reusable-workflow-pins)
- [Concurrency and timeouts](#concurrency-and-timeouts)
- [Caches, artifacts, and provenance](#caches-artifacts-and-provenance)
- [Workflow review checklist](#workflow-review-checklist)

## Source basis

Use current GitHub documentation when platform behavior may have changed:

- [Workflow syntax for GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax):
  triggers, filters, permissions, jobs, conditions, concurrency, matrices, and
  timeouts.
- [Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows):
  event-specific refs, SHAs, permissions, secrets, and warnings.
- [Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use):
  full-SHA pinning, untrusted input, token and secret safety, and runner risks.
- [Script injections](https://docs.github.com/en/actions/concepts/security/script-injections):
  unsafe context values and the environment-variable mitigation.
- [Use `GITHUB_TOKEN` for authentication](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token):
  token behavior and least-privilege permissions.
- [Dependency caching](https://docs.github.com/en/actions/concepts/workflows-and-actions/dependency-caching):
  cache purpose, scope, and poisoning risk.
- [Workflow artifacts](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts):
  artifact handoff, diagnostic storage, and the distinction from caches.
- [OpenID Connect](https://docs.github.com/en/actions/concepts/security/openid-connect):
  short-lived cloud credentials and trust claims.
- [Managing environments for deployment](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments):
  protection rules, allowed refs, reviewers, and environment-scoped secrets.
- [Reuse workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows):
  inputs, outputs, permissions, secret passing, and nesting.
- [Artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations):
  build provenance, required permissions, and plan availability.
- [Immutable releases](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases):
  protected tags, assets, and release attestations.

The source repositories supplied during the initial design informed the
workflow ergonomics: explicit timeouts, PR-aware concurrency, job-local
permissions, immutable installs, artifact handoff, clean consumer smoke tests,
bounded service readiness, failure logs, unconditional cleanup, protected
release environments, OIDC publishing, and comments that explain exceptional
choices. Their organization-specific runners, registries, actions, secret
names, task runners, observability vendors, branches, and project commands are
intentionally not part of the portable standard.

## Trigger and checkout decisions

GitHub requires workflow files under `.github/workflows` and supports `.yml` or
`.yaml`. Tashtit standardizes the primary file as `ci.yml` for discoverability.

For `pull_request`, the default checkout tests GitHub's event commit, normally a
synthetic merge commit. This is the preferred correctness check when the
question is whether the proposed change integrates with the base. Select
`github.event.pull_request.head.sha` only when a tool explicitly requires the
source commit or the repository deliberately tests head state. Document that
the job no longer tests the synthetic merge.

Use full history only when a command requires graph history, such as affected
change calculation, changelog generation, or semantic versioning. Otherwise
retain shallow checkout.

GitHub warns that executing untrusted code on `pull_request_target` can expose
write privileges or secrets and poison caches. Keep that event limited to safe
base-repository metadata operations. A privileged second-stage
`workflow_run` design has similar artifact and cache trust risks and needs an
explicit producer-verification protocol.

Path and branch filters can leave a required check pending when the workflow is
skipped. GitHub also limits changed-file evaluation. Before adding a filter,
verify required-check behavior and prove the filter cannot exclude code that
affects the deliverable.

## Permissions and credentials

GitHub calculates `GITHUB_TOKEN` permissions from enterprise, organization,
repository, workflow, job, and fork settings. Once any permission is declared,
unspecified permissions become `none`.

Prefer these minimal shapes and add only evidenced capabilities:

```yaml
permissions: {}
```

```yaml
permissions:
  contents: read # checkout repository content
```

Do not copy a generic release permission set. Derive it from the chosen
publisher. For example, creating a GitHub release normally needs
`contents: write`; commenting on issues is a separate capability and must not
be granted merely because another release tool once used it.

Environment secrets become available only after the environment's protection
rules pass. Use that boundary for deployments instead of placing production
credentials in a general CI job.

OIDC replaces stored cloud credentials only after the cloud provider trust is
configured. Restrict subject and other claims; otherwise a short-lived token
can still be over-authorized.

## Action and reusable-workflow pins

GitHub states that a full-length commit SHA is the only immutable action
reference. Tashtit applies the same rule to official, third-party, and internal
remote actions. A tag in a comment preserves readability:

```yaml
- uses: owner/action@0123456789abcdef0123456789abcdef01234567 # v1.2.3
```

Verify the SHA against the upstream repository, not a fork. Configure
Dependabot or Renovate to propose reviewed updates. A repository policy can
also require full-SHA pins.

Local actions use a repository-relative path and have no remote reference:

```yaml
- uses: ./.github/actions/setup
```

Cross-repository reusable workflows accept tags, branches, or SHAs, but
Tashtit requires a full SHA because tags and branches can move. A called
workflow can only reduce `GITHUB_TOKEN` permissions through a chain, not
elevate them. Secrets pass only to directly called workflows; explicitly
forward the narrow subset required at each boundary.

## Concurrency and timeouts

Concurrency groups are case-insensitive. GitHub allows only a bounded set of
running and pending work for a group and does not guarantee arbitrary ordering.
Use the ref for ordinary CI and the actual mutable resource, such as an
environment, for deployments.

The default job timeout is six hours. An explicit shorter timeout bounds cost
and failure detection. Choose it from observed duration plus reasonable
variance, then revisit repeated timeouts rather than continually increasing the
limit.

Cancellation can interrupt cleanup or publishing. Cancel superseded PR
validation by default. For releases and deployments, decide whether to queue,
cancel, or reject based on the publisher's transaction and recovery model.

## Caches, artifacts, and provenance

GitHub distinguishes caches from artifacts:

- caches accelerate reproducible work and may be absent or attacker-influenced;
- artifacts persist outputs or pass them between jobs.

Never store secrets in either. Prefer dependency-manager caches to caching an
installed dependency tree. Include the lockfile digest, runner platform,
runtime, architecture, and other behavior-changing inputs in keys where
relevant.

Artifact upload paths must not expand to the whole workspace or home
directory. Required artifacts fail on absence. Diagnostic artifacts can ignore
absence when their producer legitimately did not run. Retention is a policy and
cost choice; do not invent a universal period.

Artifact attestations provide build provenance, not correctness or
vulnerability absence. Check feature availability and grant the documented
attestation and OIDC permissions only in the producer job.

When immutable GitHub releases are available and fit the release process,
assemble a draft with all assets before publishing because published assets
and their tag cannot then be modified.

## Workflow review checklist

- [ ] Repository instructions, required checks, supported versions, and release
      authority were inspected.
- [ ] PR, trusted push, manual, schedule, and reusable triggers are intentional.
- [ ] Path filters cannot strand or bypass required checks.
- [ ] Untrusted code cannot reach secrets, write tokens, OIDC, protected
      environments, or persistent runners.
- [ ] Untrusted expressions do not flow directly into shell code.
- [ ] Every remote action and reusable workflow uses a verified full commit SHA.
- [ ] Lockfiles and immutable install commands make dependencies reproducible.
- [ ] Every job has an explicit timeout and least-privilege permissions.
- [ ] CI concurrency cancels superseded PR work without racing publication.
- [ ] Independent jobs run in parallel; `needs` models only real dependencies.
- [ ] The actual distributable artifact is tested in a clean consumer where
      applicable.
- [ ] Matrices reflect supported combinations and expensive duplicate work is
      justified.
- [ ] Cache misses are correct and caches contain no sensitive data.
- [ ] Artifact paths, absence behavior, retention, and sensitive-data exclusion
      are explicit.
- [ ] Integration services have bounded readiness, safe diagnostics, and
      unconditional cleanup.
- [ ] Release and deployment jobs use trusted refs, protected environments,
      verified inputs, and a recovery path.
- [ ] Workflow syntax, local commands, observed runs, and failure paths are
      verified without overstating evidence.
