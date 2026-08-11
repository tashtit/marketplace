# Lint-rule mapping

Encode machine-checkable conventions in lint configuration rather than prose.
The mapping below uses ESLint with `typescript-eslint` and, where noted,
`eslint-plugin-unicorn` and `eslint-plugin-functional`. Biome and oxlint carry
equivalents for most of these; map by intent, not by rule name.

Adding a lint plugin is a dependency decision - route it through the
repository's dependency-intake policy rather than installing it as a side
effect of a style change.

| Convention | Rule |
| --- | --- |
| Prefer `type` over `interface` | `@typescript-eslint/consistent-type-definitions: ["error", "type"]` |
| `readonly` class members where never reassigned | `@typescript-eslint/prefer-readonly` |
| `readonly` parameter types for unmutated inputs | `functional/prefer-immutable-types` (or `@typescript-eslint/prefer-readonly-parameter-types`, which is strict and often too noisy - evaluate before enabling) |
| Max 3 parameters | `max-params: ["error", 3]` |
| No positional booleans | `no-boolean-param` intent via `@typescript-eslint/no-unnecessary-boolean-literal-compare` is not equivalent; enforce in review or with `functional`-style custom rules |
| `kebab-case` filenames with ecosystem exceptions | `unicorn/filename-case: ["error", { "cases": { "kebabCase": true, "pascalCase": true } }]` scoped so `pascalCase` applies only to component globs |
| Named exports | `import/no-default-export`, with per-glob overrides for framework-required defaults |
| No `any` | `@typescript-eslint/no-explicit-any` |
| No unexplained suppressions | `@typescript-eslint/ban-ts-comment` (default requires description for `@ts-expect-error`) |
| Type-only imports | `@typescript-eslint/consistent-type-imports` |
| Unions/`as const` over `enum` | `no-restricted-syntax` targeting `TSEnumDeclaration` |
| `const` over `let`, no `var` | `prefer-const`, `no-var` |
| Nullish convention | `unicorn/no-null` when the repository standardizes on `undefined` |

Compiler-enforced items belong in `tsconfig`, not ESLint: `strict: true`,
`noUncheckedIndexedAccess: true`.
