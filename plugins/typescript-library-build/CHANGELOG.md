# Changelog

## 0.2.0 - 2026-08-09

### Changed

- **Breaking:** renamed skill `typescript-library-build` to `tashtit-typescript-library-build`.
- Every Tashtit skill name now carries the `tashtit-` provenance prefix.
  Hosts flatten installed skills into one namespace and GitHub Copilot
  displays only the bare skill name, so unprefixed names can collide with
  or be indistinguishable from skills shipped by other marketplaces. See
  the skill naming policy in `docs/compatibility.md`.

## 0.1.0 - 2026-08-04

- Added opinionated dual ESM and CommonJS TypeScript and JavaScript library
  build and publish guidance.
- Added the single-package Rollup shape and the workspaces monorepo `tsc` plus
  Rollup `preserveModules` shape, with a shared decision on when to use each.
- Added the `exports`-map-first packaging model, generated minimal publish
  manifest, external runtime dependencies, and clean-room `import` and
  `require` smoke verification.
- Added positive, failure, and unsafe acceptance scenarios.
