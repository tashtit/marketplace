# Release process

This document defines how Tashtit plugins are released so that a consumer can
trust what they install and reproduce how it was built. It is a Tashtit
convention; where it references external formats it cites their authoritative
source.

Plugins are versioned independently with [Semantic Versioning
2.0.0](https://semver.org/spec/v2.0.0.html) once they reach candidate status, as
required by [GOVERNANCE.md](../GOVERNANCE.md) and
[the quality standard](quality-standard.md).

## Preconditions

A release MUST NOT be cut unless, at the release commit:

- `make validate` passes, including generated-adapter drift, catalog-table,
  link, Markdown, and secret checks;
- the plugin's acceptance record satisfies the maturity gate for the maturity it
  claims (see [quality-standard.md](quality-standard.md));
- the plugin `CHANGELOG.md` has a dated entry for the version being released;
- the version in the plugin manifest, the shared marketplace, and both catalog
  tables agree.

## Versioning and changelogs

- Each plugin owns a `plugins/<name>/CHANGELOG.md` in
  [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) style, newest first.
- A behavioral change MUST bump the plugin version. Because recorded reviews are
  version-pinned, a bump returns the plugin to `experimental` until it is
  reviewed again at the new version.
- Breaking behavioral changes require a major version or a documented migration
  path.

## Tags and provenance

- Releases are marked with an annotated, signed Git tag named
  `<plugin>/vMAJOR.MINOR.PATCH` (for example `logging-standards/v0.2.0`). The
  repository-wide marketplace version, when released, uses `vMAJOR.MINOR.PATCH`.
- Release automation runs from the tag in an isolated job with least privilege.
  It MUST NOT reuse deployment credentials for build steps and MUST pin all
  actions to a full commit SHA, consistent with the
  [github-actions-standards](../plugins/github-actions-standards/) plugin.
- Build provenance SHOULD be emitted as a
  [SLSA](https://slsa.dev/) provenance attestation using
  [`actions/attest-build-provenance`](https://github.com/actions/attest-build-provenance),
  so a consumer can verify which workflow, at which commit, produced an
  artifact.

## Checksums

- Every published artifact (for example a packaged plugin archive) MUST ship a
  `SHA256SUMS` file listing `sha256` digests, generated with `sha256sum` (or an
  equivalent) at release time.
- The workflow SHOULD verify the checksums after upload and fail the release if
  they do not match, and SHOULD attach the provenance attestation alongside the
  checksums.
- Consumers verify with `sha256sum --check SHA256SUMS` before trusting an
  artifact.

## Rollback

- A release that is found to be broken or unsafe is superseded by a new patch
  release; published tags and artifacts are not rewritten.
- If an artifact must be withdrawn, mark the affected version as yanked in the
  changelog with the reason and the recommended replacement, and keep the record
  visible.

## Status

Release automation is defined here but not yet wired into CI. The
[roadmap](roadmap.md) tracks the remaining implementation: a tag-triggered
workflow that builds artifacts, generates checksums, emits provenance, and
publishes them.
