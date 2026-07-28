# Governance

Tashtit is maintained in the open. The governance model favors technical
quality, security, portability, and sustainable maintenance over catalog size.

## Roles

- **Contributors** propose issues, documentation, plugins, tests, and fixes.
- **Maintainers** review changes, manage releases, moderate the community, and
  enforce the quality and security standards.
- **Plugin owners** are maintainers or designated contributors responsible for
  a plugin's accuracy, compatibility, and lifecycle.

Roles are earned through consistent, constructive participation. Maintainers
may invite contributors into additional responsibility based on demonstrated
judgment and project need.

## Decision making

Routine changes use pull-request review and lazy consensus. Material changes
require a written proposal, including:

- new core platforms or compatibility guarantees;
- changes to maturity definitions or the quality bar;
- new runtime dependencies or networked services;
- breaking plugin behavior;
- licensing or governance changes.

Maintainers seek consensus. When consensus is not practical, the maintainers
responsible for the affected area decide and document the reasoning. Conflicts
of interest must be disclosed.

## Releases and lifecycle

Plugins are versioned independently with Semantic Versioning once they reach
candidate status. Breaking behavioral changes require a major version or a
documented migration path. Security fixes may accelerate the normal review and
release process but still require retrospective review.

Deprecations must name a replacement or explain why none exists, define a
migration window, and remain visible in the catalog until that window ends.

## Vendor independence

Tashtit is not affiliated with or endorsed by Anthropic, OpenAI, GitHub, or
Anysphere. Platform support decisions are based on user value, documented
interfaces, maintainability, and testability.
