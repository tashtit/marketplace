---
name: github-actions-standards
description: Design, simplify, or review GitHub Actions workflow structure and security. Use when deciding what belongs in ci.yml, splitting jobs or reusable workflows, naming steps, or changing CI, artifacts, matrices, releases, and deployments. Covers triggers, permissions, concurrency, runners, caching, secrets, OIDC, environments, action pins, and verification. For a scored read-only hygiene audit, use the maturity plugin's evaluate-ci-workflow.
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

For new CI, start with `.github/workflows/ci.yml`, named `CI`, and a job with
the identifier `ci`. Keep the ordinary delivery path readable in its `jobs:`
block. Choose the smallest shape that proves the repository's contract.

| Repository contract | Default layout in `ci.yml` |
| --- | --- |
| Source checks and unit tests share setup | One `ci` job runs both. |
| Consumers install a package | `ci` builds and packs once. A `smoke` job tests that artifact across supported runtimes. Add service-backed `e2e` only when the integration is part of the contract. |
| Packaging needs another OS or toolchain | `package` depends on `ci`, assembles the distributable and tests it on that runner. |
| An established release follows successful CI | Add a separately permissioned `release` job downstream of all required gates and pass it the tested artifact. Preserve the authorized event and ref. |

Give a workflow its own file when it has an independent lifecycle, such as
a docs site deployed to a separate target or an explicitly required manual
release. Keep validation in the primary file by default. Introduce bootstrap
automation only for an evidenced first-release requirement and identify when
it can be retired.

Before reorganizing an existing workflow, trace each event through its jobs to
its final effect. Preserve required check identities, dry runs, approvals and
the distinction between manual and automatic publication. A change to any of
these requires an explicit delivery decision. Check external references to a
renamed file, including trusted-publisher bindings, badges and dispatch commands.

Apply these conventions to the primary workflow:

- trigger on `workflow_dispatch`, `pull_request`, and push to the actual
  default branch;
- give jobs short, stable lowercase identifiers and set `timeout-minutes`
  on each runner job, including jobs inside reusable workflows. GitHub omits
  that key from the supported keywords on a job that calls a workflow;
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

Read observed check names and required-check settings before renaming jobs,
adding a matrix or introducing a reusable caller. Each can change the check
a ruleset expects.

## Format workflows consistently

Use these Tashtit property orders for the keys present. Omit unused fields.

| Scope | Property order |
| --- | --- |
| Workflow | `name`, `on`, `permissions`, `concurrency`, `env`, `defaults`, `jobs` |
| Runner job | `needs`, `if`, `runs-on`, `timeout-minutes`, `environment`, `concurrency`, `permissions`, `strategy`, `env`, `defaults`, `outputs`, `container`, `services`, `steps` |
| Workflow call | `needs`, `if`, `permissions`, `strategy`, `concurrency`, `uses`, `with`, `secrets` |
| Step | `name`, `id`, `if`, `timeout-minutes`, `continue-on-error`, `uses`, `with`, `env`, `working-directory`, `shell`, `run` |

Give every step a concise, single-quoted name. Use the same name for the same
operation across jobs, such as `'Checkout'`, `'Setup Node.js'`, `'Install'`,
`'Lint'`, `'Test'` and `'Build'`. Qualify names when the distinction matters,
such as `'Test packed package'`. Keep workflow names and job identifiers free
of emoji. Put one blank line between successive steps. Keep properties
together with no other decorative blank lines.

Inline simple maps and lists when the complete indented line fits within
160 columns. Expand nested structures, per-entry comments, multiline values
and longer collections. Preserve whitespace inside scripts. Quote string
inputs and versions so their spelling survives YAML parsing. Keep genuine
numbers and booleans typed. YAML 1.1 loaders can interpret the `on` key as a
boolean, which workflow tooling must account for.

For example, a Node.js repository with a committed npm lockfile, `.nvmrc`
and a test script can start here. Use the repository's actual default branch
and verify the upstream release tags when applying the example.

```yaml
name: 'CI'
on:
  workflow_dispatch:
  pull_request:
  push: { branches: ['main'] }
permissions: {}
concurrency:
  group: '${{ github.workflow }}-${{ github.ref }}'
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
jobs:
  ci:
    runs-on: 'ubuntu-latest'
    timeout-minutes: 10
    permissions: { contents: 'read' }
    steps:
      - name: 'Checkout'
        uses: actions/checkout@v7.0.1
        with: { persist-credentials: false }

      - name: 'Setup Node.js'
        uses: actions/setup-node@v7.1.0
        with: { node-version-file: '.nvmrc', cache: 'npm' }

      - name: 'Install'
        run: npm ci

      - name: 'Test'
        run: npm test
```

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
- name: 'Report pull request title'
  env: { PR_TITLE: '${{ github.event.pull_request.title }}' }
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

Start with no stored secrets. Ordinary build and test jobs should work on fork
PRs with read-only access. Introduce a stored credential only for an evidenced
operation that the automatic job token and federated identity cannot support.
Scope it to the consuming step in its job or protected environment and document
rotation.

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
- name: 'Checkout'
  uses: actions/checkout@v7.0.1
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

Prefer built-in workflow features, existing commands and official GitHub
actions. For actions published by GitHub under `actions/` or `github/`, use
a verified, complete release tag such as `actions/checkout@v7.0.1`. Exact
tags can move. Follow an explicit repository or organization SHA mandate
when present and identify it in the review.

For a third-party action, check the Marketplace publisher and upstream source.
An unverified publisher, including one whose identity cannot be established,
requires explicit user approval for that specific action before adoption.
A verified-creator badge identifies a publisher and confers no GitHub
authorship. Pin any adopted third-party action and any cross-repository
reusable workflow to the full 40-character upstream commit SHA and add the
reviewed release tag in a comment. A SHA alone does not authorize adoption.
Reject branches, `latest`, and partial version tags for all remote references.

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

Default to direct steps. Use safe action defaults and pass only inputs needed
by the repository or this security baseline. Call existing build, test and
release commands directly. Avoid introducing shell implementations, helper
scripts, local composite actions or same-repository reusable workflows just
to wrap setup or a single command. A few repeated checkout and setup lines
make each job readable on its own.

Consider extraction only for substantive, stable logic shared by continuing
callers or for a documented platform requirement. Identify the callers and
what would drift if kept inline. Keep permissions and deployment decisions
visible in the caller, type the inputs and pass only individually named
secrets required by the callee.

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
5. compare the before/after job graph for each supported event, including
   a fork PR, trusted push, manual dry run and authorized publication where
   applicable. Identify which gates run, which artifact advances and the
   first job that can write. Cite observed runs when available. Publishing
   solely to validate a workflow requires separate authorization;
6. test cancellation, cache miss, missing artifact, service timeout, failed
   diagnostics, and cleanup behavior where relevant.

Do not record an unobserved GitHub run as successful. For review-only requests,
lead with findings by severity and cite file and line evidence. Modify files or
external repository settings only when requested.

Read [references/github-actions.md](references/github-actions.md) when choosing
event, permission, pinning, cache, artifact, reusable-workflow, OIDC,
environment, or release behavior, or when an authoritative source is needed.
