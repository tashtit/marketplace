# Changelog

All notable changes to this plugin are documented here. Versions follow
[Semantic Versioning](https://semver.org/).

## 0.1.0 - 2026-09-09

### Added

- Router skill that detects the installed agents by config home (`~/.claude`,
  `~/.codex`, `~/.copilot`, with `CLAUDE_CONFIG_DIR` and `CODEX_HOME`
  overrides), defines the read-only safety contract and the credential
  deny-list, computes a weighted parity score over item-and-agent pairs, and
  fixes the apply contract: explicit request, plan before write, user-only
  backup, no removals, no agent CLI runs, running-host caveat.
- `parity-instructions` skill: one managed block per scope inside
  `<!-- agent-parity:shared:start -->` and `<!-- agent-parity:shared:end -->`
  markers across the three global instructions files and repository
  `CLAUDE.md` plus `AGENTS.md`, with the legacy `cockpit:shared` markers read
  as the same block. Statuses are in sync, out of date, not applied, not
  adopted, and not evaluated; a repository `CLAUDE.md` that imports or links
  `AGENTS.md` inherits its status. Apply replaces, repairs, appends, or
  creates the block and never touches text outside it.
- `parity-mcp` skill: server inventory from `~/.claude.json` (user and
  local scope), `~/.codex/config.toml`, and `~/.copilot/mcp-config.json`,
  with repository `.mcp.json` listed, read through a shell command that
  prints only redacted fields and compared by transport (http versus sse),
  command, args, url, and env and header key names. Apply translates one
  server into the target agent's own format and edits Codex TOML textually,
  leaving every other line byte-identical.
- `parity-skills` skill: personal skill directories compared by name and a
  whole-directory fingerprint across every directory each agent documents,
  including the shared `~/.agents/skills`, the repository `.claude/skills`,
  `.agents/skills`, and `.github/skills` locations, and linked directories.
  Apply copies one directory from a named source, replaces one (moving the
  existing directory to a printed backup) when the user says replace, or
  creates a symlink when the user asks for one.
- `parity-plugins` skill: installed plugins, versions, enablement, and
  marketplaces per agent, with agent-native marketplaces and catalog
  `platforms` exclusions. Report-only; each gap is returned as the agent's
  own install, enable, or update command.
- Positive, failure, and unsafe-input acceptance scenarios.
