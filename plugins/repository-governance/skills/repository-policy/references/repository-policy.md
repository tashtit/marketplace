# Repository settings reference

Authoritative field names and encodings for GitHub repository settings and
rulesets. Prefer the current
[GitHub REST API for repositories](https://docs.github.com/en/rest/repos/repos)
and
[rules](https://docs.github.com/en/rest/repos/rules)
documentation when GitHub behavior is volatile; the fields below are Tashtit's
mapping of the standard, not a replacement for it.

## Merge and cleanup fields

Set through `PATCH /repos/{owner}/{repo}`
([reference](https://docs.github.com/en/rest/repos/repos#update-a-repository)):

| Field | Type | Standard value | Effect |
| --- | --- | --- | --- |
| `allow_squash_merge` | boolean | `true` | Enable squash merging. |
| `allow_merge_commit` | boolean | `false` | Disable merge commits. |
| `allow_rebase_merge` | boolean | `false` | Disable rebase merging. |
| `allow_auto_merge` | boolean | `true` | Allow auto-merge on eligible PRs. |
| `delete_branch_on_merge` | boolean | `true` | Delete head branch after merge. |
| `allow_update_branch` | boolean | `true` | Always suggest updating PR branches. |
| `squash_merge_commit_title` | enum | `PR_TITLE` | Squash commit title source. |
| `squash_merge_commit_message` | enum | `COMMIT_MESSAGES` | Squash commit body source. |
| `has_wiki` | boolean | `false` when unused | Wiki feature toggle. |
| `has_projects` | boolean | `false` when unused | Projects feature toggle. |

At least one of `allow_squash_merge`, `allow_merge_commit`, and
`allow_rebase_merge` MUST remain `true`; GitHub rejects a repository with all
three disabled.

### Squash commit title and message encoding

"Pull request title and commit details" in the web UI corresponds to:

- `squash_merge_commit_title=PR_TITLE`
- `squash_merge_commit_message=COMMIT_MESSAGES`

Other documented combinations, for reference:

| UI choice | title | message |
| --- | --- | --- |
| Default to PR title | `PR_TITLE` | `PR_BODY` |
| PR title and commit details | `PR_TITLE` | `COMMIT_MESSAGES` |
| PR title and description | `PR_TITLE` | `PR_BODY` |

The equivalent `merge_commit_title` and `merge_commit_message` fields apply only
when merge commits are enabled, which the standard policy disables.

## Ruleset structure

Repository rulesets are managed through
`GET|POST /repos/{owner}/{repo}/rulesets` and
`GET|PUT|DELETE /repos/{owner}/{repo}/rulesets/{id}`
([reference](https://docs.github.com/en/rest/repos/rules)). A ruleset has:

- `name`: human-readable identifier;
- `target`: `branch`, `tag`, or `push`;
- `enforcement`: `active` (enforce), `evaluate` (log only, higher plans), or
  `disabled` (staged);
- `conditions.ref_name.include` / `exclude`: refs the ruleset applies to;
  `~DEFAULT_BRANCH` matches the repository default branch and `~ALL` matches all
  branches without hard-coding names;
- `rules`: an array of typed rule objects;
- `bypass_actors`: actors permitted to bypass, each with a `bypass_mode` of
  `always` or `pull_request`.

### Common rule types

| `type` | Purpose |
| --- | --- |
| `deletion` | Block branch deletion. |
| `creation` | Restrict who can create matching refs. |
| `non_fast_forward` | Block force pushes. |
| `required_linear_history` | Require a linear history (no merge commits). |
| `pull_request` | Require a pull request with review before merge. |
| `required_status_checks` | Require named status checks to pass. |
| `copilot_code_review` | Request automated review on matching pull requests. |

Key `pull_request.parameters`:

- `required_approving_review_count`: minimum approvals;
- `dismiss_stale_reviews_on_push`: dismiss approvals when new commits arrive;
- `require_code_owner_review`: require CODEOWNERS approval;
- `require_last_push_approval`: require approval of the most recent push;
- `required_review_thread_resolution`: require resolved review threads;
- `allowed_merge_methods`: the merge methods a PR may use, for example
  `["squash"]` to match a squash-only repository.

Key `required_status_checks.parameters`:

- `strict_required_status_checks_policy`: require the branch be up to date with
  the base before merge;
- `required_status_checks`: an array of `{ "context": <check name>,
  "integration_id": <app id> }`. The `context` MUST match a check that actually
  reports on the repository, and `integration_id` MUST identify the app that
  reports it. A wrong or omitted integration id can cause the requirement to
  match nothing and silently pass.

### Bypass actors

Each entry in `bypass_actors` names an `actor_type` (such as
`OrganizationAdmin`, `RepositoryRole`, `Team`, or `Integration`), an optional
`actor_id`, and a `bypass_mode`. A broad bypass such as organization admins
weakens the control; keep it only when it is a deliberate, documented decision,
and prefer the narrowest actor and `pull_request` bypass mode that satisfies the
operational need.

## Annotated example

The definition below is derived from a supplied `Branch Protection` ruleset. It
protects the default branch and a `beta` branch, requires a reviewed pull
request with resolved threads, requires a set of status checks that must exist in
the repository, keeps history linear, and blocks deletion and force pushes.
Replace the `required_status_checks` contexts and `integration_id` values with
the repository's real checks before applying; the values here are illustrative,
not universal.

```json
{
  "name": "Branch Protection",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "exclude": [],
      "include": ["~DEFAULT_BRANCH", "refs/heads/beta"]
    }
  },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "creation" },
    { "type": "required_linear_history" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": true,
        "require_last_push_approval": true,
        "required_review_thread_resolution": true,
        "allowed_merge_methods": ["squash"]
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "do_not_enforce_on_create": false,
        "required_status_checks": [
          { "context": "ci", "integration_id": 15368 }
        ]
      }
    },
    {
      "type": "copilot_code_review",
      "parameters": {
        "review_on_push": false,
        "review_draft_pull_requests": false
      }
    }
  ],
  "bypass_actors": [
    {
      "actor_id": null,
      "actor_type": "OrganizationAdmin",
      "bypass_mode": "always"
    }
  ]
}
```

`allowed_merge_methods: ["squash"]` keeps the ruleset consistent with the
squash-only repository merge policy. Because `required_linear_history` is set,
merge commits would be rejected anyway; enabling only squash at the repository
level avoids offering a method the ruleset forbids.

## Rollback

Each setting is reversible by sending the previous value to the same `PATCH`
endpoint. A ruleset is reversible by restoring its prior definition with `PUT`,
or by deleting a newly created ruleset with
`DELETE /repos/{owner}/{repo}/rulesets/{id}`. Record the pre-change values (from
the inspection step) before applying so a rollback restores the exact prior
state. Disabling `has_wiki` does not delete the separate wiki Git repository, but
restoring UI access requires re-enabling the feature.
