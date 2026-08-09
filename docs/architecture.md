# Architecture

## Design goals

Tashtit separates engineering knowledge from provider packaging. This keeps
behavior reviewable, reduces drift, and allows platforms to evolve without
forking the standards themselves.

The GitHub repository is `tashtit/marketplace`. Repository ownership and naming
are distribution details; the marketplace identifier remains `tashtit` so a
repository move does not silently rename installed marketplace references.

## Deduplication policy

Every piece of behavior and metadata MUST have one canonical source. Apply this
order:

1. **Share:** use one neutral or multi-platform standard file directly. Prefer
   established paths such as `skills/` and `.agents/` when all relevant hosts
   support them.
2. **Reference:** point provider manifests at the canonical file instead of
   copying its content.
3. **Link:** use a repository-relative link only when every supported checkout,
   archive, cache, and operating system preserves it and resolves it inside the
   plugin package.
4. **Generate:** when a schema or a host-mandated location cannot be shared,
   generate the smallest possible adapter from canonical metadata.

Hand-maintained copies are prohibited. A generated adapter MUST have a
deterministic sync command and a CI drift check. Links MUST NOT be absolute,
escape the repository, or depend on developer-machine paths.

### Why repository symlinks are not used

A Git symlink is not a portable packaging mechanism for a file a host must
parse. When a checkout sets `core.symlinks=false` — the default whenever the
filesystem or user cannot create symlinks, which is common on Windows — Git
materializes the entry as a regular file whose contents are the link target
path. A host then reads `../.claude-plugin/plugin.json` instead of JSON and the
plugin fails to load. `git archive` in tar and zip form does preserve the
symlink, so archive testing alone does not detect this.

Tier 3 is therefore unavailable for any file a provider parses, including
manifests and catalogs. Those use tier 4. Validation rejects a symlinked
manifest rather than trusting that every consumer can follow it.

## Layers

### Canonical payload

Each plugin lives at `plugins/<plugin-name>/`. Skills, references, scripts, and
assets in that directory define its distributed behavior. Content should follow
the portable Agent Skills conventions where practical.

### Provider adapters

Adapters describe the same payload to each host. They are added only when a
shared standard location cannot serve the platforms:

- Claude Code and GitHub Copilot: canonical `.claude-plugin/plugin.json`;
- Codex: `.codex-plugin/plugin.json`, generated from that canonical manifest.
  Codex accepts the same fields, but it only discovers the manifest at its own
  required path, so the file is duplicated by generation rather than shared;
- Cursor: an optional adapter once its contract is validated.

Adapters may express platform capabilities but must not silently change
normative behavior. A documented capability gap is preferable to an
inconsistent implementation.

### Catalog adapters

`.claude-plugin/marketplace.json` is both the canonical catalog and the
distribution file shared by Claude Code and GitHub Copilot. One additional
distribution artifact is required:

- `.agents/plugins/marketplace.json` is generated for Codex because its
  marketplace schema includes different source and policy fields.

Run `npm run sync` to regenerate every Codex artifact: the catalog above and each
plugin's `.codex-plugin/plugin.json`. `npm run validate` and CI fail if any of them
differs from the canonical source. Because JSON carries no comment syntax, these
files cannot carry an in-file generated marker; they are marked as generated here
and in `plugins/README.md`, and must never be hand-edited.

## Plugin shape

```text
plugins/example/
├── README.md
├── CHANGELOG.md
├── .claude-plugin/plugin.json
├── .codex-plugin/plugin.json
├── skills/
│   └── example/
│       ├── SKILL.md
│       ├── references/
│       └── scripts/
```

Only files required by a plugin should exist. MCP servers, hooks, commands, and
executables require additional threat modeling and test coverage.

### Progressive disclosure and context cost

A skill is loaded in layers, so structure it to spend context only when needed:

1. `name` and `description` are loaded for every installed skill on every turn.
   Keep them specific and short; they are the highest-cost, highest-leverage
   text a plugin owns.
2. The `SKILL.md` body loads only when the skill triggers. Keep the common path
   inline here.
3. `references/` and `scripts/` load only when the skill navigates to them.

Split content into a reference only when it is large and needed on a rare or
mutually exclusive path. A small reference that the skill reads on nearly every
run costs more than inlining it, because the extra read is another tool call and
its tokens on top of the reference body. Prefer a runnable `scripts/` file over
prose for deterministic work, and state explicitly whether the agent should read
a file or run it.

The same hierarchy applies inside a plugin: share `skills/`, references,
scripts, and assets directly. If plugin manifest schemas cannot share one file,
generate the narrower adapter and validate semantic equivalence.

### Repository quality assurance

Maintainer-only evaluation specifications, fixtures, and review checklists live
under `tests/plugins/<plugin-name>/`, outside the distributed plugin source.
Provider hosts do not consume these files. Repository automation validates their
structure; a scenario is not considered executed until a human or evaluation
runner records a result in `tests/plugins/<plugin-name>/acceptance.json`. That
record, not the scenario file, is what gates a maturity claim above
`experimental`, so an unreviewed plugin cannot advertise reviewed behavior.

## Trust boundaries

Plugin instructions are executable influence. Every design review must identify
which inputs are trusted, which tools can cause side effects, what data can
leave the machine, and how a user can inspect and recover from changes.

Remote content is untrusted by default. Secrets must not enter prompts, logs, or
fixtures. Network access and persistent writes must be explicit.

## Versioning

Plugin versions are independent. Catalog versions describe catalog schema or
release state and do not replace plugin versions. Portable behavior and all
provider adapters for a plugin ship together under one plugin version.
