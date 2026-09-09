---
name: parity-instructions
description: Compare the agent-parity managed instructions block across the installed AI coding agents — global ~/.claude/CLAUDE.md, ~/.codex/AGENTS.md, and ~/.copilot/copilot-instructions.md, plus CLAUDE.md and AGENTS.md at a repository root — and report each file as in sync, out of date, or not applied against one baseline. Use when asked to sync, mirror, copy, or push shared instructions between Claude Code, Codex CLI, and Copilot CLI, or whether their CLAUDE.md and AGENTS.md managed blocks match. Reads and writes only the text between the markers; everything outside them is never read into the report or changed. Writes only on explicit request, and a named source is required whenever the blocks disagree. Not for authoring instructions or reviewing what they say.
---

# Compare instructions

Sub-skill of `agent-parity`. Agent detection and config-home resolution, the
safety contract, the backup step, scoring, and the report frame are defined in
[the router](../agent-parity/SKILL.md); read it first when this skill was
invoked directly.

Every agent reads free-form Markdown instructions from its own file. One
baseline per scope lives inside managed markers in each of those files, so the
agents can share text without sharing the file. Text outside the markers is
that agent's own: it is never compared, summarized, printed, or changed.

## Targets

| Scope | Agent(s) | File |
| --- | --- | --- |
| Global | Claude Code | `<claude home>/CLAUDE.md` (default `~/.claude/CLAUDE.md`) |
| Global | Codex CLI | `<codex home>/AGENTS.md` (default `~/.codex/AGENTS.md`) |
| Global | Copilot CLI | `~/.copilot/copilot-instructions.md` |
| Repository | Claude Code | `<root>/CLAUDE.md` and `<root>/.claude/CLAUDE.md`; Claude Code loads and concatenates both when both exist |
| Repository | Codex CLI and Copilot CLI | `<root>/AGENTS.md` (both read it natively) |

A file is a target only when its agent is installed. Repository targets are
evaluated only when the working directory is inside a Git repository.
`<root>/.github/copilot-instructions.md` and
`<root>/.github/instructions/*.instructions.md` are Copilot-only repository
files: list them as present or absent on the report's last line, but never
manage them.

When both Claude repository files exist, read both: the one holding a managed
block is the managed target, and a block in each is reported with the warning
`duplicate: two Claude files`, because Claude Code then loads the shared text
twice. Apply writes only to the file that already holds the block, or to
`<root>/CLAUDE.md` when neither does.

Each target file and agent that reads it is one pair for scoring, so a
repository `AGENTS.md` contributes two pairs when both Codex and Copilot are
installed, while the two Claude repository files together count as one pair.

## Managed block

```markdown
<!-- agent-parity:shared:start -->
The shared baseline text.
<!-- agent-parity:shared:end -->
```

