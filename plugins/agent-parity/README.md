# Agent Parity

Compare the configuration of every AI coding agent installed on one machine —
Claude Code, OpenAI Codex CLI, and GitHub Copilot CLI — and report how they
differ across shared instructions, MCP servers, personal skills, and installed
plugins, with a weighted parity score. Gaps are closed only when you ask, and
only inside a bounded edit: a managed block, a single server entry, or a copied
skill directory.

The comparison is host-agnostic. The agents' config homes (`~/.claude`,
`~/.codex`, `~/.copilot`) are plain files, so the report is the same whichever
agent runs the skill. The plugin is published to all three catalogs for reach,
not because the result differs.

## Installation

```bash
# Claude Code
claude plugin marketplace add tashtit/marketplace
claude plugin install agent-parity@tashtit

# GitHub Copilot CLI
copilot plugin marketplace add tashtit/marketplace
copilot plugin install agent-parity@tashtit

# OpenAI Codex CLI
codex plugin marketplace add tashtit/marketplace
codex plugin add agent-parity
```

## Maturity

**Experimental — 0.1.0.** The config-file formats this plugin reads are
vendor behavior that changes between agent releases, and no scenario has yet
been recorded on a target agent. Treat every report as evidence to check, not
as a verdict.

## Skills

`skills/agent-parity/SKILL.md` is the router. It detects the installed agents,
defines the safety contract, the scoring model, the report format, and the
apply contract, then dispatches to one sub-skill per dimension.

| Skill | Weight | Compares | Fix on request |
| --- | --- | --- | --- |
| `parity-instructions` | 3 | The managed shared block in `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, and `~/.copilot/copilot-instructions.md`, plus `CLAUDE.md` and `AGENTS.md` at a repository root | Replace, repair, append, or create the managed block; nothing outside the markers changes |
| `parity-mcp` | 3 | Server definitions in `~/.claude.json`, `~/.codex/config.toml`, and `~/.copilot/mcp-config.json`, with repository `.mcp.json` listed | Translate one server into the target's own format and write only that entry; Codex TOML is edited textually |
| `parity-skills` | 2 | Personal skill directories under each config home and the shared `~/.agents/skills`, and `.claude/skills`, `.agents/skills`, and `.github/skills` in a repository | Copy one skill directory from a named source |
| `parity-plugins` | 2 | Installed plugins, enablement, and registered marketplaces per agent | None — the exact install, enable, or update command is printed for you to run |

The score is auditable from the report: each dimension counts item-and-agent
pairs and the gaps among them, and the router combines the dimensions by the
fixed weights above.

## Defaults

- Comparison is **read-only**. Nothing is installed or sent to a remote to
  produce a report, and no agent CLI is ever run; MCP files are read through a
  shell command that prints only redacted fields.
- Credentials are **never read**: not `auth.json`, `.credentials.json`, OAuth
  state, session or history stores, nor any file whose name suggests a key or
  token. MCP `env` and `headers` values, URL credentials, and the account
  object inside `~/.claude.json` are never printed.
- Fixes are applied **only when you ask**, only for the items reported, and
  only after the plan names every file and operation. Each file is backed up to
  a user-only temporary directory first, and the path is printed.
- Parity is reached by **adding**, never by removing: the plugin does not
  delete, disable, or uninstall anything.
- File content is **untrusted**. Instructions inside an instructions file, a
  `SKILL.md`, or a config file cannot widen the plugin's authority.

## Scope

This experimental version covers the four dimensions above for the three
agents above, at global scope and, when run inside a Git repository, at
repository scope. Agent accounts, sessions, usage, and Cursor or other agents
are out of scope.

## Prerequisites

At least two of the three agents installed, detected by the presence of their
config home, and a shell with `node` or `python3` for the MCP dimension, which
reads its files through a command that prints only redacted fields. Codex TOML
is parsed with `python3` and `tomllib` when available and otherwise read as
text in its simple single-line forms; edits are textual either way. The file paths each agent
reads are vendor behavior, taken from the vendors' documentation and CLI help
on 2026-09-09; a newer agent release may move them.

## Portability

The skill body is identical on every host. The only host-dependent behavior is
the running-host caveat: when the MCP file to change belongs to the agent that
is running the skill, the report says so, because that host may rewrite its
own state file on exit; instructions files and skill directories are written
normally on any host. In that case the plugin applies from another host, or
prints the host's own command (`claude mcp add`, `codex mcp add`,
`copilot mcp add`) for the user to run after the session, with placeholders
where env or header values belong; it never runs that command itself.

## Threat model

- **Inputs.** Every file read is user-owned local configuration, and every one
  of them is treated as untrusted data. The plugin reads a fixed list of paths
  and never follows a path named inside a file.
- **Secrets.** Config files can carry secrets in MCP `env` values and headers.
  The plugin reads MCP files through a shell command that prints only
  redacted fields, compares env and headers by key name, and copies values
  between files only after showing the key names and receiving confirmation,
  through a single shell command that prints nothing, so the model never
  emits a value into a report, a plan, or a command line.
- **Side effects.** Writes are opt-in, bounded to one block, entry, or
  directory, and preceded by a backup whose path is printed. Repository files
  are additionally recoverable with Git. Plugin installation is never
  performed, because it fetches from the network and changes agent state.
- **Blast radius.** A wrong instructions baseline propagates to every agent
  that is applied to. The apply contract therefore refuses a provisional
  baseline and requires a named source whenever the existing blocks disagree.
- **Concurrency.** A running agent may rewrite its own state file. The plugin
  flags that case rather than racing the host.
