# Host profile: Claude Code

Loaded **only** when the current host is Claude Code (`CLAUDECODE=1`). Do not read
the Copilot profile. Every host-specific detail the dynamic skills need is defined
below under a stable heading the skill refers to by name.

## Headless invocation

One headless session per arm. Substitute `<task>`, `<model>`, and `<out>`
(the arm's JSONL capture path):

```bash
claude -p "<task>" \
       --model <model> \
       --permission-mode bypassPermissions \
       --output-format stream-json \
       > <out>
```

- Omit `--model` to use the session default / auto.
- `<out>` is `runs/<arm>-<run-id>.jsonl`.

## Review-layer subprocess

Run the arm-blind code review as a headless `claude -p` subprocess **inside the
arm's worktree** so it inherits `CLAUDE.md` and the project's skills:

```bash
claude -p "<review instructions + the diff>" \
       --permission-mode bypassPermissions \
       --output-format stream-json
```

Never pass the arm label (or, for `compare-models`, the model name) to the
reviewer or judge.

## Telemetry parsing

Parse `runs/<arm>-<run-id>.jsonl` — Claude Code stream-json:

- Final `result` event: `total_cost_usd`, `usage.input_tokens`, `usage.output_tokens`,
  `usage.cache_read_input_tokens`, `usage.cache_creation_input_tokens`, `duration_ms`, `turns`, `session_id`.
- Tool profile: count `tool_use` events grouped by `name`.
- Tool errors: count `tool_result` events where `is_error` is `true`.

## Report metric rows

Substitute these host-specific rows into the skill's report table (in place of the
generic cost/token rows):

```text
tokens (in/out)   | ...k/...k               | ...k/...k
cost (USD)        | $...                    | $...
```

## Skill-invocation detection

Determine whether a given skill actually **fired** in an arm by scanning its
`runs/<arm>-<run-id>.jsonl` for a signal that names the skill under test (match on
the skill's `name` front-matter value, not its directory):

- A `tool_use` event with `name` == `Skill` whose `input.command` / `input.name`
  names the skill, **or**
- A `tool_use` `Read` of a path ending in that skill's `SKILL.md`.

Presence of either ⇒ `skill_fired = yes`; absence of both ⇒ `skill_fired = no`.

## Skill isolation

A skill reaches a session one of two ways. Classify the skill under test, then
isolate it with the matching mechanism — **never** by editing the shared
`$HOME/.claude/` in place (that corrupts other sessions and the parallel arm).

**1. Loose skill under a skills directory** (a `SKILL.md` committed in the repo at
`.claude/skills/`, `.github/skills/`, `src/skills/`, …). Its file is inside the
worktree, so isolate by **deleting the skill's file/directory** in the arm that must
lack it. Fully isolated; no shared state is touched.

**2. Plugin skill** (installed under `$HOME/.claude/plugins/` and enabled through an
`enabledPlugins` map). The files are shared by every worktree, so a worktree delete
does nothing. Instead **pin enablement per arm by writing the highest-precedence
settings file into the arm's worktree** — do not touch `$HOME`.

Claude merges settings from three scopes, `local` highest:

| Scope   | File                                 | Git-tracked     | Precedence |
|---------|--------------------------------------|-----------------|------------|
| user    | `$HOME/.claude/settings.json`        | no (shared)     | low        |
| project | `<repo>/.claude/settings.json`       | yes             | mid        |
| local   | `<repo>/.claude/settings.local.json` | not by default  | high       |

`enabledPlugins` is a `"<plugin>@<marketplace>": <bool>` map merged **per key**, so a
`local`-scope entry overrides whatever `user` or `project` scope set — `true` forces
the skill on, `false` forces it off. Isolate each arm by writing
`<repo>/.claude/settings.local.json` in the worktree:

```jsonc
// with arm
{ "enabledPlugins": { "<plugin>@<marketplace>": true } }
// without arm
{ "enabledPlugins": { "<plugin>@<marketplace>": false } }
```

The pin must stay out of the captured diff, or the arm-blind review layer sees
`enabledPlugins` set to `true` in one arm and `false` in the other and can infer the
arm label. **Do not assume the file is gitignored** — `.claude/settings.local.json`
is only ignored if the target repo happens to ignore it, and most do not. Instead
exclude it explicitly when staging the arm's result, per the **Commit the result**
step in the calling skill:

```bash
git add -A -- ':(exclude).claude/settings.local.json'
```

The file stays on disk and in effect for the session; it is simply never staged, so
it does not reach `git diff <base>` or inflate `files_changed`. The plugin files are
already present via the shared `$HOME/.claude/plugins/`, so no `HOME` copy is
needed — only enablement is pinned.

When writing `settings.local.json`, **merge-write** — do not replace the whole file.
Read any existing `.claude/settings.local.json` in the worktree, add or update only
the `enabledPlugins` key, and write it back. This preserves any other local settings
(e.g. `model`, `permissions`) that may already be present.

**Preconditions — stop rather than produce an invalid run if any fail:**

- The plugin's **files must be installed** on the machine. Enablement toggles a
  plugin that exists; it cannot conjure missing files. If not installed, the `with`
  arm cannot have it — install it first or stop.
- A **managed/enterprise scope** can force-enable above `local`; if one pins the
  plugin, `local: false` cannot override it — detect and stop.
- **`enabledPlugins` must exist in a parent scope** (`user` `$HOME/.claude/settings.json`
  or `project` `<repo>/.claude/settings.json`) before writing a `local`-scope override.
  If the key is absent from both parent scopes, a `local`-scope `enabledPlugins` is
  silently ignored (issue #27247) — the `with` arm's `true` pin won't take effect and
  the run will be inconclusive. Detect this case: if `enabledPlugins` is absent from
  both parent scopes, stop and tell the user to add the plugin's key to their user or
  project settings first.

Always verify isolation with **Skill-invocation detection**: the arm that must lack the
skill must show `skill_fired = no` and the arm that must have it `skill_fired = yes`.
If either is wrong, the pin did not take effect — treat the run as invalid.

## Reviewer sub-agent

The static skills use the bundled `skill-reviewer` agent (`agents/skill-reviewer.md`);
it is host-agnostic and ships with this plugin.