The legacy markers `<!-- cockpit:shared:start -->` and
`<!-- cockpit:shared:end -->` denote the same block and are written by
Cockpit (<https://github.com/tashtit/cockpit>), which manages these same files
and is still maintained. Read either style, in any combination. Write the
canonical pair for a block this skill creates, and keep the style a file
already uses when replacing an existing block. Claude Code strips block-level
HTML comments before loading a file, so the markers cost it nothing; Codex and
Copilot see them as inert comments.

A marker counts only when it is the entire content of its line and is not
inside a fenced code block. To extract a block: find the first start marker,
then the first end marker after it. The block is the text between them with
one leading newline and any trailing whitespace removed. Compare blocks after
trimming leading and trailing whitespace and normalizing CRLF to LF. A start
marker with no end marker after it makes the file `not evaluated`; report the
path and line number. Only the first block is managed; report any later start
marker as a warning.

## Baseline

Resolve the baseline per scope in this order and state which rule applied:

1. The user named a source agent or file: its block is the baseline. A named
   target that has no block is not a valid source: never fall back to its
   whole content, because that would read the agent's own text into the
   report; ask the user to wrap the shared text in markers or to supply the
   text. A named target whose block is unterminated is not a valid source
   either, and a named `(by import)` or `(linked)` `CLAUDE.md` redirects to
   the file it imports. A named file outside the targets contributes its block, or its whole
   content when it has no markers.
2. Every target that has a block agrees: that text is the baseline, and the
   files it came from are named.
3. The blocks disagree: take the block from the most recently modified target
   (ties broken in the order Claude Code, Codex CLI, Copilot CLI; a repository
   file's time reflects its checkout) as a **provisional** baseline for the
   report only, label it as such with the file it came from, show a unified
   diff (at most 40 lines per file) for each other block, and say that
   applying requires a named source. A provisional baseline is never applied.
4. No target in the scope has a block: the scope has not adopted a shared
   baseline. Every target is `not adopted`, outside the score, and the report
   says that applying requires the user to name a source file or supply the
   text.

## Status per target

| Status | Meaning | Counts as |
| --- | --- | --- |
| `in sync` | Block equals the baseline | parity |
| `<status> (by import)` | A Claude `CLAUDE.md` target has no block but imports another target of the same scope (see below); it takes that target's status and is never written | as the base status |
| `<status> (linked)` | Repository `CLAUDE.md` is a symlink to `AGENTS.md`; it takes the status of `AGENTS.md` and is never written | as the base status |
| `out of date` | Block exists and differs from the baseline | gap |
| `not applied` | File exists without a managed block | gap |
| `not applied (missing)` | File does not exist | gap |
| `not adopted` | No target in the scope has a block (rule 4) | neither |
| `not evaluated` | Unterminated block, or the file could not be read | neither |

Claude Code expands `@path` imports found anywhere in a file outside code
spans, fenced code blocks, and block-level HTML comments, resolving a relative
path against the importing file's directory. An import counts when the token
is preceded by the start of the line or whitespace and resolves to another
target of the same scope: `@AGENTS.md` or `@./AGENTS.md` in `<root>/CLAUDE.md`,
`@../AGENTS.md` in `<root>/.claude/CLAUDE.md`, or `@~/.codex/AGENTS.md` (or the
resolved `<codex home>` path) in the global `CLAUDE.md`. The importing file
takes that target's status `(by import)` and is never written. When the
imported file is missing, render the status as `not applied (by import;
AGENTS.md missing)`. A `CLAUDE.md` that has both a block and such an import is
compared by its block and carries the warning `duplicate: block and import`,
because Claude then loads the text twice.

## Report

```text
Baseline: <rule 1-4> (<source path or "none">; provisional under rule 3)

| Scope | File | Agent(s) | Status | Detail |
| --- | --- | --- | --- | --- |
| global | ~/.codex/AGENTS.md | Codex CLI | out of date | +3/-1 lines vs baseline; legacy markers |
| global | ~/.copilot/copilot-instructions.md | Copilot CLI | not applied | no managed block |
| global | ~/.claude/CLAUDE.md | Claude Code | in sync | |
| repo | AGENTS.md | Codex CLI, Copilot CLI | in sync | |
| repo | CLAUDE.md | Claude Code | in sync (by import) | imports AGENTS.md |

Copilot-only (not managed): .github/copilot-instructions.md present
```

The detail column carries line counts, marker style, and warnings. It never
quotes text from outside the block. If the baseline contains Claude-style
`@path` imports, warn that Codex and Copilot do not expand them.

## Apply on request

Preconditions: the user asked to apply, named the targets (an agent, a file,
or "everywhere"), and the baseline came from rule 1 or rule 2. Under rule 3 or rule 4
ask for a source and do not write.

| Status | Operation |
| --- | --- |
| `out of date` | replace block |
| `not applied` | append block |
| `not applied (missing)` | create file |
| `not evaluated` (unterminated block) | repair block, offered under "Not scored" and applied only when the user names the file |
| `<status> (by import)` or `<status> (linked)` | skip; the operation lands on the imported file, and the plan names every agent that reads it |
| `in sync` | none; legacy markers are left as they are |

State the plan first — one line per file with its operation — then write,
after the backup step the router defines. Write by replacing the exact span
described below, emitting the block with the file's existing line ending, so
every byte outside the span is unchanged.

- **Replace block.** The file has a start and end marker (canonical or
  legacy): replace from the start marker through the end marker, inclusive,
  with a block in the marker style the file already uses. Renaming legacy
  markers to the canonical pair happens only when the user asks for it, and
  the plan then says that Cockpit will report the file as unmanaged and append
  a second copy of the baseline on its next apply.
- **Repair block.** The file has a start marker with no end marker: replace
  the lone start marker with the full canonical block and keep everything that
  followed it, which then remains as the agent's own unmanaged text; say so in
  the plan. Never append a second block, which a later replace would treat as
  one span and swallow the text between.
- **Append block.** The file exists without markers: ensure the file ends with
  a newline, then append one blank line and the canonical block ending with a
  newline. An empty file receives only the block.
- **Create file.** The file does not exist: create it containing only the
  block, at `<root>/CLAUDE.md` for the Claude repository target. Never create
  a directory; every target's parent already exists when its agent is
  installed or the repository root was found.
- **Skip.** A `CLAUDE.md` whose status carries `(by import)` or `(linked)` is
  never given a block; `AGENTS.md` carries it. The Copilot-only repository
  files are never written.

Never rewrite, reformat, or reorder text outside the block, and never remove a
block: switching an agent off the shared baseline is the user's manual edit,
not a fix this skill applies.

After writing, re-run the comparison and show the new statuses. Repository
files show in `git status`; whether to commit them is the user's decision.
