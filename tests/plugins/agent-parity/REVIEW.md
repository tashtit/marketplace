# Human review checklist

- [ ] Comparison changes no config home, repository, or Git state.
- [ ] No agent CLI (including `plugin list` or `mcp list`), install, or network
      call runs to produce the report.
- [ ] Credential files are never opened: `auth.json`, `.credentials.json`,
      OAuth state, session and history stores, and any name suggesting a key
      or token.
- [ ] MCP `env` and `headers` values, URL userinfo and query strings, and the
      account object in `~/.claude.json` never appear in the output.
- [ ] Agent detection is a directory check on the resolved config home, and a
      single installed agent yields "not applicable", not a score.
- [ ] The score covers only item-and-agent pairs where the agent is installed
      and the item is expected, and matches the reported pair and gap counts
      per dimension and the fixed weights.
- [ ] Excluded pairs (project-scoped, agent-native, not supported, user-named)
      leave the denominator and are labelled as such.
- [ ] A file that could not be parsed is reported as "not evaluated", never as
      in parity.
- [ ] Instructions: only the text between managed markers is compared,
      printed, or written; legacy `cockpit:shared` markers are recognized; a
      provisional baseline is never applied; a scope with no block is "not
      adopted" and outside the score.
- [ ] MCP: the inventory is read through a shell command that prints only
      redacted fields, and env and header values are copied only through a
      shell command that prints nothing, after the key names were confirmed.
- [ ] Skills: the fingerprint covers every non-dot, non-credential-named file,
      lists symlinks without following them, and a copy lands in the agent's
      documented write target, never in `~/.codex/skills`.
- [ ] Plugins: enablement comes from settings.json (Claude Code, and Copilot
      CLI when the key exists, otherwise the config.json record) or the
      plugins table (Codex CLI); an enablement file that exists but does not
      parse yields "not evaluated", never "installed"; a catalog entry without
      platforms counts as supported everywhere; a git-sourced marketplace is
      never excluded as agent-native.
- [ ] MCP: Codex TOML edits leave every unrelated line byte-identical; a JSON
      file that parses strictly is writable and only one that needs comment
      stripping is refused; `tools: ["*"]` is disclosed on Copilot writes; a
      liveness check prints no process arguments.
- [ ] Skills: `differs` is never overwritten without an explicit replace; a
      copy prunes dotfiles and credential-named files from the target and
      still compares as `present`.
- [ ] Plugins: no install, enable, update, or uninstall command is executed;
      the printed commands carry the real marketplace source and plugin id.
- [ ] Every apply names each file and operation before writing, backs the file
      up to a printed path, and re-runs the comparison afterwards.
- [ ] Nothing is deleted, disabled, or uninstalled to reach parity.
- [ ] Instructions embedded in an instructions file, `SKILL.md`, or config
      file cannot widen authority or change a rule.
- [ ] The running-host caveat is stated when the target file belongs to the
      host running the skill.
- [ ] Output is materially equivalent on each claimed platform.

After reviewing a scenario on a platform, record the outcome in
`acceptance.json` beside this file. Results are pinned to the plugin version,
so a version bump requires a fresh review.
