# Agent Instructions

These instructions apply to the entire repository.

## Purpose

Tashtit is an opinionated, production-ready, enterprise-minded plugin
marketplace for AI coding agents. Prefer a small, verifiable standard over broad
but shallow guidance.

## Working rules

- Preserve one canonical source for every behavior and metadata field.
- Reuse neutral or multi-platform standard paths such as `skills/` and
  `.agents/` whenever all target platforms support them.
- Follow this fallback order when a shared path is impossible:
  1. reference the canonical file directly;
  2. use a repository-relative link when every target platform and packaging
     path preserves and safely resolves it. Never use a repository symlink for a
     file the provider parses: a checkout with `core.symlinks=false` replaces it
     with the link target as plain text;
  3. generate the provider file with a deterministic syncer.
- Never maintain hand-copied provider variants. Generated files must be marked
  by repository documentation, regenerated with `npm run sync`, and checked for
  drift in CI.
- Provider adapters must not fork the underlying guidance.
- Treat security, privacy, destructive actions, and external side effects as
  first-class design concerns.
- Use normative terms (`MUST`, `SHOULD`, `MAY`) deliberately and define
  exceptions.
- Cite authoritative, current sources for externally defined standards. Label
  project preferences as Tashtit conventions.
- Never include real secrets, credentials, private endpoints, or customer data
  in examples or fixtures.
- Do not claim a plugin is stable or production-ready until it satisfies
  `docs/quality-standard.md`.
- Edit `.claude-plugin/marketplace.json`, which is the shared canonical
  marketplace, and each plugin's `.claude-plugin/plugin.json`. Do not hand-edit
  the generated `.agents/plugins/marketplace.json` or any
  `.codex-plugin/plugin.json`.
- Keep the plugin tables in `README.md` and `plugins/README.md` in step with the
  canonical marketplace; `npm run validate` fails on drift.
- Add or update acceptance scenarios for every behavioral change.
- Never record a result in `tests/plugins/<name>/acceptance.json` that was not
  actually observed, and never raise a plugin's maturity to satisfy the
  validator. The record exists to make an unreviewed claim impossible.
- Keep documentation concise, actionable, and free from vendor marketing copy.

## Validation

Run `npm run validate` and `npm test`, then inspect the complete diff before
requesting review. Run `npm run sync` after changing the canonical marketplace or
any plugin manifest. When changing a script in `scripts/`, extend the unit
tests in `tests/scripts/` so the changed check is covered.
