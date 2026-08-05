# Human review checklist

- [ ] The response inspects existing diagrams and real structure before drawing.
- [ ] The intended level (C1 or C2) and audience are stated up front.
- [ ] Each level stays at its own abstraction; no mixing of context, containers,
      and code in one diagram.
- [ ] The smallest useful set of diagrams is produced.
- [ ] A C1 shows exactly one system in focus with an unambiguous boundary.
- [ ] A C1 shows all actors and all external systems as boundaries, not
      internals.
- [ ] Every C1 interaction is directional and labeled with intent.
- [ ] A C2 documents each container's name, type, responsibilities, and
      technology.
- [ ] A container is a deployable/runnable unit, never a class, module, or file.
- [ ] C2 relationships are directional and labeled with the runtime interaction.
- [ ] The C2 stays consistent with its C1 boundary, actors, and externals.
- [ ] One visual vocabulary is used and every element and relationship is
      labeled.
- [ ] No credential, secret, token, or private endpoint is placed in a diagram.
- [ ] No specific drawing tool, diagram language, or format is mandated.
- [ ] Output is materially equivalent on each claimed platform.

After reviewing a scenario on a platform, record the outcome in
`acceptance.json` beside this file. Results are pinned to the plugin version,
so a version bump requires a fresh review.
