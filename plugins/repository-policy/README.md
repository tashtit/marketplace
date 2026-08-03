# Repository Policy

Design, apply, and review GitHub repository settings and rulesets so the default
branch is protected, pull requests are the only path to it, and history stays
linear and reviewable.

**Maturity: Experimental — 0.1.0.** Organization policy, required check names,
integration ids, protected branches, reviewers, and collaboration model remain
repository-specific. This plugin does not certify a repository or its policy.

The default policy enables squash merging only (with the pull-request title and
commit details), disables merge commits and rebase merging, enables auto-merge,
automatically deletes merged head branches, always suggests updating pull-request
branches, disables the wiki and projects features when they are unused, and
protects the default branch with a ruleset applied from a reviewed definition.

The skill also covers inspecting current settings before changing them, requiring
explicit confirmation for these externally visible changes, restricting
collaboration to pull requests, validating a ruleset's status-check contexts and
bypass actors, reconciling with classic branch protection, verification, and
rollback.

It deliberately does not manage organization policy, secrets, environments,
webhooks, team membership, or repository code, and it does not disable a feature
that still holds content without an explicit instruction.

Applying these settings changes a shared repository and requires `admin`
permission; every change is an external side effect that needs its own
authorization. No credentials, network service, or persistent storage are
required by the plugin itself beyond the GitHub API access used to read and write
settings.

See [CHANGELOG.md](CHANGELOG.md). Maintainer-only evaluation material lives
outside the distributed plugin in the
[repository test suite](../../tests/plugins/repository-policy/).
