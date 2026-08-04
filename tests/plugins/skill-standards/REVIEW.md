# Human review checklist

- [ ] Frontmatter is valid and the description is third person with real triggers.
- [ ] The body is imperative and lean, with detail pushed into references.
- [ ] Every reference named in the body exists with real content.
- [ ] No secrets, hosts, or personal data appear in any skill file.
- [ ] No instruction executes strings built from untrusted repository or issue content.
- [ ] Temporary files use `mktemp` rather than fixed paths.
- [ ] Contradictions between skills, and between a body and its references, are flagged.
- [ ] Rule removal or softening is identified as a behavioral change.
- [ ] Output is materially equivalent on each claimed platform.

After reviewing a scenario on a platform, record the outcome in
`acceptance.json` beside this file. Results are pinned to the plugin version,
so a version bump requires a fresh review.
