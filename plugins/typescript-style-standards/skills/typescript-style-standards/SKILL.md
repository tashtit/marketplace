---
name: typescript-style-standards
description: Establish, apply, or review TypeScript and JavaScript code style conventions - type aliases versus interfaces, readonly properties and immutability, function parameter design and options objects, file and export naming, and type-safety hygiene. Use when writing new TypeScript modules, choosing between type and interface, deciding parameter shape or an options object, naming files, configuring or reviewing lint style rules, or judging whether code should follow an existing repository convention or this baseline. Defers to established repository conventions and lint configuration wherever they exist.
---

# TypeScript Style Standards

Apply a consistent TypeScript and JavaScript style without fighting the
repository you are working in. These conventions are defaults for code with no
established style, not a mandate to restyle existing code.

Use `MUST`, `SHOULD`, and `MAY` to distinguish requirements, strong defaults,
and optional practices.

## Precedence: local convention wins

Existing repository convention overrides every rule in this skill.

1. **Detect before dictating.** Before writing code, read the local style
   signals: lint configuration (ESLint, Biome, oxlint), `tsconfig` strictness,
   formatter settings, and the actual style of the files being touched -
   naming, `type` versus `interface`, export style, parameter shape.
2. **Lint configuration is the authoritative expression of local style.** Never
   contradict, disable, or inline-suppress a style rule to land a change.
   Propose style changes as lint-configuration changes, not as ad-hoc
   divergence in code.
3. **Consistency has a scope order.** Match the file being edited first, then
   its module or package, then the repository. A file that consistently uses
   `interface` gets `interface` in the diff.
4. **This skill's defaults apply in full only where the repository is
   silent:** new files, new packages, greenfield repositories, or areas with no
   discernible convention.
5. **A style migration is its own change.** Never mix restyling into a feature
   or bug-fix diff. Propose it separately, driven by a lint rule so the
   convention is enforced rather than aspirational.
6. **Escape hatch.** When local convention is actively harmful (for example,
   pervasive `any`), follow it locally, do not silently "fix" it, and surface
   the observation with a separate remediation suggestion.

Ecosystem convention is local convention. React component files in
`PascalCase.tsx` named after their exported component are the established
custom of that ecosystem; detection produces the right answer without a
special case.

## Type definitions

- SHOULD define object shapes with `type` aliases rather than `interface`.
- `interface` MAY be used where it is the better tool:
  - declaration merging, including augmenting third-party or global types;
  - class-implementation hierarchies where `interface extends` produces
    clearer error messages.
- MUST NOT mix `type` and `interface` for peer declarations in the same file
  without one of the reasons above.
- SHOULD prefer union types or `as const` object maps over `enum`.

## Immutability

- SHOULD mark type properties `readonly` unless mutation is part of the
  contract.
- SHOULD type array and object parameters the function does not mutate as
  `readonly T[]` / `Readonly<T>`.
- MUST use `const` for bindings that are never reassigned; MUST NOT use `var`.
- SHOULD treat function parameters as immutable; return new values instead of
  mutating inputs unless mutation is the documented purpose.

## Function parameters

- A function SHOULD take at most 3 parameters.
- Beyond that, keep 1-2 essential positional parameters and move the rest into
  a single trailing options object with a named, `readonly`-property type.
- Optional and rarely-used parameters belong in the options object regardless
  of count.
- A boolean parameter MUST be a named option, never positional:
  `sync(url, { force: true })`, not `sync(url, true)`.
- When refactoring an exported function to an options object, update all call
  sites in the same change and state the compatibility impact if the function
  is part of a published API.

## Files and exports

- Pure TypeScript and JavaScript files MUST use `kebab-case` names
  (`parse-config.ts`, not `parseConfig.ts` or `ParseConfig.ts`). Mixed-case
  filenames invite case-sensitivity defects between macOS and Linux
  checkouts.
- Files whose primary export is an ecosystem-cased artifact follow that
  ecosystem: a React component file is `PascalCase.tsx` matching the
  component; hooks follow the repository's existing hook-file convention.
- Name the file after its primary export's role; one primary concern per
  file.
- SHOULD use named exports. Default exports MAY be used only where a
  framework requires them (for example route files or `React.lazy` targets).

## Type-safety hygiene

- MUST NOT introduce `any`, `@ts-ignore`, `@ts-expect-error` without a
  reason, or `@ts-nocheck` to silence a type error. Fix the type, or narrow
  from `unknown` with validation at the trust boundary.
- `as` casts belong at trust boundaries next to validation, not scattered
  through application logic.
- SHOULD use `import type { ... }` for type-only imports.
- SHOULD pick one nullish convention per repository - typically prefer
  `undefined` and reserve `null` for external contracts that require it.
- New TypeScript configuration MUST enable `strict`; SHOULD enable
  `noUncheckedIndexedAccess`. Never weaken existing strictness to land a
  change.

## Enforce with lint rules, not prose

Wherever a rule here is machine-checkable, encode it in the repository's lint
configuration and let the tool carry it; reserve review comments for the
judgment calls (when to cut over to an options object, whether an `interface`
exception applies). See
[references/lint-rules.md](references/lint-rules.md) for the mapping from
each convention to established ESLint rules.

## Review guidance

When reviewing, report findings ordered by severity and cite the file and
line. Distinguish three classes:

1. violations of the repository's own convention or lint configuration;
2. type-safety regressions (`any`, suppressions, weakened strictness);
3. divergence from this baseline in convention-free code.

Do not expand a review into edits, and do not flag consistent local style as
a defect merely because this skill's default differs.
