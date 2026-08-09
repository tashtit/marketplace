# Dual-package build reference

Use this reference for externally defined behavior and detailed build decisions.
The normative defaults in `SKILL.md` are Tashtit conventions unless this file
identifies a Node.js, TypeScript, or tool requirement.

## Contents

- [Source basis](#source-basis)
- [Conditional exports and resolution order](#conditional-exports-and-resolution-order)
- [The dual-package hazard](#the-dual-package-hazard)
- [Choosing between the two shapes](#choosing-between-the-two-shapes)
- [Generated publish manifest](#generated-publish-manifest)
- [External dependencies](#external-dependencies)
- [Provenance and automated publishing](#provenance-and-automated-publishing)
- [Build review checklist](#build-review-checklist)

## Source basis

Use current documentation when tool or runtime behavior may have changed:

- [Node.js: package entry points and conditional exports](https://nodejs.org/api/packages.html#conditional-exports):
  `exports`, the `import` and `require` conditions, and resolution order.
- [Node.js: determining module system](https://nodejs.org/api/packages.html#determining-module-system):
  how `type` and file extensions select ESM or CommonJS.
- [Node.js: dual CommonJS/ES module packages](https://nodejs.org/api/packages.html#dual-commonjs-es-module-packages):
  the dual-package hazard and mitigation.
- [TypeScript: `moduleResolution` and package resolution](https://www.typescriptlang.org/docs/handbook/modules/reference.html#packagejson-exports):
  how TypeScript reads the `types` condition and why it must be listed first.
- [TypeScript: `isolatedDeclarations`](https://www.typescriptlang.org/tsconfig/#isolatedDeclarations):
  per-file declaration emission constraints.
- [Rollup: `output.preserveModules`](https://rollupjs.org/configuration-options/#output-preservemodules)
  and [`external`](https://rollupjs.org/configuration-options/#external):
  per-module output and excluding dependencies from the bundle.
- [npm: `package.json` fields](https://docs.npmjs.com/cli/v10/configuring-npm/package-json):
  `exports`, `main`, `module`, `types`, `private`, `dependencies`, and
  `peerDependencies`.
- [npm: provenance and OIDC publishing](https://docs.npmjs.com/generating-provenance-statements):
  trusted publishing without a long-lived token.

The two build shapes were distilled from working single-package and
workspaces-monorepo repositories. Their specific registry, package names,
Node.js versions, task runners, and organization commands are intentionally not
part of the portable standard.

## Conditional exports and resolution order

Node.js matches conditions in the order they appear in the object. A resolver
uses the first condition it supports, so ordering encodes intent. TypeScript
reads the `types` condition and must find it before a runtime condition matches;
therefore `types` is listed first in every condition set.

`import` matches an ESM context and `require` matches a CommonJS context. Point
`import` at ESM output and `require` at CJS output for each entry. When present,
`exports` fully controls which paths are importable; paths not listed are not
accessible even if they exist on disk. `main` and `module` remain only for older
tools that predate `exports`.

Do not add `"type": "module"` to a dual package's published manifest. With
`type` set to `module`, every `.js` file is treated as ESM and CommonJS
consumers can no longer load the package through the `require` condition unless
those files use the `.cjs` extension. A dual package selects format from the
`exports` conditions and the emitted extensions instead, so omitting `type`
keeps both consumers working.

## The dual-package hazard

Node.js documents that when both an ESM and a CommonJS copy of the same package
are loaded in one process, they are distinct module instances with separate
internal state. Code that relies on `instanceof`, a shared singleton, or module
level mutable state can break when one dependent loads the ESM copy and another
loads the CJS copy.

Mitigate by keeping shared state out of the dual-loaded module, or by having one
format be a thin wrapper that re-exports the other so a single implementation
holds the state. Keeping runtime dependencies external also avoids multiplying
the hazard across bundled copies. Verifying both `import` and `require` in a
clean consumer surfaces resolution mistakes that create an unintended second
instance.

## Choosing between the two shapes

Shape A, a single Rollup configuration emitting one ESM bundle, one CJS bundle,
and one declaration file, is enough for one package with one or a few entry
points. It is the least machinery and the easiest to reason about.

Shape B uses `tsc` for declarations and Rollup `preserveModules` for per-module
`.js` and `.cjs` output. Preserving modules keeps the import graph, which
matters when a package has many entry points, when consumers deep-import
subpaths, or when a monorepo publishes several packages that must each carry a
full `exports` map. It costs more configuration, so do not adopt it for a
single-entry package.

Both shapes produce the same consumer contract; the choice is about how many
entries and packages the build must serve.

## Generated publish manifest

Publishing the development `package.json` leaks `devDependencies`, `scripts`,
and internal fields, and risks shipping a stray `type`. Generate a manifest into
the output directory instead:

- start from the development manifest;
- remove `devDependencies`, `scripts`, and `private`;
- delete `type` for a dual package;
- set `types`, `main`, `module`, and the full `exports` map to the built paths;
- keep `dependencies` and `peerDependencies`.

Publish with the output directory as the package root so the generated manifest
and built files are the published tree, and copy `README` and `LICENSE` there.
Marking the root manifest `"private": true` makes an accidental publish of the
development tree fail rather than shipping the wrong files.

## External dependencies

A library MUST NOT inline its runtime or peer dependencies. Bundling them
duplicates code, breaks `instanceof` and singletons across copies, defeats the
consumer's deduplication, and can violate a peer contract. Derive the external
list from `dependencies` and `peerDependencies` so it stays correct as they
change. Node.js built-ins are always external. Inline only a build-only helper
that is intentionally vendored and licensed for redistribution.

## Provenance and automated publishing

Prefer publishing from CI with registry authentication that needs no long-lived
token. npm supports OIDC-based trusted publishing with provenance, which
records where and how the package was built and requires `id-token: write` on
the publishing job. When a token is unavoidable, treat it as a secret: pass it
through a scoped environment variable, never a command-line argument or source,
and rotate it if exposed.

Derive the version from commit history with the repository's release tool rather
than editing a manifest, publish only from a trusted branch or tag, and run the
tool's dry run or non-publishing verification before the first real publish. A
publish is effectively irreversible; a mistaken version usually cannot be
overwritten, only deprecated or superseded.

## Build review checklist

- [ ] The single-package or monorepo shape matches the entry-point count and
      layout.
- [ ] `exports` is the source of truth and lists `types` first in every
      condition set.
- [ ] `import` points at ESM output and `require` points at CJS output for every
      entry.
- [ ] No stray `"type": "module"` ships in a dual package's published manifest.
- [ ] Runtime and peer dependencies are external in the bundle; only intended
      build-only helpers are inlined.
- [ ] The published manifest is generated, without `devDependencies`, `scripts`,
      or `private`, with built paths.
- [ ] The root development manifest is `"private": true` and `README` and
      `LICENSE` are copied into the output directory.
- [ ] A clean build removes stale output and emits the expected ESM, CJS, and
      declaration files.
- [ ] A packed tarball is imported and required in a clean consumer across the
      supported runtimes.
- [ ] The version comes from the release tool, publishing runs in CI from a
      trusted ref, and any token is handled as a secret.
- [ ] No registry, package manager, Node.js version, test runner, or command is
      generalized from a project-specific example.
