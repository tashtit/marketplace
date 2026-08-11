# Changelog

## 0.1.0 - 2026-08-12

- Added convention-first precedence rules: local convention and lint
  configuration override the skill's defaults, and style migrations are
  separate lint-driven changes.
- Added type-definition guidance preferring `type` aliases with explicit
  `interface` exceptions.
- Added immutability defaults: `readonly` properties and unmutated
  `readonly` parameter types.
- Added parameter-design rules: at most 3 parameters, trailing options
  objects, and named boolean options.
- Added file and export naming: `kebab-case` for pure TS/JS with
  ecosystem-cased exceptions, and named exports by default.
- Added type-safety hygiene and a lint-rule mapping reference.
