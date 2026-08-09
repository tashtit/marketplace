# Changelog

## 0.2.0 - 2026-08-09

### Changed

- **Breaking:** renamed skill `architecture-diagrams` to `tashtit-architecture-diagrams`.
- Every Tashtit skill name now carries the `tashtit-` provenance prefix.
  Hosts flatten installed skills into one namespace and GitHub Copilot
  displays only the bare skill name, so unprefixed names can collide with
  or be indistinguishable from skills shipped by other marketplaces. See
  the skill naming policy in `docs/compatibility.md`.

## 0.1.0 - 2026-08-04

- Added a C4 System Context (C1) contract: single system boundary, actors,
  external systems, and directional, labeled interactions aimed at a stated
  audience.
- Added a C4 Container (C2) contract: name, type, responsibilities, technology,
  and labeled runtime relationships for each deployable unit, with people and
  external dependencies shown.
- Added a consistent visual-vocabulary and level-discipline requirement so C1
  and C2 stay at their intended abstraction.
- Added the C4 model reference and maintainer evaluation scenarios.
