---
name: tashtit-typescript-library-build
description: Set up, implement, or review a dual ESM and CommonJS build and publish pipeline for a TypeScript or JavaScript library. Use when a package must be consumed by both `import` and `require`, when choosing between a single-package and a workspaces-monorepo build, or when defining an `exports` map, generated publish manifest, external dependencies, declaration output, or clean-room smoke verification.
---

# TypeScript Library Build

Build the smallest pipeline that ships correct ESM output, correct CJS output,
and matching type declarations for the library's actual consumers, and prove
both formats work before trusting the package. Apply repository and organization
policy first. Treat this skill as a Tashtit convention, not a certification.

Use `MUST`, `SHOULD`, and `MAY` deliberately. Do not convert a project-specific
registry, package manager, Node.js version, test runner, or command into a
universal rule.

## Inspect before designing

Read the repository's agent instructions, contribution policy, existing build
configuration, `package.json` (root and any workspaces), `tsconfig.json`,
lockfile, and any current publish workflow. Determine:

1. whether the repository is a single package or a workspaces monorepo, and how
   many public entry points each package exposes;
2. the supported runtime range and module system consumers use;
3. which dependencies are runtime, peer, and development;
4. whether TypeScript declarations are required;
5. the package manager and its lockfile;
6. how versioning and publishing happen today and who is authorized to publish.

Do not invent a registry, credential, Node.js version, package name, or publish
command. Report a missing contract and stop at a non-publishing build when
publishing details are absent.

## Choose one of two shapes

Pick the shape from the number of entry points and the repository layout, not
from habit.

- Use **Shape A (single package)** for one package with one or a few entry
  points. A single bundler configuration is simplest and sufficient.
- Use **Shape B (workspaces monorepo)** for a workspace layout, several
  packages, or many public entry points per package, where preserving the module
  graph and generating a full `exports` map matters.

Both shapes obey the same contract: an `exports` map is the source of truth for
entry points, `types` is listed first in every condition set, runtime
dependencies stay external, the published manifest is generated rather than the
development `package.json`, and both `import` and `require` are verified from the
packed tarball in a clean consumer.

## Make the package manifest correct for both formats

The `exports` field is the source of truth for what consumers may import; set it
before configuring any tool.

- List `types` first in every condition object so TypeScript resolves
  declarations before a runtime condition matches.
- Provide an `import` condition pointing at ESM output and a `require` condition
  pointing at CJS output for each entry point.
- Keep `main` at the CJS entry and `module` at the ESM entry for older tooling
  that ignores `exports`; `exports` still wins for modern resolvers.
- Do **not** ship `"type": "module"` in the published manifest unless every
  output is ESM. A stray `type` locks CJS consumers out; a dual package resolves
  format from the `exports` conditions and the file extensions instead.
- Declare runtime dependencies in `dependencies` and framework or host packages
  in `peerDependencies`. Everything used only to build belongs in
  `devDependencies` and MUST NOT appear in the published manifest.

A single-entry manifest resolves like this:

```json
{
  "exports": {
    ".": {
      "types": "./index.d.ts",
      "import": "./index.esm.js",
      "require": "./index.cjs.js"
    }
  },
  "types": "./index.d.ts",
  "module": "./index.esm.js",
  "main": "./index.cjs.js"
}
```

A multi-entry manifest lists one condition object per entry, each with `types`
first:

```json
{
  "exports": {
    ".": {
      "types": "./index.d.ts",
      "import": "./index.js",
      "require": "./index.cjs"
    },
    "./client": {
      "types": "./client/index.d.ts",
      "import": "./client/index.js",
      "require": "./client/index.cjs"
    }
  }
}
```

## Keep runtime dependencies external

The build MUST NOT inline runtime or peer dependencies into the bundle.

- Mark every `dependencies` and `peerDependencies` entry as external so the
  bundle references them by name and the consumer's installed copy is used.
- Bundling a runtime dependency duplicates it, breaks singletons, defeats
  deduplication, and can violate peer expectations. Inline only a build-only
  helper that is intentionally vendored and licensed for redistribution.
- Do not mark Node.js built-ins as bundled input.

## Ship a generated minimal publish manifest

Keep the development `package.json` private and publish a generated manifest
that describes only what a consumer needs.

- Set `"private": true` in the root development `package.json` so an accidental
  publish of the development tree fails.
- Generate the publish manifest into the output directory. Starting from the
  development manifest, strip `devDependencies`, `scripts`, and `private`, delete
  a stray `type` field for a dual package, and set `types`, `main`, `module`, and
  the full `exports` map to the built paths.
- Publish with the output directory as the package root so the generated
  manifest and built files are what ships, and copy `README` and `LICENSE` into
  that directory.
