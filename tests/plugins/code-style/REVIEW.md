# Human review checklist

- [ ] The response identifies the repository's existing style and tooling policy.
- [ ] The proposed change remains focused on the requested behavior.
- [ ] Readability guidance uses clear names, cohesive responsibilities, and
      comments only for non-obvious decisions or invariants.
- [ ] Mechanical formatting is separated from semantic linting, type checks,
      compilation, and tests.
- [ ] The language profile names appropriate formatter and semantic-lint tools
      without claiming that they are mandatory dependencies.
- [ ] Autofixes that can alter behavior, imports, or dependency boundaries are
      reviewed.
- [ ] Generated files are identified and changed only through their documented
      canonical source and regeneration path.
- [ ] Vendored code is protected from style-only churn and preserves upstream
      provenance, licensing, and package metadata.
- [ ] Whole-repository formatting requests are narrowed to a justified scope.
- [ ] Output is materially equivalent on each claimed platform.

After reviewing a scenario on a platform, record the outcome in
`acceptance.json` beside this file. Results are pinned to the plugin version,
so a version bump requires a fresh review.
