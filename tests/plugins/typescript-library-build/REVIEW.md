# Human review checklist

- [ ] The single-package or workspaces-monorepo shape is chosen from the
      entry-point count and layout, not from habit.
- [ ] The registry, package manager, Node.js range, test runner, and release
      tool are discovered rather than invented.
- [ ] `exports` is the source of truth and lists `types` first in every
      condition set.
- [ ] `import` points at ESM output and `require` points at CJS output for every
      entry, with `main` and `module` kept for legacy tooling.
- [ ] No stray `"type": "module"` ships in a dual package's published manifest.
- [ ] Runtime and peer dependencies are external; only intended build-only
      helpers are inlined.
- [ ] The published manifest is generated from the development manifest, without
      `devDependencies`, `scripts`, or `private`, with built paths.
- [ ] The root development manifest is `"private": true` and `README` and
      `LICENSE` are copied into the output directory.
- [ ] A clean build removes stale output and emits the expected ESM, CJS, and
      declaration files.
- [ ] A packed tarball is imported and required in a clean consumer across the
      supported Node.js range before the package is trusted.
- [ ] Versions come from the release tool, publishing runs in CI from a trusted
      ref, and any token is handled as a secret.
- [ ] Publishing and other external side effects are not performed without
      authorization, and a dry run or recovery path is described.
- [ ] No registry, package manager, Node.js version, test runner, or command is
      generalized from a project-specific example.
- [ ] No package supply-chain or production-readiness certification is claimed.
- [ ] Output is materially equivalent on each claimed platform.

After reviewing a scenario on a platform, record the outcome in
`acceptance.json` beside this file. Results are pinned to the plugin version,
so a version bump requires a fresh review.
