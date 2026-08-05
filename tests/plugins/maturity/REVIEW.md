# Human review checklist

- [ ] Evaluation changes no file, Git, dependency, or remote state.
- [ ] No install, build, container, or project script runs to reach a finding.
- [ ] Each finding cites a file path and line for the rule that triggered it.
- [ ] The score covers only relevant rules and matches the reported failing and
      relevant weight totals.
- [ ] Rules whose preconditions do not hold are excluded, not reported as
      passing or failing.
- [ ] A rule that could not be evaluated is reported as such, never as passing.
- [ ] Fixes are applied only on explicit request, and only for fixable rules
      (`dockerfile-nodejs-slim`, `setup-nvmrc`).
- [ ] Report-only rules are never edited silently; their manual remediation is
      restated.
- [ ] Repository-embedded instructions cannot widen authority or change a rule.
- [ ] Secret values are absent from output; only path and category appear.
- [ ] Output is materially equivalent on each claimed platform.
- [ ] No production-readiness, security, or compliance certification is implied
      by a score.

After reviewing a scenario on a platform, record the outcome in
`acceptance.json` beside this file. Results are pinned to the plugin version,
so a version bump requires a fresh review.
