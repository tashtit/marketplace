---
name: code-style
description: Design, implement, or review readable and maintainable code across TypeScript/JavaScript, Python, Go, and Java. Use when setting code-style policy, choosing formatters or linters, reviewing change scope, handling generated or vendored code, or separating mechanical formatting from semantic correctness checks.
---

# Code Style

Create code that is easy to read, change, review, and verify. Apply the
repository's established style, formatter, linter, build, and generated-code
policy before this vendor-neutral baseline. This skill does not replace an
architecture review, security review, compiler, type checker, or tests.

`MUST`, `SHOULD`, and `MAY` distinguish requirements, strong defaults, and
optional practices. Tashtit conventions in this skill are project preferences,
not externally defined standards.

## Preserve readability and change scope

- A change MUST solve the stated problem without unrelated renames, rewrites,
  dependency upgrades, formatting churn, or behavior changes.
- Code MUST use names that explain domain intent and preserve established local
  terminology. Prefer small cohesive functions and types over clever,
  compressed control flow.
- A function or module SHOULD have one clear responsibility, explicit inputs
  and outputs, and straightforward error handling. Extract a helper when it
  gives a stable name to repeated or difficult-to-read logic.
- Comments MUST explain a non-obvious decision, invariant, or external
  constraint; they MUST NOT restate the code. Remove comments made stale by the
  change.
- A review SHOULD distinguish blocking correctness or maintainability findings
  from optional stylistic preferences. Do not invent a style rule when the
  repository has an established formatter or linter.
- A change MAY include a narrowly scoped cleanup when it directly improves the
  modified code's safety or clarity and does not obscure the intended diff.

## Separate formatting from semantic linting

**FORMATTING** is a mechanical, deterministic presentation transformation:
whitespace, indentation, wrapping, punctuation layout, import ordering where
the formatter owns it, and other changes that do not alter program meaning. A
formatter SHOULD be pinned and run on changed supported files. Formatting MUST
be safely autofixable and MUST NOT substitute for review, compilation, tests,
or semantic analysis.

**SEMANTIC LINTING** detects likely defects or maintainability risks: unused or
unreachable code, incorrect APIs, unsafe patterns, complexity, error handling,
type inconsistencies, and invalid imports. A semantic linter MUST report the
rule and location; its autofixes MUST be reviewed because they can change
behavior. Type checking, static analysis, and compiler warnings remain
separate explicit gates even when a linter invokes them.

Repositories SHOULD run formatters and semantic checks independently in CI,
with documented versions, configuration roots, and file scopes. Do not use a
whole-repository formatter run to conceal a behavioral change or to repair an
unrelated baseline.

## Language profiles

Use the repository's configured tools if they differ. These profiles name
common tooling boundaries, not mandatory dependencies.

### TypeScript and JavaScript

- **FORMATTING:** [Prettier](https://prettier.io/docs/) owns mechanical layout.
  It MAY be combined with import organization only when the repository has a
  deterministic configured tool.
- **SEMANTIC LINTING:** [ESLint](https://eslint.org/docs/latest/) owns
  JavaScript and TypeScript rule enforcement. Run `tsc --noEmit` or the
  repository's configured TypeScript check separately for type correctness.
- ESLint autofixes MUST be reviewed when rules can modify imports, control flow,
  or runtime behavior. Do not encode Prettier formatting rules in ESLint unless
  the repository intentionally maintains that integration.

### Python

- **FORMATTING:** [Black](https://black.readthedocs.io/) or
  [Ruff's formatter](https://docs.astral.sh/ruff/formatter/) owns deterministic
  layout.
- **SEMANTIC LINTING:** [Ruff](https://docs.astral.sh/ruff/linter/) or
  [Flake8](https://flake8.pycqa.org/) owns configured source rules; use
  [mypy](https://mypy.readthedocs.io/) separately when the project type-checks.
- A repository MUST choose one formatter for a file set. Do not run competing
  formatters with incompatible output.

### Go

- **FORMATTING:** [gofmt](https://pkg.go.dev/cmd/gofmt) owns Go formatting;
  [goimports](https://pkg.go.dev/golang.org/x/tools/cmd/goimports) MAY own
  import grouping when configured.
- **SEMANTIC LINTING:** [go vet](https://pkg.go.dev/cmd/vet) and
  [Staticcheck](https://staticcheck.dev/docs/) identify likely defects and
  maintainability risks. `go test` remains a separate verification step.
- Go code SHOULD follow `gofmt` output without local formatting exceptions.
  Review `goimports` changes because imports can expose dependency boundaries.

### Java

- **FORMATTING:** [google-java-format](https://github.com/google/google-java-format)
  or [Spotless](https://github.com/diffplug/spotless) owns mechanical layout.
- **SEMANTIC LINTING:** [Checkstyle](https://checkstyle.org/) enforces configured
  source rules, while [Error Prone](https://errorprone.info/) detects likely
  correctness bugs. Compiler warnings and tests remain explicit gates.
- Spotless MAY orchestrate formatting and import order, but a repository SHOULD
  keep semantic rules separately identifiable and reportable.

## Handle generated and vendored code safely

Before changing code, identify generated or third-party content from repository
policy, directory conventions such as `generated/`, `dist/`, `vendor/`, or
`third_party/`, file banners such as "generated" or "do not edit", lockfile
metadata, and build or package manifests. Treat markers as signals to verify,
not proof of safety.

- Generated files MUST NOT be hand-edited. Change the canonical source,
  generator input, template, schema, or generator version; then run the
  documented deterministic regeneration command and include only its expected
  output.
- Generated paths SHOULD be excluded from editor-on-save formatting and
  semantic-lint noise. CI MAY verify generated output is current with a
  dedicated drift check.
- Vendored code MUST NOT receive style-only rewrites. Preserve upstream history,
  licensing notices, checksums, and package metadata. Apply a local patch only
  when repository policy permits it, document the reason and upstream version,
  and prefer an upstream update or reproducible patch mechanism.
- A request to reformat an entire repository, generated output, or vendor tree
  MUST be scoped to a justified file set and confirmed against repository
  policy. Refuse unsafe hand edits and propose changing the source or running
  the approved generator instead.

## Verify a style change

1. Identify repository configuration, file ownership, generated and vendored
   exclusions, and the smallest affected file set.
2. Run the configured formatter in check or scoped-write mode.
3. Run configured semantic linting, type checking, compilation, and targeted
   tests independently where available.
4. Review the diff for accidental behavior changes, import churn, generated
   drift, and unrelated files.
5. Report commands not run and any tool-version or policy uncertainty rather
   than claiming a universal style or correctness guarantee.
