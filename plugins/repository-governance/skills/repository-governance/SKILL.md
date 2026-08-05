---
name: repository-governance
description: Govern GitHub repository settings, branch protection, and rulesets. Route a request to the right skill — an audit-only review that inventories governance and proposes a reversible plan, or a confirmed apply of Tashtit's standard merge policy and a reviewed ruleset. Use when asked to audit, review, plan, harden, or apply repository settings, branch protection, required reviews or checks, merge methods, or rulesets.
---

# Repository Governance

Repository governance has two distinct modes, and this router selects the right
one. Auditing reads settings and proposes a plan; applying mutates a shared
resource. Keeping them separate keeps read-only review safe by default and makes
every mutation an explicit, confirmable operation. Each sibling skill carries its
own detailed procedure and triggers on its own phrasing; use this router when the
request is general ("help me sort out our repository settings") and hand off once
the intent is clear.

## Choosing a skill

| The user wants to… | Use | Mode | Side effects |
| --- | --- | --- | --- |
| Audit, review, or plan repository/organization governance | `repository-settings` | Read-only by default | None until an approved plan is confirmed |
| Apply Tashtit's standard merge policy and a reviewed ruleset | `repository-policy` | Mutating | Changes shared repository settings; needs `admin` and confirmation |

## Audit versus apply

- **Audit** (`repository-settings`) is a vendor-neutral decision framework with
  GitHub references. It inventories effective rulesets, protected branches,
  reviews, checks, signing, merge methods, CODEOWNERS, templates, security
  features, and dependency updates, then proposes a scoped, reversible plan. It
  MUST NOT mutate settings without explicit confirmation and a tested rollback.
  Prefer it when the question is "what is our governance and what should change?"
- **Apply** (`repository-policy`) applies Tashtit's opinionated default: squash-
  only merges with the PR title and commit details, auto-merge, head-branch
  deletion, suggested branch updates, disabling unused wiki and projects, and a
  branch-protection ruleset from a reviewed definition. Prefer it when the
  question is "apply our standard settings to this repository."

## Routing rules

1. If the request is to review, audit, plan, or check governance — or names
   organization or enterprise scope, compliance, or a change that could weaken
   protections — route to `repository-settings` and stay read-only until an
   approved plan is confirmed.
2. If the request is to apply, set, enable, or enforce specific repository
   settings or a supplied ruleset, route to `repository-policy`. Confirm the
   target `owner/repo` and each from/to value before mutating, and never
   fabricate a check context, integration id, reviewer, or branch to make a
   definition validate.
3. When intent is ambiguous, default to the audit skill first: produce the
   inventory and plan, then hand off to apply only after explicit confirmation.

Neither skill manages organization-wide policy defaults, secrets, environments,
webhooks, team membership, or repository code. Each sibling skill also triggers
directly on its own description, so an explicit request (or `/<skill-name>`)
reaches it without going through this router.
