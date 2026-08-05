---
name: evaluate-dockerfile
description: Evaluate Node.js Dockerfiles in a local checkout for maturity issues — Alpine base images, source copied before dependency install, end-of-life Node.js versions, Node version drift from .nvmrc, and npm used as the container entrypoint. Use when asked to audit or evaluate a Dockerfile, check container image hygiene, or score Dockerfile maturity. Applies deterministic fixes only when the user explicitly asks.
---

# Evaluate Dockerfile

Evaluate Node.js Dockerfiles against a fixed rule catalog. Read the file
contents only; never build the image or run a container to reach a finding.
Fixes are applied only when the user explicitly asks, and only for rules marked
fixable below.

## Discovery

Find files named `Dockerfile` or `Dockerfile.*` at any depth, excluding
`node_modules`. Evaluate each independently and report findings per file with a
line number. Only Node.js Dockerfiles (a `FROM` that references a `node` image)
are in scope for the Node-specific rules below.

## Rules

Each rule lists its stable id, detection, priority, weight, whether it is
automatically fixable, and the reference to cite.

### dockerfile-nodejs-slim (Medium, weight 3, fixable)

- Detect: a base image line matching `FROM <registry>/node:<tag>-alpine`
  (regex `^\s*FROM\s+.+/node:.+-alpine`).
- Why: the Alpine (musl) variant frequently breaks native modules; the Debian
  `slim` variant is more compatible at a comparable size.
- Fix: replace the `-alpine` suffix with `-slim` on the matching image tag.
- Reference: <https://docs.docker.com/develop/develop-images/dockerfile_best-practices/>

### dockerfile-copy-src-before-install (High, weight 4, report-only)

- Detect: a broad source copy (for example `COPY . .`) appears **before** the
  dependency install step (`npm install`, `npm ci`, or `yarn install`). This
  defeats Docker layer caching because any source change invalidates the
  dependency layer.
- Why: copying `package.json` and the lockfile first, installing, then copying
  the rest keeps the install layer cached until dependencies change.
- Remediation (manual): reorder to copy `package*.json` first, run the install,
  then `COPY . .`. Report only — reordering is not always safe to automate.
- Reference: <https://docs.docker.com/develop/develop-images/dockerfile_best-practices/>

### dockerfile-nodejs-end-of-life (Medium, weight 2, report-only)

- Detect: a pinned Node.js version `FROM ...node:<X.Y.Z>...` whose version is
  older than the configured stable floor (`18.0.0`).
- Why: end-of-life Node.js lines stop receiving security fixes.
- Remediation (manual): bump to a supported LTS line, reinstall dependencies,
  and run the project's tests. Report only — a major bump needs verification.
- Reference: <https://nodejs.org/en/about/previous-releases>

### dockerfile-node-nvmrc-compat (Medium, weight 2, report-only)

- Precondition: an `.nvmrc` exists next to the project. If it does not, this
  rule is not relevant and is excluded from the score.
- Detect: the Node.js **major** version in the Dockerfile base image differs
  from the major version declared in `.nvmrc`.
- Why: drift between the container and the declared dev version causes
  "works on my machine" failures.
- Remediation (manual): align the Dockerfile major version to `.nvmrc`.
- Reference: <https://github.com/nvm-sh/nvm#nvmrc>

### dockerfile-use-node-command (Low, weight 2, report-only)

- Detect: a `CMD` instruction that invokes npm, for example
  `CMD ["npm", "start"]` (regex on `CMD` lines calling `npm`).
- Why: `npm` as PID 1 adds a process layer and mishandles signals; invoking
  `node` directly (`CMD ["node", "dist/main.js"]`) starts faster and forwards
  signals correctly.
- Remediation (manual): replace the npm `CMD` with a direct `node` invocation of
  the built entrypoint. Report only — the entrypoint path must be confirmed.
- Reference: <https://docs.docker.com/develop/dev-best-practices/>

## Fixing on request

Only `dockerfile-nodejs-slim` is automatically fixable (deterministic
`-alpine` → `-slim` substitution on the matched line). Apply it only when the
user asks, and only to files you reported. For every other rule, restate the
manual remediation instead of editing the file.
