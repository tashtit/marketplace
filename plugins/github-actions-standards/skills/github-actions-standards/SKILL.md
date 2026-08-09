---
name: github-actions-standards
description: Design, implement, or review secure and reproducible GitHub Actions workflows. Use when creating or changing CI, test, build, artifact, matrix, release, deployment, or reusable workflows; choosing triggers, permissions, concurrency, runners, caching, secrets, OIDC, environments, or action pins; or diagnosing unsafe, flaky, redundant, slow, or incomplete automation under .github/workflows. For a scored, read-only maturity audit of existing workflows, use the maturity plugin's evaluate-ci-workflow instead.
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
- use a short, stable workflow name such as `CI`;
- trigger on `workflow_dispatch`, `pull_request`, and push to the actual
  default branch;
- give every job a short, stable, lowercase identifier such as `build`,
  `test`, or `release`, and an explicit `timeout-minutes`;
- do not set a job-level `name`; the identifier is the display name;
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

A job's status check appears as `<workflow name> / <job id>`, so both halves
are contracts: keep the workflow name short and stable, keep job identifiers
undecorated lowercase tokens, and do not hide an identifier behind a job-level
`name`. Step names SHOULD be concise and diagnostic. Emojis MAY mark a few
high-value steps but MUST NOT appear in workflow or job names and MUST NOT
carry meaning by themselves.

Quote string values in `with:`, `env:`, and runtime-version fields. Unquoted
YAML scalars are type-coerced, which silently changes what an action receives:
`node-version: 20.10` becomes the number `20.1`, and `no` becomes `false`.
Booleans and numbers that are genuinely typed, such as
`persist-credentials: false` or `timeout-minutes: 10`, stay unquoted. Note that
a bare `on:` key is itself parsed as the boolean `true` by YAML loaders, so
tooling that reads workflows MUST NOT assume the string key.

## Establish the trust boundary

Treat workflow files as privileged code and event payload, branch names, commit
messages, issue or PR text, file contents, artifacts, caches, and fork code as
untrusted input.

- Use `pull_request` for code validation.
- Do not use `pull_request_target` to build, install, test, or execute pull
  request code. If target-context automation is necessary, keep it
  metadata-only and never checkout or execute the untrusted head.
- Do not interpolate a GitHub expression directly into a `run` script. Bind the
  value to an `env:` entry on the step and read it back with ordinary shell
  expansion, quoted: `"${VARNAME}"`, never `${{ env.VARNAME }}`.
- Do not expose secrets or write tokens to fork code.
- Do not run untrusted contributions on a persistent self-hosted runner unless
  the organization provides documented single-use isolation and cleanup.
- Treat downloaded artifacts and restored caches as untrusted until their
  producer and contents are established.

An expression is substituted into the script text before any shell parses it,
so a value carrying a quote, `$(…)`, a backtick, or a newline becomes runner
code rather than an argument. A shell variable stays data. This applies to
`${{ env.VARNAME }}` too, even for a variable the workflow defines itself: the
substitution happens the same way, and a workflow-level or job-level `env`
value can still originate in event payload, a matrix entry, a prior step's
output, or a reusable-workflow input. Prefer the binding, quote the expansion,
validate the expected form, and avoid `eval`:

```yaml
- env:
    PR_TITLE: '${{ github.event.pull_request.title }}'
  run: |
    printf 'title: %s\n' "${PR_TITLE}"
```

Bind literal configuration the same way rather than reading it back through an
expression, so a later change to where the value comes from cannot turn a safe
line into an injection point. Expressions remain correct outside `run` — in
`if:`, `with:`, `env:`, and other workflow-syntax fields, which are not shell
input.

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

Scoped permissions still leave the token reachable. `actions/checkout`
persists the job's credential on the runner filesystem by default: versions
before v6 write it into the checked-out `.git/config`, while v6 and later
store it under `$RUNNER_TEMP`. In both cases it stays usable by every later
step in that job, including build scripts and their transitive dependencies,
and it can escape the run entirely when a step packages the workspace into an
artifact.

Every `actions/checkout` step SHOULD therefore set `persist-credentials`
explicitly, so the choice is a reviewed decision rather than an inherited
default. Consider each checkout in turn and ask whether any later step in the
same job must authenticate as the repository — push a commit or tag, fetch
another private repository, call the API through git credentials. When none
does, which is the common case for build and test jobs, choose `false`:

```yaml
- uses: actions/checkout@<ref>
  with: { persist-credentials: false }
```

