---
name: evaluate-repository-hygiene
description: Evaluate a local checkout for repository hygiene issues — missing or malformed CODEOWNERS, missing README, missing CONTRIBUTING guide, and a missing .editorconfig. Use when asked to audit or evaluate repository hygiene, documentation, code ownership, or contributor onboarding, or to score how well a repository is set up for collaboration. Applies deterministic fixes only when the user explicitly asks.
---

# Evaluate repository hygiene

Evaluate a checkout against a fixed catalog of collaboration and documentation
hygiene rules by reading files only. Never contact a remote or run a script to
reach a finding. Fixes are applied only when the user explicitly asks, and only
for rules marked fixable below.

## Discovery

Inspect the repository root and the conventional locations without executing
anything:

- CODEOWNERS: `CODEOWNERS`, `.github/CODEOWNERS`, or `docs/CODEOWNERS`.
- README: `README`, `README.md`, or `README.*` at the repository root.
- CONTRIBUTING: `CONTRIBUTING`, `CONTRIBUTING.md`, or `CONTRIBUTING.*` at the
  root, `.github/`, or `docs/`.
- `.editorconfig` at the repository root.

These rules apply to every repository, so each is always relevant to the score.

## Rules

Each rule lists its stable id, detection, priority, weight, whether it is
automatically fixable, and the reference to cite.

### setup-codeowners (High, weight 8, report-only)

- Detect: no CODEOWNERS file exists in any conventional location.
- Why: without CODEOWNERS, review routing is manual and ownership is
  undocumented, which weakens change control.
- Remediation (manual): add a `.github/CODEOWNERS` mapping paths to the owning
  users or teams. Report only — the correct owners are a project decision that
  must not be guessed.
- Reference: <https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners>

### invalid-codeowners (High, weight 8, report-only)

- Precondition: a CODEOWNERS file exists. If none exists, this rule is not
  relevant and `setup-codeowners` covers the gap.
- Detect: a non-comment, non-blank line that has a path pattern but no owner
  token, or an owner token that is not a valid `@user` or `@org/team-slug`
  (owners must start with `@`; team slugs are `@org/team`). Report the offending
  line numbers.
- Why: malformed entries are silently ignored by GitHub, so intended reviewers
  are never requested.
- Remediation (manual): correct each flagged line to `pattern @owner` form.
  Report only — verifying that an owner exists requires the network and the
  intended owner is a project decision.
- Reference: <https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners#codeowners-syntax>

### setup-readme (High, weight 4, report-only)

- Detect: no `README` file at the repository root.
- Why: a README is the entry point that explains what the repository is and how
  to use it; its absence blocks onboarding.
- Remediation (manual): add a `README.md` describing purpose, setup, and usage.
  Report only — meaningful content cannot be generated without project context.
- Reference: <https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes>

### setup-contributing (Low, weight 3, report-only)

- Detect: no `CONTRIBUTING` file at the root, `.github/`, or `docs/`.
- Why: a contributing guide tells contributors how to set up, test, and submit
  changes, reducing back-and-forth on pull requests.
- Remediation (manual): add a `.github/CONTRIBUTING.md` covering local setup and
  the change workflow. Report only — the content is repository-specific.
- Reference: <https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors>

### setup-editorconfig (Low, weight 1, fixable)

- Detect: no `.editorconfig` at the repository root.
- Why: an `.editorconfig` keeps indentation, charset, and newline behavior
  consistent across editors, avoiding noisy whitespace diffs.
- Fix: create a root `.editorconfig` with the portable defaults below.
- Reference: <https://editorconfig.org>

The fixable default content is:

```ini
# Editor configuration, see https://editorconfig.org
root = true

[*]
end_of_line = lf
charset = utf-8
indent_style = space
indent_size = 2
insert_final_newline = true
trim_trailing_whitespace = true

[*.md]
max_line_length = off
trim_trailing_whitespace = false
```

## Fixing on request

Only `setup-editorconfig` is automatically fixable (write the deterministic
default `.editorconfig` above; never overwrite an existing file). Apply it only
when the user asks. For every other rule, restate the manual remediation instead
of editing files, because each requires project-specific content or a project
decision.
