# Code Style

Design, implement, and review readable, maintainable code with clear
formatting, semantic-linting, and generated-code boundaries.

**Maturity: Experimental — 0.1.0.** Repository policy, language tooling, and
generator ownership always take precedence; this plugin makes no universal
correctness or production-readiness claim.

The skill defines language-neutral readability and change-scope guidance,
separates mechanical formatting from semantic linting, and provides practical
profiles for TypeScript/JavaScript, Python, Go, and Java. It also protects
generated and vendored code from unsafe hand edits and indiscriminate churn.

It deliberately does not mandate a programming language, formatter, linter,
build system, complexity limit, or repository-wide rewrite. Map the guidance to
the repository's configured tools and policy.

No network, credentials, telemetry, or storage are required. Review is
read-only unless implementation is requested.

See [CHANGELOG.md](CHANGELOG.md). Maintainer-only evaluation material lives
outside the distributed plugin in the
[repository test suite](../../tests/plugins/code-style/).
