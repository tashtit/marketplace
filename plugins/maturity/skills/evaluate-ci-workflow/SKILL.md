---
name: evaluate-ci-workflow
description: Evaluate a local checkout for GitHub Actions CI-workflow hygiene issues — missing CI workflow, unpinned remote actions, overly permissive or undeclared GITHUB_TOKEN permissions, jobs without a timeout, and unsafe pull_request_target checkout of untrusted code. Use when asked to audit or evaluate CI, GitHub Actions, workflow security, action pinning, or token permissions, or to score how safe and reproducible a repository's automation is. Reports findings only; does not edit workflows — to design, fix, or harden workflows, use github-actions-standards.
---

# Evaluate CI-workflow hygiene

Evaluate a checkout against a fixed catalog of GitHub Actions CI-workflow rules
by reading `.github/workflows/*.yml` and `.github/workflows/*.yaml` only. Never
run a workflow, contact a remote, or resolve a tag to a commit to reach a
finding. Every rule below is report-only: CI fixes depend on the repository's
delivery contract, so restate the manual remediation instead of editing files.

This evaluator aligns with the `github-actions-standards` skill; cite it when a
finding needs the full rationale.

## Discovery

Inspect the workflow directory without executing anything:

- CI workflows: every `*.yml` or `*.yaml` file under `.github/workflows/`.
- Parse each as YAML. If a file cannot be parsed, report it as unparseable and
  skip its content rules rather than guessing.

The `setup-ci-workflow` rule is always relevant. The remaining rules apply only
when at least one parseable workflow file exists.

## Rules

Each rule lists its stable id, detection, priority, weight, and the reference to
cite. All rules are report-only.

### setup-ci-workflow (High, weight 6, report-only)

- Detect: no `*.yml` or `*.yaml` file exists under `.github/workflows/`.
- Why: without CI, no automated check protects a pull request, so regressions
  reach the default branch unverified.
- Remediation (manual): add a `.github/workflows/ci.yml` that runs the
  repository's real lint, type-check, test, and build commands on
  `pull_request` and pushes to the default branch. Report only — the correct
  commands are a project decision.
- Reference: <https://docs.github.com/en/actions/using-workflows/about-workflows>

### unpinned-action (High, weight 8, report-only)

- Precondition: a workflow references a remote action or reusable workflow.
- Detect: check the executable ref on each remote `uses`. GitHub-authored
  actions under `actions/` and `github/` use exact release tags such as
  `v7.0.1` by convention. Honor an explicitly supplied SHA-only policy.
  Third-party actions and cross-repository workflow calls require a full
  40-character commit SHA. Exclude local paths and container references.
  Report a failing pin with its actual form. Mention an official action's full
  SHA as a style observation outside the score when the tag convention applies.
  A full SHA already satisfies the integrity goal of this scored rule.
- Remediation (manual): identify the expected pin form and cite the line.
  Leave release resolution, publisher verification and any required user
  approval to the implementation review. Offline inspection cannot prove
  those properties.
- Reference: <https://docs.github.com/en/actions/reference/security/secure-use#using-third-party-actions>

### overly-permissive-permissions (High, weight 8, report-only)

- Precondition: a parseable workflow exists.
- Detect: a blanket `GITHUB_TOKEN` grant — the scalar `permissions: read-all` or
  `permissions: write-all` — at the workflow top level or on any job. Report
  each location. A scoped `permissions:` map (for example `contents: read` with
  `packages: write`) is the recommended least-privilege form and is not flagged
  here; a job that needs no scoped `write` is instead covered by
  `missing-workflow-permissions` when it declares nothing at all.
- Why: `write-all` grants every scope at once and `read-all` grants every read
  scope, so a compromised step in that job inherits far more authority than it
  needs. A scoped map, by contrast, is auditable and least-privilege.
- Remediation (manual): replace the broad grant with the exact permissions each
  job needs, preferring `permissions: {}` for jobs that do not use the token
  and `contents: read` for checkout-only jobs. Report only.
- Reference: <https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token>

### missing-workflow-permissions (Medium, weight 5, report-only)

- Precondition: a parseable workflow exists and does not already trigger
  `overly-permissive-permissions`.
- Detect: a workflow that declares no `permissions:` block at the top level and
  has at least one job that also declares none. Report the workflow.
- Why: with no explicit `permissions:`, jobs inherit the repository default
  token scope, which is often broader than the workflow requires.
- Remediation (manual): add an explicit `permissions:` block scoped to the
  minimum each job needs. Report only.
- Reference: <https://docs.github.com/en/actions/using-jobs/assigning-permissions-to-jobs>

### ci-workflow-job-missing-timeout (Medium, weight 5, report-only)

- Precondition: a parseable local workflow contains a runner job (`runs-on`).
- Detect: report each runner job missing `timeout-minutes` by file and job id,
  including runner jobs in local reusable workflows. A job-level `uses` calls
  a workflow and cannot declare a timeout. A step-level `uses` is an action
  within a runner job and the job still needs a timeout.
- Why: a job without a timeout can hang until the runner limit, wasting minutes
  and delaying feedback instead of failing fast.
- Remediation (manual): add `timeout-minutes` to the runner job, sized to its
  expected duration. Report only.
- Reference: <https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idtimeout-minutes>
- [Supported caller keywords](https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations#supported-keywords-for-jobs-that-call-a-reusable-workflow)

### unsafe-pull-request-target (High, weight 9, report-only)

- Precondition: a workflow is triggered by `pull_request_target`.
- Detect: the same workflow checks out the pull request head — for example an
  `actions/checkout` step whose `ref` is `github.event.pull_request.head.sha`,
  `github.event.pull_request.head.ref`, or `github.head_ref`. Report the
  workflow and step.
- Why: `pull_request_target` runs with repository secrets and a read-write
  token in the base-repository context; checking out and running fork code
  under it lets an untrusted contributor exfiltrate secrets or write to the
  repository.
- Remediation (manual): validate untrusted pull requests with `pull_request`
  instead, or keep the `pull_request_target` job metadata-only and never
  checkout or execute the untrusted head. Report only — the safe redesign
  depends on what the workflow needs to do.
- Reference: <https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/>

## Fixing on request

No rule in this ecosystem is automatically fixable. A correct CI fix depends on
the repository's build, test, permission, and release contract, so restate the
manual remediation and defer the implementation to the `github-actions-standards`
skill when the user asks for changes.