When one does, declare `persist-credentials: true` and say in a comment which
step needs it, then isolate that step in its own job with the narrowest
permissions. Auditing a workflow includes flagging any checkout that leaves the
setting unstated.

Prefer OIDC-issued, job-scoped credentials to long-lived cloud secrets. Bind
the provider trust policy to the expected organization, repository, ref,
workflow, and environment. Grant `id-token: write` only to the job that
exchanges the token; it does not itself grant cloud access.

Pass secrets through a secret-aware action input or, when a command requires
them, a narrowly scoped environment variable or standard input. Secrets MUST
NOT appear in workflow source, generated scripts, command-line arguments, or
ordinary log output. Disable shell tracing around secret-bearing commands and
delete secret-bearing temporary files with cleanup that also runs on failure.

GitHub log redaction is a defense in depth, not a guarantee. Register every
derived or transformed secret with `::add-mask::` before it can reach output.
Store unrelated sensitive values as separate secrets rather than one structured
blob when feasible, because redaction depends on matching known values. Test
failure paths with synthetic values and inspect their logs. If a secret reaches
a log, delete the log where possible, revoke or rotate the credential, and
investigate the exposure before rerunning.

Use a protected GitHub environment for releases and deployments to shared,
stable, or production targets. Configure allowed branches or tags, reviewers
when appropriate, and environment-scoped secrets outside the workflow.
Changing repository permissions, secrets, environments, or protection rules
is an external side effect and requires explicit authorization.

## Pin the supply chain

Remote actions SHOULD use a full 40-character commit SHA. Non-GitHub-authored
actions and cross-repository reusable workflows MUST use one. Add a comment
with the human-readable release version so automated dependency tooling can
update it:

```yaml
- uses: actions/checkout@<full-40-character-commit-sha> # vX.Y.Z
```

An action authored by GitHub in the `actions` or `github` organization MAY use
a complete release tag such as `@v6.0.2` when repository policy intentionally
trusts GitHub as the publisher and does not require SHA pinning. This is a
convenience exception, not an immutability claim; prefer a full SHA for jobs
with secrets, write permissions, OIDC, or deployment authority.

Do not use a branch, `@latest`, or a movable major tag such as `@v6` as the
executable reference. Verify a pinned commit belongs to the intended upstream
repository and an exact tag identifies the intended release. Prefer
allowlisted, maintained actions with a narrow purpose. Review their inputs,
permissions, network behavior, and release history before adoption.

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

Prefer a single job while every check shares one toolchain and setup and the
combined runtime stays short; a repository's structural validation and its
unit tests usually belong together. Split an orthogonal or materially slower
check into its own job when parallel execution improves feedback or the job
needs different permissions, runner, timeout, service, or failure
diagnostics. Do not split jobs merely for visual symmetry; repeated checkout
and installation have real cost.

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

A release job or a deployment job targeting a shared, stable, or production
environment MUST:

1. depend on the exact required CI, artifact, smoke, and integration jobs;
2. run only for explicitly trusted refs and events;
3. use a protected environment when it changes an external system;
4. receive only the permissions and credentials needed for that target;
5. consume the verified build artifact when the delivery model permits;
6. serialize or reject conflicting changes to the same release target;
7. provide a dry-run or non-publishing verification path when the release tool
   supports it;
8. report the published version, digest, target, and rollback or recovery path.

Pull requests MUST NOT publish releases or deploy to a shared, stable, or
production target. A pull request MAY deploy an ephemeral preview only when:

- an unprivileged `pull_request` job builds and tests the exact artifact;
- any credential-bearing deploy step consumes that verified artifact without
  checking out or executing contributor-controlled code;
- the target is isolated per pull request and contains no production data;
- credentials are short-lived, least-privilege, non-production credentials;
- public forks are excluded unless the preview path is demonstrably safe
  without exposing credentials or trusted infrastructure;
- a bounded lifetime, quota, and cost limit exist; and
- cleanup is idempotent and uses provider expiry or trusted, metadata-only base
  code that never executes the pull request head.

A PR dry run MUST remain non-publishing and MUST NOT receive production
credentials. It MAY receive a narrowly scoped non-production credential only
when the same isolation requirements apply. Manual dispatch inputs that affect
a release MUST be typed, validated, and visible in the run; a manual button is
not an authorization boundary.

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
2. inspect the diff for triggers, expressions reaching `run` scripts, scalar
   quoting and YAML type coercion, action pins, permissions, explicit
   `persist-credentials` on every checkout, secret flow, `if` conditions,
   `needs`, concurrency groups, timeouts, artifact paths, and cleanup;
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
