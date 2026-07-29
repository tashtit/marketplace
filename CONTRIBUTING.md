# Contributing to Tashtit

Thank you for helping make agent-assisted engineering more reliable.

## Before you start

- Search existing issues and the [roadmap](docs/roadmap.md).
- Use an issue for substantial plugins, behavioral changes, new dependencies,
  or architecture changes.
- Report vulnerabilities privately as described in [SECURITY.md](SECURITY.md).
- Read the [Code of Conduct](CODE_OF_CONDUCT.md).

## Development workflow

1. Create a focused branch from the default branch.
2. Make one coherent change.
3. Add or update documentation and acceptance scenarios with behavior.
4. Run the validation described below.
5. Open a pull request using the repository template.

Use Conventional Commits for commit messages:

```text
<type>(<optional-scope>): <imperative summary>
```

Common types are `feat`, `fix`, `docs`, `test`, `refactor`, `build`, and
`chore`. Do not mix unrelated changes in one commit or pull request.

## Proposing a plugin

A proposal must identify:

- the engineering problem and intended users;
- the recommended default and material alternatives;
- risks, permissions, side effects, and recovery behavior;
- authoritative sources and Tashtit-specific opinions;
- supported platforms and known differences;
- acceptance scenarios and expected outcomes;
- an owner or maintenance plan.

Plugin names use lowercase kebab-case and must describe a capability, not a
vendor endorsement.

## Quality requirements

Every contribution must satisfy [docs/quality-standard.md](docs/quality-standard.md).
In particular:

- examples must be safe to copy and must use placeholders for secrets;
- commands must state prerequisites and meaningful side effects;
- destructive or externally visible operations must include confirmation and
  recovery guidance;
- shared standards and files must be reused across platforms where possible;
- platform-specific files must be links or deterministic generated adapters,
  never hand-maintained copies, and never repository symlinks when the provider
  parses the file itself;
- stable guidance must not depend on an unpinned mutable external source.

## Validation

The repository validator has no third-party runtime dependencies. Before
opening a pull request:

```bash
make sync
make validate
```

`make sync` regenerates the unavoidable Codex artifacts from canonical sources:
the Codex marketplace from `.claude-plugin/marketplace.json`, and each
`.codex-plugin/plugin.json` from that plugin's `.claude-plugin/plugin.json`.
Never edit a generated file by hand; change the canonical source and re-run
`make sync`.

`make validate` fails when any generated file drifts and also checks JSON
syntax, marketplace alignment, the plugin catalog tables in `README.md` and
`plugins/README.md`, plugin naming and manifest consistency, recorded acceptance
results against the claimed maturity, safe links, canonical skill presence,
local documentation links, and whitespace. CI runs the same validation on every
push and pull request.

Nothing here executes an acceptance scenario. Raising a plugin's maturity above
`experimental` requires recording a passing review for every scenario and claimed
platform at the published version in `tests/plugins/<name>/acceptance.json`;
see [the quality standard](docs/quality-standard.md). Bumping a plugin's version
invalidates earlier results, because the reviewed behavior changed.

## Review

Maintainers review correctness, security, portability, operational completeness,
and long-term maintenance cost. Review may request evidence or narrower scope.
Approval indicates the contribution meets the current maturity level; it is not
an endorsement by any platform vendor.
