# Maintainers

Tashtit is maintained in the open under the model described in
[GOVERNANCE.md](GOVERNANCE.md). This file is the authoritative, machine- and
human-readable record of who owns what. It is kept in step with
[`.github/CODEOWNERS`](.github/CODEOWNERS): every path owned in that file MUST
map to a maintainer or plugin owner listed here.

## Project maintainers

Project maintainers review changes, manage releases, moderate the community, and
enforce the quality and security standards across the whole repository.

| Maintainer | GitHub | Areas |
| --- | --- | --- |
| Tashtit maintainers | [@tashtit/maintainers](https://github.com/orgs/tashtit/teams/maintainers) | Repository, governance, security, releases, adapters |

## Plugin owners

Each plugin has an owner responsible for its accuracy, compatibility, security
posture, and lifecycle. Until an individual owner is designated, the project
maintainers own the plugin.

| Plugin | Owner |
| --- | --- |
| [engineering-standards](plugins/engineering-standards/) | [@tashtit/maintainers](https://github.com/orgs/tashtit/teams/maintainers) |
| [git-workflow](plugins/git-workflow/) | [@tashtit/maintainers](https://github.com/orgs/tashtit/teams/maintainers) |
| [github-actions-standards](plugins/github-actions-standards/) | [@tashtit/maintainers](https://github.com/orgs/tashtit/teams/maintainers) |
| [logging-standards](plugins/logging-standards/) | [@tashtit/maintainers](https://github.com/orgs/tashtit/teams/maintainers) |
| [repository-onboarding](plugins/repository-onboarding/) | [@tashtit/maintainers](https://github.com/orgs/tashtit/teams/maintainers) |

New plugins MUST add both a plugin-owner row here and a matching `CODEOWNERS`
entry in the same change.

## Becoming a maintainer

Maintainer and plugin-owner roles are earned through consistent, constructive
participation, as described in [GOVERNANCE.md](GOVERNANCE.md). Nominations are
decided by the existing maintainers.

## Security

Report vulnerabilities through the private channel in [SECURITY.md](SECURITY.md),
never in a public issue or pull request.
