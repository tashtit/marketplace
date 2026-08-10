# Host profile: GitHub Copilot CLI

Loaded **only** when the current host is Copilot CLI (`COPILOT_CLI=1`). Do not read
the Claude profile. Every host-specific detail the dynamic skills need is defined
below under a stable heading the skill refers to by name.

## Headless invocation

One headless session per arm. Substitute `<task>`, `<model>`, and `<out>`
(the arm's JSONL capture path):

```bash
copilot -p "<task>" \
        --model <model> \
        --allow-all-tools \
        --no-ask-user \
        --output-format json \
        --log-level none \
        > <out>
```

- Omit `--model` to use the session default / auto.
- `<out>` is `runs/<arm>-<run-id>.jsonl`.

## Review-layer subprocess

Run the arm-blind code review as a headless `copilot -p` subprocess **inside the
arm's worktree** so it inherits `AGENTS.md` / `.github/copilot-instructions.md`
and the project's skills:

```bash
copilot -p "<review instructions + the diff>" \
        --agent code-review \
        --allow-all-tools \
        --no-ask-user \
        --output-format json \
        --log-level none
```

Never pass the arm label (or, for `compare-models`, the model name) to the
reviewer or judge.

## Telemetry parsing

Parse `runs/<arm>-<run-id>.jsonl` — Copilot CLI JSONL, one JSON object per line,
discriminated by `type`:

- `result` event: `sessionId`, `usage.sessionDurationMs`, `usage.totalApiDurationMs`,
  `usage.premiumRequests`, `usage.codeChanges.filesModified` (array) / `linesAdded` / `linesRemoved`.
- Output tokens: sum `data.outputTokens` across `assistant.message` events (input tokens are NOT emitted).
- AI-unit cost: the last `session.usage_checkpoint` event's `data.totalNanoAiu` (÷ 1e9 = AIU) and `data.totalPremiumRequests`.
- Turns: count `assistant.turn_start` events.
- Tool profile: count `tool.execution_start` events grouped by `data.toolName`.
- Tool errors: count `tool.execution_complete` events where `data.success` is `false`.

> Copilot CLI does not emit input-token counts or a USD cost in JSONL. Report cost
> in premium requests / AI units (nano AIU), and report output tokens only.

## Report metric rows

Substitute these host-specific rows into the skill's report table (in place of the
generic cost/token rows):

```text
output_tokens     | ...k                    | ...k
premium_reqs      | ...                     | ...
ai_units (AIU)    | ...                     | ...
```

`ai_units (AIU)` is per-model-priced — the relevant cost dimension for `compare-models`.

## Skill-invocation detection

Determine whether a given skill actually **fired** in an arm by scanning its
`runs/<arm>-<run-id>.jsonl` for a signal that names the skill under test (match on
the skill's `name` front-matter value, not its directory):

- A `tool.execution_start` event for the skill-invocation tool (`data.toolName` is
  the `skill` tool) whose `data.arguments` / `data.input` names the skill, **or**
- A `tool.execution_start` for a file read whose path ends in that skill's
  `SKILL.md`, **or**
- Any event whose payload otherwise references the skill's `name`.

Presence of any of these ⇒ `skill_fired = yes`; absence of all ⇒ `skill_fired = no`.

## Skill isolation

A skill reaches a session one of two ways. Classify the skill under test, then
isolate it with the matching mechanism — **never** by editing the shared
`$HOME/.copilot/` in place (that corrupts other sessions and the parallel arm).

**1. Loose skill under a skills directory** (a `SKILL.md` committed in the repo at
`.github/skills/`, `.claude/skills/`, `src/skills/`, … or pointed to by
`COPILOT_SKILLS_DIR`). Its file is inside the worktree, so isolate by **deleting the
skill's file/directory** in the arm that must lack it. Fully isolated; no shared
state is touched.

**2. Plugin skill** (installed under `$HOME/.copilot/installed-plugins/<marketplace>/<plugin>/`
and enabled through an `enabledPlugins` map). The files are shared by every worktree,
so a worktree delete does nothing. Instead **pin enablement per arm by writing the
highest-precedence settings file into the arm's worktree** — do not touch `$HOME`.

Copilot merges settings from three scopes, `local` highest:

| Scope | File                                         | Git-tracked     | Precedence |
|-------|----------------------------------------------|-----------------|------------|
| user  | `$HOME/.copilot/settings.json`               | no (shared)     | low        |
| repo  | `<repo>/.github/copilot/settings.json`       | yes             | mid        |
| local | `<repo>/.github/copilot/settings.local.json` | not by default  | high       |

`enabledPlugins` is a `"<plugin>@<marketplace>": <bool>` map merged **per key**
(`{...lower, ...higher}`), so a `local`-scope entry deterministically overrides
whatever `user` or `repo` scope set — `true` forces the skill on, `false` forces it
off. Isolate each arm by writing `<repo>/.github/copilot/settings.local.json` in the
worktree:

```jsonc
// with arm
{ "enabledPlugins": { "<plugin>@<marketplace>": true } }
// without arm
{ "enabledPlugins": { "<plugin>@<marketplace>": false } }
```

The pin must stay out of the captured diff, or the arm-blind review layer sees
`enabledPlugins` set to `true` in one arm and `false` in the other and can infer the
arm label. **Do not assume the file is gitignored** —
`.github/copilot/settings.local.json` is only ignored if the target repo happens to
ignore it, and most do not. Instead exclude it explicitly when staging the arm's
result, per the **Commit the result** step in the calling skill:

```bash
git add -A -- ':(exclude).github/copilot/settings.local.json'
```

The file stays on disk and in effect for the session; it is simply never staged, so
it does not reach `git diff <base>` or inflate `files_changed`. The plugin files are
already present via the shared `$HOME/.copilot/installed-plugins/`, so no `HOME` copy
is needed — only enablement is pinned.

**Preconditions — stop rather than produce an invalid run if any fail:**

- The plugin's **files must be installed** on the machine. Enablement toggles a
  plugin that exists; it cannot conjure missing files. If the plugin is not
  installed, the `with` arm cannot have it — install it first or stop.
- A **managed/enterprise scope** can force-enable above `local`; if one pins the
  plugin, `local: false` cannot override it — detect and stop.
- Keep the inherited `extraKnownMarketplaces` (from `user` scope) so the enable
  resolves; only add `enabledPlugins` at `local` scope, never replace the whole file.

Always verify isolation with **Skill-invocation detection**: the arm that must lack the
skill must show `skill_fired = no` and the arm that must have it `skill_fired = yes`.
If either is wrong, the pin did not take effect — treat the run as invalid.

## Reviewer sub-agent

The static skills use the bundled `skill-reviewer` agent (`agents/skill-reviewer.md`);
it is host-agnostic and ships with this plugin.
