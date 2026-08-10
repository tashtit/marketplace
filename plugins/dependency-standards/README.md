# Dependency Standards

Decide whether a third-party dependency may enter a codebase, on evidence
rather than availability, and keep it pinned, recorded, updated, and removable
afterwards.

**Maturity: Experimental — 0.1.0.** Licensing decisions, allowed license sets,
approval authority, and registry policy remain repository-specific and are not
legal advice. This plugin does not certify a dependency, a license, or a supply
chain.

The default is a blocking gate for a new dependency: need, alternatives, real
usage and maintenance health, provenance, license, security and capability
exposure, and pinning and exit control are each answered with evidence and
committed as a dependency record before the dependency is declared. An update
gets a lighter but non-optional review — read the change, confirm the trust
facts still hold, and re-record the pinned version — so bot-authored bumps are
not merged unread.

The standard is ecosystem-neutral and applies to language packages, CI actions
and reusable workflows, container base images, system packages, fetched
binaries, IaC modules, and plugins. The reference material carries concrete
evidence commands for npm, GitHub Actions, containers, Python, Go, and Rust,
license classes with default handling, and the record shape that makes the gate
enforceable in CI.

It deliberately does not mandate a registry, scanner, license allowlist,
package manager, or update bot, and it does not decide license compatibility on
a project's behalf.

The skill reads manifests and public package metadata. Evidence commands
contact public registries and are read-only; adopting, updating, or removing a
dependency edits repository files and requires the usual review. No credentials
or persistent storage are required.

See [CHANGELOG.md](CHANGELOG.md). Maintainer-only evaluation material lives
outside the distributed plugin in the
[repository test suite](../../tests/plugins/dependency-standards/).

## Installation

```bash
# Claude Code
claude plugin marketplace add tashtit/marketplace
claude plugin install dependency-standards@tashtit

# GitHub Copilot CLI
copilot plugin marketplace add tashtit/marketplace
copilot plugin install dependency-standards@tashtit

# OpenAI Codex CLI
codex plugin marketplace add tashtit/marketplace
codex plugin add dependency-standards
```
