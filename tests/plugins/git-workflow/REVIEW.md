# Human review checklist

- [ ] Existing work and unrelated changes remain intact.
- [ ] The active branch is not the default branch.
- [ ] Repository, account, identity, and signing checks are explicit.
- [ ] The staged diff is focused and secret-free.
- [ ] Validation evidence is exact.
- [ ] Commit messages match repository policy.
- [ ] Push and pull-request effects were authorized.
- [ ] No destructive recovery, unauthorized rewrite, merge, or settings change occurs.
- [ ] Output is materially equivalent on each claimed platform.

After reviewing a scenario on a platform, record the outcome in
`acceptance.json` beside this file. Results are pinned to the plugin version,
so a version bump requires a fresh review.
