# Human review checklist

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
      team membership is changed by this skill.
- [ ] No compliance or production-readiness certification is claimed.
- [ ] Output is materially equivalent on each claimed platform.

After reviewing a scenario on a platform, record the outcome in
`acceptance.json` beside this file. Results are pinned to the plugin version,
so a version bump requires a fresh review.
