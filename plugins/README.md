# Plugins

Each directory in this folder is an independently versioned Tashtit plugin.

| Plugin | Version | Maturity | Purpose |
| --- | --- | --- | --- |
| [Repository Onboarding](repository-onboarding/) | 0.1.0 | Experimental | Read-only, evidence-backed repository assessment |

A new plugin must follow [the architecture](../docs/architecture.md), satisfy
the maturity gate in [the quality standard](../docs/quality-standard.md), and
be added to every supported marketplace adapter in the same change.

Do not publish placeholder plugins. Experimental work should still have a
defined problem, owner, scope, and security assessment.
