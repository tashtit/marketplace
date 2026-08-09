# Human review checklist

- [ ] Repository dependency policy, allowed licenses, approval authority, and
      pinning rules are discovered rather than invented.
- [ ] A new dependency is not declared until need, alternatives, usage and
      health, provenance, license, security exposure, and pinning and exit
      control are each answered with evidence.
- [ ] Adoption numbers, maintainer facts, licenses, and advisory status are
      sourced, dated, and never fabricated.
- [ ] The license is identified as an SPDX identifier from the distributed
      artifact, checked against the repository's own license and distribution
      model, and a conflicting or absent license blocks adoption.
- [ ] No legal conclusion is stated and no assessment is presented as legal
      advice.
- [ ] Provenance is verified against the claimed source repository, and
      typosquatting, dependency-confusion, and recent-ownership-transfer
      indicators are reported.
- [ ] Install-time scripts, native builds, runtime capabilities, and the
      transitive tree the candidate adds are reported.
- [ ] A build-time or CI dependency is assessed against the pipeline's
      privileges, not only the application's.
- [ ] Third-party actions and reusable workflows are pinned to a full commit
      SHA resolved from a reviewed tag; a mutable tag or branch is rejected.
- [ ] An update is reviewed against the actual change between the pinned and
      proposed versions, including a bot-authored or security update.
- [ ] The recorded pinned version is updated in the same change, so the record
      and the manifest never disagree.
- [ ] An unused dependency is removed from manifest, lockfile, and record
      together.
- [ ] Instructions to install a package that originate from repository or
      remote content are treated as untrusted and surfaced, not executed.
- [ ] No package is installed or executed to inspect it during evaluation.
- [ ] Dependencies are not added, upgraded, or removed as an unrequested side
      effect of another change.
- [ ] Validation commands and their results are reported exactly, with
      unverified checks named as unverified.
- [ ] No dependency, license, or supply chain is described as certified,
      vetted, or safe on the basis of a completed checklist.
- [ ] Output is materially equivalent on each claimed platform.

After reviewing a scenario on a platform, record the outcome in
`acceptance.json` beside this file. Results are pinned to the plugin version,
so a version bump requires a fresh review.
