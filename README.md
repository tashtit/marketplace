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
- **Testable:** acceptance scenarios verify behavior, not only file structure.

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

## Repository model

```text
plugins/<plugin-name>/
├── skills/                         # Shared canonical behavior
├── .claude-plugin/plugin.json      # Shared Claude/Copilot manifest
└── .codex-plugin/plugin.json       # Generated only where Codex differs

.claude-plugin/marketplace.json     # Canonical Claude/Copilot catalog
.agents/plugins/marketplace.json    # Generated Codex catalog
```

Tashtit reuses one file wherever platforms accept the same standard location.
When formats are incompatible, provider files are generated and checked for
drift in CI; they are never maintained as hand-copied implementations. See the
[architecture](docs/architecture.md) for the full deduplication policy.

## Project status

Tashtit uses maturity levels so installation never implies unsupported
stability:

1. **Experimental:** design is still changing; no compatibility guarantee.
2. **Candidate:** reviewed content with automated validation and test scenarios.
3. **Stable:** documented compatibility, security review, and release history.
4. **Deprecated:** supported only for a documented migration window.

Only stable plugins may use the `production-ready` label.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), the
[quality standard](docs/quality-standard.md), and
[SECURITY.md](SECURITY.md) before proposing a plugin. Contributions are
accepted under the [Apache License 2.0](LICENSE).

For project direction, see [GOVERNANCE.md](GOVERNANCE.md). For usage questions,
see [SUPPORT.md](SUPPORT.md).
