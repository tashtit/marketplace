# Dependency intake evidence

How to gather the evidence the seven checks require, per ecosystem, and what
the answers should look like when they are written down.

Every command below reads public metadata over the network and changes nothing
in the repository. Run them before the dependency is declared, not after.
Nothing here inspects private registries; substitute the equivalent command for
an internal registry and say so in the record.

## Ecosystem-neutral sources

- [deps.dev](https://deps.dev) — dependents, transitive tree, licenses, and
  advisories across npm, PyPI, Go, Maven, Cargo, and NuGet.
- [OSV](https://osv.dev) — vulnerability data keyed by package and version;
  `osv-scanner` runs the same data against a lockfile.
- [OpenSSF Scorecard](https://securityscorecards.dev) — automated maintenance,
  branch protection, signing, and dangerous-workflow checks for a source
  repository. Read the individual checks, not the aggregate number.
- [SPDX License List](https://spdx.org/licenses/) — the canonical identifiers
  to record. If the project's license is not on that list, read the text.
- [Sigstore and npm provenance](https://docs.npmjs.com/generating-provenance-statements)
  — how to confirm an artifact was built from the repository it claims.

Vendor behavior changes; verify against the current documentation rather than
from memory when a decision depends on a registry feature.

## npm

```bash
npm view <package> versions dist-tags time.modified maintainers repository license
npm view <package> dependencies
```

Evidence to capture:

- **Usage:** dependent count and weekly downloads. A package with heavy
  download counts but no dependents is often pulled in by one framework, not
  independently adopted.
- **Health:** `time.modified` against the ecosystem's current runtime; the
  number of maintainers; whether the repository field resolves to a real
  source tree containing the published files.
- **Provenance:** a published provenance attestation, or a signed release plus
  a tag that matches the artifact. `npm audit signatures` verifies registry
  signatures for what is already installed.
- **Weight:** the transitive count and install size the package adds. Compare
  candidates on the tree they drag in, not the package alone.

Repository rules:

- Install with the lockfile (`npm ci`), never a floating install, in CI.
- Run installs with `--ignore-scripts` where the toolchain allows it, and
  record every dependency that genuinely needs a lifecycle script and why.
- Prefer packages with no `postinstall`, no native build step, and no bundled
  binaries downloaded at install time.
- Treat a scoped package from a namespace you already trust as materially
  safer than an unscoped same-named package.
- Keep a devDependency a devDependency. A build-time package that lands in
  `dependencies` ships its tree to every consumer.

Red flags: a name one character away from a popular package; a version jump to
a very high number from an unknown author (dependency confusion); a package
whose README is copied from another project; a maintainer added days before
the release you are pinning.

## GitHub Actions and reusable workflows

An action is code that runs inside the pipeline with the pipeline's token,
secrets, and network. Review it as a build-time dependency with elevated
privilege, not as configuration.

```bash
gh api repos/<owner>/<action>/releases/latest --jq '.tag_name'
gh api repos/<owner>/<action>/commits/<tag> --jq '.sha'
```

Rules:

- Pin a third-party action to a full 40-character commit SHA, resolved from the
  tag you reviewed, and keep the tag in a trailing comment for readability. A
  tag and a branch are both mutable and can be moved onto different code after
  review. See
  [GitHub's hardening guidance](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions#using-third-party-actions).
- An action published by GitHub itself may use an exact release tag when
  repository policy allows it; a movable major tag such as `v4` never
  qualifies.
- Read what the action does with `GITHUB_TOKEN`, secrets, and the runner
  filesystem before pinning it. Prefer an action that declares narrow
  permissions and does not require write scopes.
- Prefer a short inline script over an action that wraps one CLI call. The
  action adds a trust relationship the script does not.
- Cross-repository reusable workflows follow the same pinning rule.

Red flags: an action that requires broad `permissions`; one that curls a
script at runtime; a fork of a popular action under an unfamiliar owner; a
repository with no releases and only branch references.

## Container base images

- Pin by digest (`image@sha256:...`), not by tag. Tags are reassigned.
- Prefer an image from the upstream project or a distribution you already
  trust, with a documented rebuild cadence for CVE patching.
- Record the image's own license and the licenses of what it bundles; a base
  image is a package tree.
- Check the image is rebuilt for security updates rather than published once.

## Python, Go, Rust, and other language ecosystems

The checks are identical; only the commands change.

```bash
pip index versions <package>            # candidate versions
pip download --no-deps --no-binary :all: <package>==<version>   # inspect the sdist
go list -m -versions <module>
go mod why <module>
cargo info <crate>
```

Ecosystem notes:

- **Python:** a wheel can execute arbitrary code at build time from an sdist;
  prefer projects that publish wheels and attestations. Constrain with a
  lockfile or hash-pinned requirements, never a bare range.
- **Go:** module paths are owned by their domain, so verify the domain, and
  rely on the checksum database rather than disabling it.
- **Rust:** `cargo` crates may run build scripts; review `build.rs` for a new
  crate the same way you would review an npm lifecycle script.

## System packages and fetched binaries

- Install from the distribution's signed repositories, pinned to a version.
- Any binary fetched by a script must be verified against a published checksum
  or signature from a second channel, and the checksum must be committed.
- A `curl | sh` installer is not acceptable in a build; download, verify, then
  execute.

## License classes

Record the SPDX identifier and decide against the project's distribution model.

| Class | Examples | Default handling |
| --- | --- | --- |
| Permissive | MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, 0BSD | Allowed; keep the attribution notices. |
| Weak copyleft | MPL-2.0, LGPL-3.0, EPL-2.0 | Allowed for unmodified library use; document how modifications would be released. |
| Strong copyleft | GPL-3.0, AGPL-3.0 | Blocked unless the project itself is distributed under compatible terms; AGPL reaches hosted services. |
| Source-available | BUSL-1.1, SSPL, Elastic-2.0, "fair source" | Not open source. Blocked without an explicit legal decision. |
| Unclear | absent, "custom", conflicting files, dual licenses | Blocked until the text is read and the choice is recorded. |

Apache-2.0 adds a patent grant and a NOTICE obligation; GPL-2.0-only is
incompatible with Apache-2.0. When a transitive dependency carries a stronger
license than the direct one, the stronger license governs the decision.

## The dependency record

One record per direct dependency, stored in the repository and reviewed like
code. The fields exist because each answers one of the gate's checks:

| Field | Check it answers |
| --- | --- |
| `ecosystem`, `name`, `version` | What is pinned, and where the manifest must agree. |
| `purpose` | Need. |
| `alternatives` | Fit. |
| `adoption` | Usage and health, with numbers and their date. |
| `provenance` | Trust: how the artifact's origin was verified. |
| `license` | SPDX identifier of the distributed artifact. |
| `source` | The canonical source repository the artifact is built from. |
| `reviewed_by`, `reviewed_on` | Who accepted the risk, and when. |

Make it enforceable: a check that fails when a declared dependency has no
record turns the gate from a convention into a build failure, and a warning
when a recorded version no longer matches the manifest keeps updates visible
without blocking them.

Automate what a machine does better than a reviewer — vulnerability and license
diffing on pull requests, scheduled grouped update pull requests, lockfile
enforcement in CI — and keep the human judgment for need, fit, and trust.
