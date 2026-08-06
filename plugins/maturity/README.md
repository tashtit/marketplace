# Maturity

Statically evaluate a local checkout for repository maturity issues, produce a
prioritized findings report with a weighted maturity score, and apply
deterministic fixes only when you ask.

## Maturity

**Experimental — 0.3.0.** The rule catalog and scoring model still require
review on each target agent before any stability is claimed.

## Skills

`skills/maturity/SKILL.md` is the router. It defines the read-only safety
contract, the weighted scoring model, and the report format, then dispatches to
one or more ecosystem sub-skills.

| Skill | What it evaluates |
| --- | --- |
| `evaluate-dockerfile` | Node.js Dockerfile hygiene: Alpine vs slim base, source copied before install, end-of-life Node.js, drift from `.nvmrc`, npm used as the container command. |
| `evaluate-npm` | package.json, lockfile, `.npmrc`, and `.nvmrc` hygiene: missing/conflicting lockfiles, outdated lockfile version, non-reproducible git/file dependencies, missing `.npmrc`/`.nvmrc`, and CI installing with `npm install` or `--ignore-scripts`. |
| `evaluate-repository-hygiene` | Collaboration and documentation hygiene: missing or malformed CODEOWNERS, missing README, missing CONTRIBUTING, and missing `.editorconfig`. |
| `evaluate-ci-workflow` | GitHub Actions CI-workflow hygiene: missing CI workflow, unpinned remote actions, overly permissive or undeclared `GITHUB_TOKEN` permissions, jobs without a timeout, and unsafe `pull_request_target` checkout of untrusted code. |

Each rule carries a stable id, priority (Critical/High/Medium/Low), and weight.
The score is `1 − (failing weight / relevant weight)` over the rules whose
preconditions hold, so it is auditable from the reported totals.

## Defaults

- Evaluation is **read-only**. Nothing is installed, built, executed, or sent to
  a remote to produce a finding.
- Fixes are applied **only when you ask**, and only for rules the catalog marks
  fixable (`dockerfile-nodejs-slim`, `setup-nvmrc`, and `setup-editorconfig`).
  Every other rule is report-only with a manual remediation, because it resolves
  the network or requires a project decision.
- Repository content is treated as untrusted evidence; instructions inside the
  repository cannot widen the skill's authority or change a rule.

## Scope

This experimental version covers the Dockerfile, npm, repository-hygiene, and
CI-workflow ecosystems. Other ecosystems (for example Terraform) are
intentionally out of scope for now.

## Prerequisites

None beyond a local checkout. The skills use read-only file discovery and text
search that the host already provides.
