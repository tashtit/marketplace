# Changelog

## 0.1.0 - 2026-08-04

- Added opinionated dual ESM and CommonJS TypeScript and JavaScript library
  build and publish guidance.
- Added the single-package Rollup shape and the workspaces monorepo `tsc` plus
  Rollup `preserveModules` shape, with a shared decision on when to use each.
- Added the `exports`-map-first packaging model, generated minimal publish
  manifest, external runtime dependencies, and clean-room `import` and
  `require` smoke verification.
- Added positive, failure, and unsafe acceptance scenarios.
