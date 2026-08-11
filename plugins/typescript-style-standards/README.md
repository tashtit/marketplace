# TypeScript Style Standards

Establish, apply, and review TypeScript and JavaScript code style: type
aliases versus interfaces, readonly immutability, function parameter design,
file and export naming, and type-safety hygiene.

**Maturity: Experimental — 0.1.0.** Style is inherently repository-specific;
this plugin's rules are defaults for convention-free code, never an
instruction to restyle an existing codebase.

The skill puts precedence first: existing repository convention and lint
configuration always win, the skill's defaults apply only where the
repository is silent, and style migrations are separate, lint-driven changes
rather than passengers on feature diffs.

It deliberately does not mandate a linter, formatter, framework, or module
system, and it makes no claim about runtime behavior or performance. Where a
default is genuinely contested - `type` versus `interface` - the requirement
is lint-enforced consistency; the skill states its default, the rationale,
and the one-line lint change that flips it repository-wide.

No network, credentials, or storage are required. Review is read-only unless
implementation is requested.

See [CHANGELOG.md](CHANGELOG.md). Maintainer-only evaluation material lives
outside the distributed plugin in the
[repository test suite](../../tests/plugins/typescript-style-standards/).

## Installation

```bash
# Claude Code
claude plugin marketplace add tashtit/marketplace
claude plugin install typescript-style-standards@tashtit

# GitHub Copilot CLI
copilot plugin marketplace add tashtit/marketplace
copilot plugin install typescript-style-standards@tashtit

# OpenAI Codex CLI
codex plugin marketplace add tashtit/marketplace
codex plugin add typescript-style-standards
```
