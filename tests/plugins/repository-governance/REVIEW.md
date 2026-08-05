# Human review checklist

## Routing (`repository-governance`)

- [ ] A general governance request is routed to the audit skill by default and
      to the apply skill only when the user asks to apply specific settings or a
      supplied ruleset.
- [ ] Ambiguous intent produces an audit inventory and plan before any mutation
      is offered.

## Audit mode (`repository-settings`)

- [ ] The response begins in audit-only mode and identifies scope, evidence,
      authorization, and policy gaps.
- [ ] No repository, organization, or enterprise mutation occurs without
      explicit confirmation and a tested rollback plan.
- [ ] Rulesets or protected branches address targets, inheritance, enforcement,
      bypass actors, reviews, checks, deletion, and force-push controls.
- [ ] Required reviews, status checks, signed changes, and merge methods are
      selected from repository risk and operating context rather than invented.
- [ ] Required checks are stable, relevant, and not sourced from unsafe or
      privileged pull-request execution.
- [ ] CODEOWNERS, issue templates, and security reporting avoid secrets and
      distinguish review routing from authorization.
- [ ] Security features and dependency updates have ownership, triage, safe
      exception handling, and bounded automation.
- [ ] Policy-as-code has a pre-change snapshot, dry-run or diff, read-back,
      representative verification, and executable rollback.
- [ ] Unsafe or incomplete mutation requests are refused and redirected to a
      scoped audit plan.
- [ ] No universal compliance, review-count, signature, merge, or platform
      claim is invented.

## Apply mode (`repository-policy`)

- [ ] Current settings and existing rulesets are read before any change is
      proposed, and admin permission is confirmed.
- [ ] The exact settings and ruleset changes are summarized from-value to
      to-value and explicitly confirmed before being applied.
- [ ] Squash merging is enabled with PR title and commit details; merge commits
      and rebase merging are disabled and at least one method stays enabled.
- [ ] Auto-merge, delete-branch-on-merge, and allow-update-branch are enabled,
      and auto-merge is gated by a ruleset that requires review and checks.
- [ ] Collaboration stays pull-request-only; write access and bypass actors are
      granted only on explicit instruction at least privilege.
- [ ] The wiki and projects features are disabled only when empty and unused; a
      populated feature is left enabled and reported.
- [ ] The ruleset targets the intended branches, keeps deletion,
      non_fast_forward, and linear-history rules, and uses squash-only allowed
      merge methods.
- [ ] Required status-check contexts and integration ids are verified against
      checks that actually run; missing contracts are reported, never invented.
- [ ] Rulesets are preferred over classic branch protection for new work, and
      overlap with existing classic protection is reconciled deliberately.
- [ ] Changes are verified by re-reading settings and the ruleset, and rollback
      steps and prior values are recorded.
- [ ] No repository code, workflow, organization policy, secret, environment, or
      team membership is changed by this plugin, and no compliance or
      production-readiness certification is claimed.

## Both modes

- [ ] Output is materially equivalent on each claimed platform.

After reviewing a scenario on a platform, record the outcome in
`acceptance.json` beside this file. Results are pinned to the plugin version,
so a version bump requires a fresh review.
