---
name: github-actions-standards
description: Design, implement, or review secure and reproducible GitHub Actions workflows. Use when creating or changing CI, test, build, artifact, matrix, release, deployment, or reusable workflows; choosing triggers, permissions, concurrency, runners, caching, secrets, OIDC, environments, or action pins; or diagnosing unsafe, flaky, redundant, slow, or incomplete automation under .github/workflows.
---

# GitHub Actions Standards

Build the smallest workflow that provides trustworthy evidence for the
repository's actual delivery contract. Apply repository and organization policy
first. Treat this skill as a Tashtit convention and security baseline, not a
certification.

Use `MUST`, `SHOULD`, and `MAY` deliberately. Do not convert a project-specific
tool, runner, registry, branch, secret, or command into a universal rule.

## Inspect before designing

Read the repository's agent instructions, contribution policy, existing
workflows, branch and release conventions, runtime-version files, lockfiles,
package scripts, build outputs, deployment definitions, and test
configuration. Determine:

1. which checks protect a pull request and which are required by repository
   settings;
2. the default and release branches or tags;
3. whether the deliverable is source, a package, binary, image, site, or
   deployment;
4. supported runtimes and platforms;
5. which jobs execute untrusted code, receive secrets, or can write externally;
6. whether any changed-path optimization can safely skip a required check;
7. the commands maintainers actually run locally.

Do not invent missing commands, secret names, environments, registries,
retention periods, or branch-protection behavior. Report a missing contract and
choose a conservative non-publishing baseline when implementation can still
proceed safely.

## Use the standard workflow shape

For the primary continuous-integration workflow, Tashtit conventions are:

- use `.github/workflows/ci.yml`;
- use a stable workflow name such as `🏗️ CI`;
- trigger on `pull_request`, push to the actual default branch, and
  `workflow_dispatch`;
- give every job a stable, simple identifier and an explicit
  `timeout-minutes`;
- define workflow-level concurrency for ordinary CI;
- cancel superseded pull-request runs, but let trusted branch runs finish;
- define exact job-level `permissions`;
- keep independent checks parallel and connect real prerequisites with
  `needs`.

Use this concurrency baseline, replacing nothing with repository-specific
state:

```yaml
concurrency:
  group: '${{ github.workflow }}-${{ github.ref }}'
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
```

Use job-level concurrency instead when release or deployment work needs a
different resource key or cancellation policy. A deployment concurrency group
SHOULD identify the target environment. Never assume execution order within a
concurrency group; make release operations idempotent or otherwise safe under
retries.

Do not use path filters on a required workflow unless repository settings and a
tested check design ensure skipped runs cannot leave a required check pending
or silently bypass relevant validation. A docs-only optimization is a
repository decision, not a default.

Keep job identifiers free of decoration because they become status-check
contracts. Step names SHOULD be concise and diagnostic. Emojis MAY mark a few
high-value steps but MUST NOT carry meaning by themselves.

## Establish the trust boundary

Treat workflow files as privileged code and event payload, branch names, commit
messages, issue or PR text, file contents, artifacts, caches, and fork code as
untrusted input.

- Use `pull_request` for code validation.
- Do not use `pull_request_target` to build, install, test, or execute pull
  request code. If target-context automation is necessary, keep it
  metadata-only and never checkout or execute the untrusted head.
- Do not interpolate untrusted GitHub expressions directly into a `run` script.
  Pass values through an environment variable, quote them in the target shell,
  validate their expected form, and avoid `eval`.
- Do not expose secrets or write tokens to fork code.
- Do not run untrusted contributions on a persistent self-hosted runner unless
  the organization provides documented single-use isolation and cleanup.
- Treat downloaded artifacts and restored caches as untrusted until their
  producer and contents are established.

Use GitHub-hosted runners by default. Use self-hosted runners only for a
documented capability, network, compliance, or performance need, and record
their trust, isolation, patching, and cleanup assumptions.

## Minimize authority

Every job MUST declare only the `GITHUB_TOKEN` permissions it needs. Prefer
`permissions: {}` for jobs that do not need the token and `contents: read` for
checkout-only jobs. Adding one explicit permission makes unspecified
permissions `none`; list each required permission and explain every write grant
with a short comment.

Separate read-only CI from publishing and deployment so untrusted build steps
never share a job with write permissions, protected secrets, or OIDC. Prefer
the built-in `GITHUB_TOKEN` for GitHub operations. Use a GitHub App or another
non-personal identity only when the built-in token cannot meet the documented
requirement.

Prefer OIDC-issued, job-scoped credentials to long-lived cloud secrets. Bind
the provider trust policy to the expected organization, repository, ref,
workflow, and environment. Grant `id-token: write` only to the job that
exchanges the token; it does not itself grant cloud access.

Use a protected GitHub environment for release and deployment jobs. Configure
allowed branches or tags, reviewers when appropriate, and environment-scoped
secrets outside the workflow. Changing repository permissions, secrets,
environments, or protection rules is an external side effect and requires
explicit authorization.

## Pin the supply chain

Remote actions and cross-repository reusable workflows MUST use a full
40-character commit SHA. Add a comment with the human-readable release version
so automated dependency tooling can update it:

