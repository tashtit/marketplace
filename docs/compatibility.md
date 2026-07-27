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
copies. Codex requires distinct catalog policy metadata, so its adapter is
generated from `.claude-plugin/marketplace.json` with the standard Tashtit
defaults (`AVAILABLE` and `ON_INSTALL`) and checked for drift.

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
