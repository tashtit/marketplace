# Repository Governance

Govern GitHub repository settings, branch protection, and rulesets. A router
skill dispatches between two modes: an audit-first review that inventories
governance and proposes a reversible plan, and a confirmed apply of Tashtit's
standard merge policy and a reviewed ruleset.

**Maturity: Experimental — 0.2.0.** Repository, organization, enterprise, and
regulatory policy remain authoritative. This plugin does not certify compliance
or configuration security, and it does not turn one repository's required check
name, integration id, reviewer, or branch into a universal rule.

## Installation

```bash
# Claude Code
claude plugin marketplace add tashtit/marketplace
claude plugin install repository-governance@tashtit

# GitHub Copilot CLI
copilot plugin marketplace add tashtit/marketplace
copilot plugin install repository-governance@tashtit

# OpenAI Codex CLI
codex plugin marketplace add tashtit/marketplace
codex plugin add repository-governance
```

## Skills

- **`repository-governance`** — router. Selects audit versus apply from the
  request and hands off to the matching skill.
- **`tashtit-repository-settings`** — audit-only by default. Collects read-only evidence
  for rulesets and protected branches, reviews, checks, signing, merge methods,
  CODEOWNERS, templates, security features, and dependency updates, then proposes
  a scoped plan with owners, confirmation, verification, snapshots, and rollback.
  It never mutates settings without explicit confirmation and a tested rollback.
- **`tashtit-repository-policy`** — apply. Applies Tashtit's default merge policy
  (squash-only with the pull-request title and commit details, auto-merge,
  head-branch deletion, suggested branch updates), disables unused wiki and
  projects, restricts collaboration to pull requests, and applies a
  branch-protection ruleset from a reviewed definition — each change inspected,
  confirmed, verified, and reversible.

The two modes are deliberately separate so read-only review is safe by default
and every mutation is an explicit, privileged operation.

## Scope and non-goals

It does not manage organization-wide policy defaults, secrets, environments,
deploy keys, webhooks, team membership, or billing, and it does not write
repository code or workflow files. Applying settings changes a shared repository
and requires `admin` permission; read-only inspection uses documented GitHub APIs
or CLI commands with least privilege and disclosed network access. The plugin
itself requires no credentials, network service, telemetry, or persistent storage
beyond the GitHub API access used to read and write settings.

See [CHANGELOG.md](CHANGELOG.md). Maintainer-only evaluation material lives
outside the distributed plugin in the
[repository test suite](../../tests/plugins/repository-governance/).
