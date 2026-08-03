---
name: repository-settings
description: Design, apply, or review GitHub repository settings and rulesets safely. Use when configuring merge methods, auto-merge, head-branch deletion, pull-request review policy, collaborator access, suggested branch updates, wiki and projects features, or when creating or updating a repository ruleset or branch protection from a reviewed definition.
---

# Repository Settings

Apply a small, auditable repository policy that makes the default branch hard to
break and pull requests the only path to it. Repository settings are an external
side effect on a shared resource, so treat every change as a privileged,
confirmable operation. Apply organization and repository policy first, and treat
this skill as a Tashtit convention rather than a certification.

Use `MUST`, `SHOULD`, and `MAY` deliberately. Do not turn one repository's
required check name, branch name, integration id, or reviewer into a universal
rule.

## Scope and non-goals

This skill covers repository-level settings and rulesets: merge methods,
auto-merge, automatic head-branch deletion, suggested branch updates, the
pull-request review and collaboration model, and the wiki and projects features.
It also covers applying a repository ruleset from a reviewed JSON definition.

It does not manage organization-wide policy, secrets, environments, deploy keys,
webhooks, team membership, or billing. It does not write repository code or
workflow files. It does not certify compliance.

## Inspect before changing

Read the repository's agent instructions and contribution policy, then read the
current settings and any existing rulesets or classic branch protection **before
proposing a change**. Determine:

1. the actual default branch and any additional protected branches;
2. which merge methods are enabled and whether history is expected to be linear;
3. whether auto-merge, suggested updates, and head-branch deletion are already
   configured;
4. the current pull-request review requirement and collaborator model;
5. whether the wiki and projects features are enabled and whether they contain
   real content;
6. which status checks and apps actually run, so a ruleset requires real check
   contexts rather than invented ones;
7. whether you have `admin` permission on the repository, which every change in
   this skill requires.

Read the current state with the REST API rather than assuming it:

```bash
gh api repos/{owner}/{repo} \
  --jq '{default_branch, allow_squash_merge, allow_merge_commit, allow_rebase_merge,
         allow_auto_merge, delete_branch_on_merge, allow_update_branch,
         squash_merge_commit_title, squash_merge_commit_message,
         has_wiki, has_projects}'
gh api repos/{owner}/{repo}/rulesets --jq '.[] | {id, name, target, enforcement}'
```

Do not invent a default branch, required check, integration id, reviewer, or
ruleset name. If the contract is missing, report it and stop rather than
guessing.

## Require explicit confirmation

Repository settings are externally visible and affect every collaborator, so
changing them is a destructive-class action. Before applying anything:

- summarize the exact settings and ruleset you will change, from-value to
  to-value;
- confirm the target `owner/repo` and default branch;
- get explicit confirmation from the requester;
- prefer a dry run: print the request bodies and the resulting diff without
  sending them when the caller has not yet approved.

Never widen access, delete a ruleset, disable an enabled feature that holds
content, or lower a protection level without a specific instruction to do so.
Record the previous values so the change can be rolled back.

## Set the standard merge policy

Tashtit's default merge policy keeps a linear, reviewable history and one
predictable merge shape:

- enable squash merging only; disable merge commits and rebase merging;
- set the squash commit to use the **pull request title and commit details**,
  so the squashed commit message is derived from the PR title and the body lists
  the squashed commits;
- enable **allow auto-merge** so an approved pull request that satisfies its
  required checks merges without a manual click;
- enable **automatically delete head branches** so merged topic branches are
  cleaned up;
- enable **always suggest updating pull request branches** so reviewers can
  bring a branch up to date with the base before merging.

Apply all of these in one request and echo the result:

```bash
gh api -X PATCH repos/{owner}/{repo} \
  -F allow_squash_merge=true \
  -F allow_merge_commit=false \
  -F allow_rebase_merge=false \
  -f squash_merge_commit_title=PR_TITLE \
  -f squash_merge_commit_message=COMMIT_MESSAGES \
  -F allow_auto_merge=true \
  -F delete_branch_on_merge=true \
  -F allow_update_branch=true
```

`squash_merge_commit_title=PR_TITLE` with
`squash_merge_commit_message=COMMIT_MESSAGES` is GitHub's encoding for "pull
request title and commit details". At least one merge method MUST remain enabled;
GitHub rejects a repository with every method disabled, so keep squash enabled
while disabling the other two.

Do not enable auto-merge without a ruleset or branch protection that requires
review and status checks, because auto-merge only helps once required conditions
gate the merge. Configure the ruleset first or in the same change.

