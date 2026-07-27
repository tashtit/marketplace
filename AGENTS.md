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
     path preserves and safely resolves it;
  3. generate the provider file with a deterministic syncer.
- Never maintain hand-copied provider variants. Generated files must be marked
  by repository documentation, regenerated with `make sync`, and checked for
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
  marketplace. Do not hand-edit `.agents/plugins/marketplace.json`.
- Add or update acceptance scenarios for every behavioral change.
- Keep documentation concise, actionable, and free from vendor marketing copy.

## Validation

Run `make validate` and inspect the complete diff before requesting review.
Run `make sync` after changing the shared marketplace.
