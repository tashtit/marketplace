# GitHub Actions reference

Use this reference for platform-defined behavior and detailed review
decisions. The normative defaults in `SKILL.md` are Tashtit conventions unless
this file identifies a GitHub requirement.

## Contents

- [Source basis](#source-basis)
- [Trigger and checkout decisions](#trigger-and-checkout-decisions)
- [Expressions in `run` scripts](#expressions-in-run-scripts)
- [Permissions and credentials](#permissions-and-credentials)
- [Action and reusable-workflow pins](#action-and-reusable-workflow-pins)
- [Concurrency and timeouts](#concurrency-and-timeouts)
- [Release and preview deployments](#release-and-preview-deployments)
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
- [Deploying with GitHub Actions](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments):
  deployment events, environments, concurrency, and deployment URLs.
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

## Expressions in `run` scripts

GitHub evaluates `${{ … }}` while assembling the step, then writes the result
into the script file the runner executes. The shell therefore parses attacker
influence as syntax. GitHub's script-injection guidance names the mitigation:
bind the value to an environment variable and let the shell expand it.

```yaml
# unsafe: the title becomes part of the script
- run: echo "title: ${{ github.event.pull_request.title }}"

# unsafe: env.* is substituted the same way
- env:
    PR_TITLE: '${{ github.event.pull_request.title }}'
  run: echo "title: ${{ env.PR_TITLE }}"

# safe: the shell reads a variable, and the value stays data
- env:
    PR_TITLE: '${{ github.event.pull_request.title }}'
  run: |
    printf 'title: %s\n' "${PR_TITLE}"
```

`${{ env.VARNAME }}` deserves specific attention because it looks like a
variable read and is not. Whether the entry was defined at workflow, job, or
step level, the expression is expanded before the shell runs, so the binding
buys nothing. It also hides provenance during review: a workflow-level `env`
value can be a literal today and a `github.event.*` value, matrix entry, step
output, or reusable-workflow input after the next change, which silently
converts the line into an injection. Reading `"${VARNAME}"` is correct in both
states, so use it unconditionally inside `run`.

Quote the expansion. `${VARNAME}` unquoted still word-splits and glob-expands
in POSIX shells. On `shell: pwsh` or `shell: powershell` the equivalent read is
`$env:VARNAME`; on `shell: cmd` it is `%VARNAME%`. Composite-action `run` steps
follow the same rule, with `inputs.*` bound through `env` rather than
interpolated.

Expressions stay correct outside `run` scripts. Workflow-syntax fields such as
`if:`, `with:`, `env:`, `name:`, and `concurrency.group` are consumed by
Actions itself, not by a shell. `if:` still deserves care because it evaluates
its argument, so compare untrusted values rather than embedding them in a
constructed expression.

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

`actions/checkout` persists the job's `GITHUB_TOKEN` on the runner unless
`persist-credentials: false` is set. Before v6 it lands in the workspace
`.git/config` as an extraheader; from v6 it moves to `$RUNNER_TEMP`, which
keeps it out of an archived workspace but leaves it usable by every subsequent
step in the job. Neither location is scoped to the step that needs it, so any
later command — a build script, a test helper, a transitive dependency — can
authenticate as the repository with whatever the job's `permissions` allow.

Treat the setting as a per-checkout decision and state it either way. Consider
what the job does after checkout: a job that only reads the tree wants `false`;
a job that pushes a commit or tag, fetches another private repository, or
drives git-authenticated tooling needs `true` and should carry a comment naming
the step that requires it, sit in its own job, and hold the narrowest
`permissions` for that work. A checkout with no `persist-credentials` key is a
review finding on its own — the default is permissive and the intent is
unrecorded. Alternatives to persistence include a step-scoped token in `env`
for a single `gh` or `git push` invocation, or a separate credential such as a
GitHub App installation token when the built-in token is not appropriate.

Environment secrets become available only after the environment's protection
rules pass. Use that boundary for deployments instead of placing production
credentials in a general CI job.

Prefer secret-aware action inputs. When a command must consume a secret, pass
it through a narrowly scoped environment variable or standard input, not
through a command-line argument or interpolated script. Avoid shell tracing and
clean up temporary secret files on success, failure, and cancellation.

GitHub attempts to redact registered secret values from logs, but redaction is
not guaranteed. Mask derived or transformed sensitive values with
`::add-mask::` before any output can contain them. Prefer separate secret
values over structured blobs such as JSON when practical, because a changed or
partially rendered structure may not match the registered value. Exercise
failure diagnostics with synthetic secrets. If a real value is exposed,
delete the affected logs where possible, revoke or rotate it, and investigate
before rerunning.

OIDC replaces stored cloud credentials only after the cloud provider trust is
configured. Restrict subject and other claims; otherwise a short-lived token
can still be over-authorized.

## Action and reusable-workflow pins

GitHub states that a full-length commit SHA is the only immutable action
reference. Tashtit therefore requires full SHAs for non-GitHub-authored remote
actions and cross-repository reusable workflows, and prefers them for every
remote action. A tag in a comment preserves readability:

```yaml
- uses: owner/action@0123456789abcdef0123456789abcdef01234567 # v1.2.3
```

GitHub's own secure-use guidance also recognizes tags as a convenient choice
when the creator is trusted. Tashtit permits this only for GitHub-authored
actions in the `actions` and `github` organizations, only with a complete
release tag such as `@v6.0.2`, and only when repository or organization policy
does not require SHA pinning:

```yaml
- uses: actions/checkout@v6.0.2
```

The exact tag improves version intent but remains movable or deletable, so it
MUST NOT be described as immutable. Prefer the SHA form for any job with
secrets, write permissions, OIDC, or deployment authority. Major-only tags,
branches, and `@latest` are not permitted by this exception.

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

## Release and preview deployments

GitHub supports deployments from `pull_request` workflows and can associate a
deployment URL with a pull request. Tashtit permits that behavior only for an
ephemeral, per-PR preview. It is not an exception for publishing releases or
deploying to shared, stable, or production targets.

Build and test the preview artifact in the unprivileged pull-request context.
If deployment requires credentials, a trusted deploy step may consume the
verified artifact but must not checkout, install, or execute the contributor
head. Give every preview an isolated target, non-production data and
least-privilege credentials, a bounded lifetime and cost, and deterministic
cleanup. Exclude public forks unless the design remains safe without disclosing
credentials or granting access to trusted infrastructure.

Cleanup triggered by pull-request closure has its own trust boundary. Prefer a
provider TTL or a metadata-only workflow that uses base-repository code and
never executes the pull-request head. Cleanup must be idempotent because event
delivery, cancellation, and retries can overlap.

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
- [ ] No `run` script interpolates an expression, including `${{ env.X }}`;
      values are bound through `env:` and read as quoted `"${VARNAME}"`.
- [ ] Every `actions/checkout` sets `persist-credentials` explicitly, and any
      `true` names the step that needs it.
- [ ] Secrets avoid source and command-line arguments; derived values are
      masked before output and exposure response is defined.
- [ ] Every non-GitHub action and cross-repository reusable workflow uses a
      verified full commit SHA; a GitHub-authored action uses either the
      preferred SHA or a policy-approved exact release tag.
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
- [ ] Releases and shared or stable deployments use trusted refs, protected
      environments, verified inputs, and a recovery path.
- [ ] Any PR preview is isolated, non-production, bounded, artifact-based, and
      cleaned up without executing contributor code in a privileged context.
- [ ] Workflow syntax, local commands, observed runs, and failure paths are
      verified without overstating evidence.