## Restrict collaboration to pull requests

The default branch MUST be reachable only through a pull request, and only
collaborators may open pull requests that run privileged automation.

- Do not grant write access to people who only need to propose changes; keep
  outside contributions on forks.
- Require a pull request and at least one approving review before merge through a
  ruleset (below), not through informal convention.
- Keep the fork pull-request policy aligned with the repository's trust model;
  restricting who can trigger privileged workflows is a repository decision,
  documented in policy rather than assumed here.

Changing collaborator or team access is an access-control change. Make it only on
explicit instruction, name the exact principal and permission, and prefer the
least privilege that satisfies the request.

## Disable unused wiki and projects

Disable a feature only when it is both unused and not part of the repository's
workflow. Reducing attack surface is good, but disabling a feature that holds
content destroys or hides that content.

- Check whether the wiki and the projects features are enabled and whether they
  contain real pages or boards before changing anything.
- Disable the wiki when it is empty and unused; disable projects when no board is
  in use.
- If a feature holds content, leave it enabled and report it rather than
  discarding data. Treat disabling a populated feature as a destructive action
  that needs an explicit, informed instruction.

```bash
gh api -X PATCH repos/{owner}/{repo} -F has_wiki=false -F has_projects=false
```

Wiki content lives in a separate `.wiki` Git repository and is not deleted by
toggling `has_wiki`, but it becomes inaccessible through the UI; still confirm
before disabling. State clearly that this only affects repository features, not
the code or its history.

## Apply the ruleset from a reviewed definition

Protect the default branch (and any additional named branches) with a repository
ruleset built from a **reviewed** JSON definition. A ruleset is the enforceable
form of the merge and review policy above.

Validate the definition before sending it:

1. confirm `target` is `branch` and `conditions.ref_name.include` names the
   intended branches; `~DEFAULT_BRANCH` targets the repository's default branch
   without hard-coding its name;
2. confirm `enforcement` is the intended value (`active` to enforce, `evaluate`
   to observe without blocking, `disabled` to stage);
3. confirm every `required_status_checks` context and `integration_id` matches a
   check and app that actually run in this repository; a wrong or invented
   integration id silently fails to require the check;
4. confirm `pull_request.allowed_merge_methods` matches the enabled merge methods
   (squash only, to match the policy above);
5. confirm `bypass_actors` grants only the intended actors a bypass, and that a
   broad bypass such as organization admins is a deliberate, documented choice;
6. keep `deletion`, `non_fast_forward`, and, when linear history is required,
   `required_linear_history` rules so the branch cannot be deleted or
   force-pushed.

Never fabricate status-check contexts, integration ids, reviewers, or bypass
actors to make a supplied definition validate. If the definition references a
check that does not exist yet, report it and let the requester decide whether to
add the check or remove the requirement.

Create a new ruleset, or update the matching existing one, from the reviewed
file:

```bash
# Inspect existing rulesets first and reuse the id when one already governs the
# same branches, rather than creating a duplicate.
gh api repos/{owner}/{repo}/rulesets --jq '.[] | {id, name, target}'

# Create from the reviewed definition.
gh api -X POST repos/{owner}/{repo}/rulesets --input ruleset.json

# Or update an existing ruleset in place, preserving its id.
gh api -X PUT repos/{owner}/{repo}/rulesets/{ruleset_id} --input ruleset.json
```

Prefer repository rulesets over classic branch protection for new work because
rulesets layer, target multiple refs, and expose bypass actors explicitly. When
a repository already relies on classic branch protection, reconcile deliberately
rather than leaving two overlapping controls that disagree.

See [references/repository-settings.md](references/repository-settings.md) for
the authoritative REST fields, the squash-title encoding, ruleset rule types, and
the annotated example derived from a supplied `Branch Protection` definition.

## Verify and report

After applying changes:

1. re-read the repository settings and rulesets and confirm each field matches
   the intended value;
2. confirm exactly one merge method (squash) is enabled and the other two are
   disabled;
3. confirm the ruleset targets the correct branches, enforces the intended rules,
   and requires only checks that exist;
4. open a throwaway test pull request only when the repository policy allows it,
   to confirm auto-merge, suggested updates, and required review behave as
   expected; otherwise state that live behavior was not exercised;
5. report every changed setting from-value to to-value, the ruleset id and
   enforcement state, and the rollback steps.

Do not record a settings or ruleset change as applied unless the re-read
confirms it. For review-only requests, report findings by severity with the
exact field and current value as evidence, and change nothing.