```yaml
- uses: actions/checkout@<full-40-character-commit-sha> # vX.Y.Z
```

Do not use a branch, `@latest`, or a movable major tag as the executable
reference. Verify the commit belongs to the intended upstream repository.
Prefer allowlisted, maintained actions with a narrow purpose. Review their
inputs, permissions, network behavior, and release history before adoption.

Use a committed lockfile and the ecosystem's immutable or frozen install
command. Pin command-line tools that are downloaded during the run. Runtime
versions SHOULD come from the repository's canonical version file when the
setup action supports it.

Cache package-manager downloads or safe intermediate data, not secrets. Key
caches from the lockfile and relevant platform inputs. A cache miss MUST still
produce a correct run. Do not treat a cache as a trusted artifact or a required
handoff between jobs.

## Make CI prove the delivery contract

Select checks from repository evidence. A typical application SHOULD run its
formatter check, fast static analysis or lint, type checking where applicable,
tests, and build. A library SHOULD additionally pack or assemble the
distributable artifact and exercise its public entry points in a clean
consumer.

Build once when downstream jobs must verify the same deliverable. Upload that
output as a workflow artifact, then download it in smoke, compatibility, or
release jobs. Do not rebuild an allegedly identical release artifact after
approval.

For required artifacts:

- use a stable unique name and an exact bounded path;
- fail when no expected files exist;
- set the shortest useful retention period from repository policy;
- exclude credentials, environment files, caches, and unrelated workspace
  contents;
- generate provenance or attestations for published artifacts when the
  repository's threat model and GitHub plan support them.

Use a compatibility matrix only for combinations the project claims to
support. Set `fail-fast: false` when seeing all compatibility failures is more
valuable than saving minutes. Run expensive coverage collection once unless
each matrix dimension has a distinct coverage contract.

Split an orthogonal or materially slower check into its own job when parallel
execution improves feedback or the job needs different permissions, runner,
timeout, service, or failure diagnostics. Do not split jobs merely for visual
symmetry; repeated checkout and installation have real cost.

Coverage remains a gate only when thresholds are enforced by the test command
or an enabled external service. Never claim coverage publishing succeeded when
the destination is unavailable or the repository plan does not support it.

## Operate dependencies and failures deliberately

Integration services MUST have a bounded readiness probe instead of a fixed
sleep. On failure, emit safe service diagnostics. Cleanup MUST run with
`if: always()` when a job starts mutable local services or resources.

Upload failure diagnostics with `if: ${{ !cancelled() }}` or the narrower
condition that matches their purpose. Redact secrets and sensitive application
data. Required cleanup and artifact steps MUST state how cancellation affects
them.

Use `continue-on-error` only for a deliberately non-blocking signal whose
status remains visible. Do not hide a required quality gate behind it. Use
retries only for a classified transient external failure, with a small bound,
backoff, and final actionable error; never retry deterministic test failures to
manufacture green runs.

Keep logs actionable: name the operation, show bounded retry or readiness
progress, and emit a clear final failure. Do not enable broad runner or shell
debug logging when it could disclose secrets.

## Isolate release and deployment

A release or deployment job MUST:

1. depend on the exact required CI, artifact, smoke, and integration jobs;
2. run only for explicitly trusted refs and events;
3. use a protected environment when it changes an external system;
4. receive only the permissions and credentials needed for that target;
5. consume the verified build artifact when the delivery model permits;
6. serialize or reject conflicting changes to the same release target;
7. provide a dry-run or non-publishing verification path when the release tool
   supports it;
8. report the published version, digest, target, and rollback or recovery path.

Pull requests MUST NOT publish, deploy, or enter a protected production
environment. A PR dry run must remain read-only and secret-free. Manual
dispatch inputs that affect a release MUST be typed, validated, and visible in
the run; a manual button is not an authorization boundary.

## Reuse without hiding risk

Create a reusable workflow or local composite action only after repeated,
stable behavior exists. Keep repository-specific orchestration in the caller.
Define typed inputs, explicit outputs, narrow permissions, and individually
named secrets. Avoid `secrets: inherit` unless the called workflow genuinely
needs every secret and the trust boundary has been reviewed.

Pin cross-repository reusable workflows by full commit SHA. Version local
interfaces, document breaking changes, and test the caller and reusable
workflow together. Reuse MUST NOT obscure which job can publish, deploy, or
receive secrets.

## Verify changes

After editing:

1. parse and lint every changed workflow with the repository's configured
   validator;
2. inspect the diff for triggers, expression quoting, action pins,
   permissions, secret flow, `if` conditions, `needs`, concurrency groups,
   timeouts, artifact paths, and cleanup;
3. run the repository's local checks that the workflow invokes when safe;
4. verify required check names still match repository settings;
5. observe a pull-request run and each trusted release path before claiming the
   workflow works;
6. test cancellation, cache miss, missing artifact, service timeout, failed
   diagnostics, and cleanup behavior where relevant.

Do not record an unobserved GitHub run as successful. For review-only requests,
lead with findings by severity and cite file and line evidence. Modify files or
external repository settings only when requested.

Read [references/github-actions.md](references/github-actions.md) when choosing
event, permission, pinning, cache, artifact, reusable-workflow, OIDC,
environment, or release behavior, or when an authoritative source is needed.
