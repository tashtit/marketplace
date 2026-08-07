# Tashtit Marketplace

**Opinionated, production-ready engineering standards for AI coding agents.**

Tashtit is an open-source plugin marketplace for teams that want agents to
work with the same discipline expected from experienced production engineers.
It packages reviewable standards, repeatable workflows, and practical
engineering knowledge for Claude Code, Codex, and GitHub Copilot. Cursor is an
optional compatibility target.

The project is hosted as `tashtit/marketplace`. Its stable marketplace
identifier is `tashtit`.

> [!IMPORTANT]
> Tashtit is in its foundation phase. The repository structure, quality bar,
> and compatibility model are being established before the first stable plugin
> release. Nothing is currently advertised as production-ready.

## Why Tashtit

Agent output should be safe to review, predictable to operate, and suitable for
real repositories. Every stable Tashtit plugin is expected to be:

- **Opinionated:** it recommends a default instead of returning an unranked menu.
- **Production-ready:** it covers failure modes, verification, and operations.
- **Enterprise-minded:** it respects security, auditability, least privilege,
  change control, and repository policy.
- **Portable:** its core behavior is shared across supported agent platforms.
- **Evidence-driven:** normative guidance cites authoritative sources or clearly
  labels a Tashtit convention.
- **Accountable:** every plugin declares its behavior as acceptance scenarios,
  and a maturity claim above experimental requires a recorded passing review of
  each scenario on each claimed platform. Automation enforces that record, not
  the behavior itself.

## Compatibility

| Platform | Priority | Status |
| --- | --- | --- |
| Claude Code | Core | Foundation |
| OpenAI Codex | Core | Foundation |
| GitHub Copilot | Core | Foundation |
| Cursor | Optional | Research |

See [compatibility](docs/compatibility.md) for the adapter model and support
policy.

## Planned catalog

The initial backlog is organized around:

- logging and observability standards;
- reusable infrastructure snippets, beginning with Redis and connection
  lifecycle patterns;
- general engineering standards;
- repository settings and policy;
- repository onboarding;
- code style and maintainability;
- Git and pull-request workflows.

The prioritized scope and acceptance criteria live in the
[roadmap](docs/roadmap.md).

## Available plugins

| Plugin | Version | Maturity | Default behavior |
| --- | --- | --- | --- |
| [API Design Standards](plugins/api-design-standards/) | 0.1.0 | Experimental | Async REST jobs and safe API deprecation |
| [Architecture Diagrams](plugins/architecture-diagrams/) | 0.1.0 | Experimental | C4 system context and container diagrams |
| [Engineering Standards](plugins/engineering-standards/) | 0.1.0 | Experimental | Evidence-backed production change review |
| [Evalkit](plugins/evalkit/) | 0.3.0 | Experimental | Host-adaptive static skill review and worktree-isolated skill/model benchmarks (Claude Code + Copilot CLI) |
| [Git Workflow](plugins/git-workflow/) | 0.1.0 | Experimental | Safe branches, commits, and pull-request handoff |
| [GitHub Actions Standards](plugins/github-actions-standards/) | 0.2.0 | Experimental | Secure, reproducible CI and release workflows |
| [Logging Standards](plugins/logging-standards/) | 0.1.0 | Experimental | Secure structured production logging |
| [Maturity](plugins/maturity/) | 0.3.0 | Experimental | Dockerfile, npm, repository-hygiene, and CI-workflow maturity evaluation, fixes on request |
| [Repository Governance](plugins/repository-governance/) | 0.1.0 | Experimental | Audit repository governance, then optionally apply merge policy and rulesets |
| [Repository Onboarding](plugins/repository-onboarding/) | 0.1.0 | Experimental | Read-only repository assessment |
| [TypeScript Library Build](plugins/typescript-library-build/) | 0.1.0 | Experimental | Dual ESM and CJS library build and publish |

Experimental plugins are published for evaluation and do not carry Tashtit's
stable compatibility or production-readiness claim.

## Repository model

```text
plugins/<plugin-name>/
├── skills/                         # Shared canonical behavior
├── .claude-plugin/plugin.json      # Canonical Claude/Copilot manifest
└── .codex-plugin/plugin.json       # Generated for Codex's required path

.claude-plugin/marketplace.json     # Canonical Claude/Copilot catalog
.agents/plugins/marketplace.json    # Generated Codex catalog
```

Tashtit reuses one file wherever platforms accept the same standard location.
When a format or a required location cannot be shared, provider files are
generated with `make sync` and checked for drift in CI; they are never
maintained as hand-copied implementations, and never as repository symlinks.
See the [architecture](docs/architecture.md) for the full deduplication policy.

## Project status

Tashtit uses maturity levels so installation never implies unsupported
stability:

1. **Experimental:** design is still changing; no compatibility guarantee, and
   no behavioral review is claimed.
2. **Candidate:** automated validation passes and every acceptance scenario has
   a recorded passing review on each claimed platform at the published version.
3. **Stable:** documented compatibility, security review, and release history.
4. **Deprecated:** supported only for a documented migration window.

Only stable plugins may use the `production-ready` label. Every plugin is
currently experimental, so no behavioral review is being claimed yet; reviews
are recorded in `tests/plugins/<name>/acceptance.json` and `make validate`
rejects an unearned maturity claim.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), the
[quality standard](docs/quality-standard.md), and
[SECURITY.md](SECURITY.md) before proposing a plugin. Contributions are
accepted under the [Apache License 2.0](LICENSE).

For project direction, see [GOVERNANCE.md](GOVERNANCE.md). For usage questions,
see [SUPPORT.md](SUPPORT.md).
