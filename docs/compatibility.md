# Compatibility

## Support policy

Tashtit distinguishes distribution compatibility from behavioral
compatibility:

- **Distribution compatibility** means the platform can discover and load the
  plugin.
- **Behavioral compatibility** means its acceptance scenarios produce
  materially equivalent outcomes on that platform.

A platform is supported only when both are tested for the plugin version.

## Platform matrix

| Platform | Marketplace adapter | Plugin adapter | Project status |
| --- | --- | --- | --- |
| Claude Code | Shared `.claude-plugin/marketplace.json` | Shared `.claude-plugin/plugin.json` | Core target |
| OpenAI Codex | `.agents/plugins/marketplace.json` | `.codex-plugin/plugin.json` | Core target |
| GitHub Copilot | Reuses `.claude-plugin/marketplace.json` | Reuses `.claude-plugin/plugin.json` | Core target |
| Cursor | To be defined | To be defined | Optional research |

GitHub Copilot officially discovers the Claude marketplace and plugin
locations, so Tashtit uses those shared files rather than keeping Copilot
copies. Codex requires distinct catalog policy metadata, so its catalog is
generated from `.claude-plugin/marketplace.json` with the standard Tashtit
defaults (`AVAILABLE` and `ON_INSTALL`) and checked for drift.

Codex plugin manifests need no field translation, but Codex only discovers a
manifest at `.codex-plugin/plugin.json`, so each one is generated from the
plugin's canonical `.claude-plugin/plugin.json`. Symlinking the two is not an
option: a checkout with `core.symlinks=false` turns the manifest into a text
file holding the link target, which no host can parse. Both Codex artifacts are
produced by `make sync` and must never be hand-edited.

## Per-plugin platform targeting

By default a plugin targets every core platform. A plugin MAY narrow this by
declaring a `platforms` array on its entry in `.claude-plugin/marketplace.json`,
listing values from `claude-code`, `codex`, `github-copilot`, and `cursor`.

The shared `.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json`
are read directly by both Claude Code and GitHub Copilot, so a plugin in the
catalog is inherently discoverable by both; `platforms` cannot hide it from
either. Codex is the only platform with a separately generated adapter, so
omitting `codex` from `platforms` suppresses that plugin's Codex catalog entry
and `.codex-plugin/plugin.json` — `make sync` does not generate them and
`make validate` fails if a stale one is present. This keeps a Copilot-only
plugin (for example, one whose harnesses invoke `copilot -p`) out of the Codex
catalog rather than advertising an installable adapter it cannot honor.

Declaring `platforms` sets distribution intent only; behavioral support is still
established per platform by acceptance scenarios and recorded results.

## Compatibility rules

- The canonical skill name and plugin name must remain stable across adapters.
- Versions, descriptions, licenses, and source paths must agree.
- A provider-specific file must be justified by an incompatible schema or
  capability; naming preference alone is not sufficient.
- Links must remain within the plugin package and work in every supported
  checkout and cache path.
- Generated adapters must be reproducible and validated in CI.
- Unsupported capabilities must be omitted or documented; adapters must not
  invent fallbacks with different security behavior.
- A platform-specific defect blocks stable support for that platform, not
  necessarily the entire plugin.
- Support claims include the tested platform version and date.
- Preview or undocumented platform APIs are experimental by default.

## Adding a platform

A new platform requires:

1. official, publicly reviewable packaging documentation;
2. a local or CI validation mechanism;
3. a mapping for skills, permissions, hooks, commands, and MCP servers;
4. acceptance-test coverage;
5. a maintainer willing to own compatibility;
6. documented installation, update, and removal behavior.

## Primary specifications

- [Claude Code plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Codex plugin structure](https://developers.openai.com/codex/plugins/build#plugin-structure)
- [GitHub Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference)
- [Cursor plugin announcement](https://cursor.com/blog/marketplace)

These links document provider behavior. Tashtit's maturity, portability, and
quality requirements remain project conventions.
