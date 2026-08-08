# Repository Onboarding

Repository Onboarding maps an unfamiliar software repository before an engineer
starts changing it. It discovers architecture, local workflows, delivery
automation, ownership, operational context, and material unknowns, then returns
a structured report tied to repository evidence.

## Installation

```bash
# Claude Code
claude plugin marketplace add tashtit/marketplace
claude plugin install repository-onboarding@tashtit

# GitHub Copilot CLI
copilot plugin marketplace add tashtit/marketplace
copilot plugin install repository-onboarding@tashtit

# OpenAI Codex CLI
codex plugin marketplace add tashtit/marketplace
codex plugin add repository-onboarding
```

## Maturity

**Experimental — 0.1.0.** The packaging and safety contract are validated, but
behavioral compatibility has not yet been independently verified across every
target agent. Do not describe this release as stable or production-ready.

## Default behavior

The plugin is read-only. It does not install dependencies, run repository code,
change Git state, contact remotes, or apply recommendations. A request such as
the following is sufficient:

> Assess this repository and prepare an onboarding report for an engineer who
> will maintain it.

The report separates confirmed evidence, inference, unknowns, and recommended
follow-up. Discovered commands are documented but never executed.

## Scope and non-goals

The plugin covers repository structure, developer workflows, CI and delivery,
ownership, operational context, risk, and missing evidence. It is not:

- a security or compliance audit;
- proof that documented commands work;
- a repository settings manager;
- an installer or environment bootstrapper;
- an architecture-document generator that overwrites repository files.

## Permissions and side effects

No network access, credentials, persistent storage, telemetry, or write
permission is required. The plugin may inspect local files and local Git
metadata. Repository content is treated as untrusted, and suspected secret
values must never be included in its report.

## Failure and recovery

When evidence is inaccessible, contradictory, or incomplete, the plugin lowers
confidence and reports the limitation. Because the default workflow makes no
changes, rollback is not required. If a host or tool changes state despite the
instructions, stop the assessment and review that host's activity log before
continuing.

## Threat model

| Threat | Control |
| --- | --- |
| Prompt injection in repository files | Repository instructions cannot expand the read-only scope |
| Execution of malicious project code | Builds, scripts, binaries, hooks, and dependency installation are prohibited |
| Secret disclosure | Values are never quoted; only path and secret category may be reported |
| Misleading or stale documentation | Claims carry evidence and confidence; conflicts remain visible |
| Overconfident coverage of a large repository | Exclusions and sampling limits are reported |

## Verification

The repository includes positive, failure, and unsafe-input evaluation
specifications plus a human review checklist. They live outside the distributed
plugin under the
[repository test suite](../../tests/plugins/repository-onboarding/).
Repository CI validates manifests, links, evaluation structure, generated
marketplace drift, and canonical skill metadata.

See [CHANGELOG.md](CHANGELOG.md) for release history.