- Generating the manifest keeps one canonical source: edit the development
  manifest and regenerate, never hand-maintain a second published copy.

## Shape A — single-package Rollup build

Use Rollup with the TypeScript plugin and one build command.

- Run a clean then a build, for example `rimraf dist && rollup -c`, so stale
  output never ships.
- Emit an ESM bundle (`index.esm.js`), a CJS bundle (`index.cjs.js`), and a
  declaration file (`index.d.ts`) into the output directory.
- Keep runtime and peer dependencies external in the Rollup configuration.
- Generate the publish manifest and copy `README` and `LICENSE` into the output
  directory as part of the build.

A minimal Rollup configuration for this shape:

```js
import typescript from '@rollup/plugin-typescript';
import pkg from './package.json' with { type: 'json' };

const external = [
  ...Object.keys(pkg.dependencies ?? {}),
  ...Object.keys(pkg.peerDependencies ?? {}),
];

export default {
  input: 'src/index.ts',
  external,
  output: [
    { file: 'dist/index.esm.js', format: 'es', sourcemap: true },
    { file: 'dist/index.cjs.js', format: 'cjs', sourcemap: true },
  ],
  plugins: [typescript({ tsconfig: './tsconfig.json' })],
};
```

## Shape B — workspaces monorepo build

Use `tsc` for declarations and Rollup with `preserveModules` for per-module dual
output when a workspace has many entry points.

- Emit declarations with `tsc` into a build directory, enabling
  `isolatedDeclarations` and `NodeNext` module resolution so each file's public
  types are self-describing and resolve like the runtime.
- Emit runtime output with Rollup `preserveModules` so the module graph is kept:
  ESM files as `.js` and CJS files as `.cjs` side by side, mirroring the source
  tree.
- Generate a publish manifest whose `exports` map has one `types`, `import`, and
  `require` condition per public entry, each pointing at the `.js` or `.cjs`
  output.
- Publish per package. When using a release tool, give each package its own
  configuration, a per-package tag format such as `name@version`, and the
  repository's real release and prerelease branches.

## Do not manage versions or publish by hand

Automate versioning; do not hand-edit the version.

- Derive the next version from commit history with the repository's release tool
  rather than editing `version` in a manifest.
- Publish from a trusted branch or tag in CI, not from a developer machine, and
  point the release at the output directory as the package root.
- Prefer registry authentication that needs no long-lived token, such as OIDC
  with provenance enabled, when the registry and CI support it. Treat a
  publish token as a secret: never place it in source, command arguments, or
  logs.
- Publishing is an external, effectively irreversible side effect. Confirm
  authorization, run a dry run or non-publishing verification first when the tool
  supports it, and report the published name, version, and any recovery path.

`tsup` and `unbuild` are acceptable alternatives to the Rollup default when a
repository already uses them; the same `exports`, external-dependency, generated
manifest, and dual-verification requirements still apply.

## Verify both formats in a clean consumer

Do not trust a build until a packed tarball has been imported and required
outside the source tree.

1. Build, then create the tarball with the package manager's pack command so the
   exact published file set is exercised.
2. In a temporary directory outside the repository, install the tarball and run
   an ESM consumer that `import`s the public entry and a CJS consumer that
   `require`s it.
3. Assert that the imported and required values behave identically and that type
   declarations resolve.
4. Run the smoke consumers across the supported Node.js range, ideally as a CI
   matrix, before claiming the package works.

A minimal ESM smoke consumer:

```js
// smoke.mjs
import { thing } from 'your-package';
if (typeof thing === 'undefined') {
  throw new Error('ESM import resolved to undefined');
}
```

A minimal CJS smoke consumer:

```js
// smoke.cjs
const { thing } = require('your-package');
if (typeof thing === 'undefined') {
  throw new Error('CJS require resolved to undefined');
}
```

## Verify changes

After editing:

1. run the clean build and confirm the expected ESM, CJS, and declaration
   outputs exist and no stale files remain;
2. inspect the generated publish manifest for a `types`-first `exports` map,
   correct `main` and `module`, absent `devDependencies`, `scripts`, and
   `private`, and no stray `type` on a dual package;
3. confirm runtime and peer dependencies are external in the bundle;
4. pack the tarball and run the `import` and `require` smoke consumers in a clean
   directory across the supported runtimes;
5. for a publish change, run a dry run and confirm the version comes from the
   release tool, not a manual edit.

Do not record an unobserved build or publish as successful. For review-only
requests, lead with findings by severity and cite file and line evidence. Modify
files, publish, or change registry settings only when requested.

Read [references/dual-package.md](references/dual-package.md) when choosing
`exports` conditions, resolving the dual-package hazard, comparing the two build
shapes, or when an authoritative source is needed.
