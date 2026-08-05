# Architecture Diagrams

Create and review high-level architecture diagrams using the C4 model at the
System Context (C1) and Container (C2) levels.

**Maturity: Experimental — 0.1.0.** The right level of detail and audience for a
diagram depend on the system and its readers; this plugin makes no completeness
or certification claim.

The skill defines what a C1 diagram must establish (system boundary, actors,
external systems, labeled interactions) and what a C2 diagram must document for
each container (name, type, responsibilities, technology, runtime
relationships), with a consistent visual vocabulary aimed at a stated audience.

It is notation-neutral: it does not require a specific drawing tool, diagram
language, or rendering format. Use whatever the repository already uses.

No network, credentials, telemetry, or storage are required. Review is
read-only unless authoring is requested.

See [CHANGELOG.md](CHANGELOG.md). Maintainer-only evaluation material lives
outside the distributed plugin in the
[repository test suite](../../tests/plugins/architecture-diagrams/).
