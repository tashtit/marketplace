---
name: tashtit-architecture-diagrams
description: Create or review C4 System Context (C1) and Container (C2) architecture diagrams. Use when documenting what a system does, who uses it, and what it depends on, or when showing the major deployable units, their responsibilities, technologies, and runtime relationships.
---

# Architecture Diagrams

Give a reader a true, appropriately abstract picture of a system: at C1, where
the system sits among its users and neighbors; at C2, what it is built from and
what runs where. Apply explicit user requirements and any repository or
organization diagramming conventions first. Treat this skill as a vendor-neutral
baseline and a Tashtit convention, not a certification.

Use `MUST`, `SHOULD`, and `MAY` deliberately. This skill is notation-neutral: it
does not require a particular drawing tool, diagram language, or rendering
format. Reuse whatever the repository already uses.

## Inspect before drawing

Read the repository's existing diagrams, README, service or module boundaries,
deployment manifests, and dependency configuration. Derive the diagram from what
the system actually is, not from an idealized design. Name the intended audience
and the level (C1 or C2) before drawing; a diagram that mixes levels serves no
audience well.

## Level discipline

- Keep each level at its own abstraction. A C1 diagram MUST NOT expand internal
  containers; a C2 diagram MUST NOT drill into individual classes or functions.
- Draw the smallest set of diagrams that answers the reader's question. Do not
  produce a C2 when a C1 answers the need, and do not omit a C1 that the C2
  assumes.

## C1 — System Context

The System Context diagram establishes the system boundary and its place in the
wider ecosystem.

- Exactly one **system in focus** MUST be shown as the center of the diagram.
- All **actors** (human users or roles) who interact with the system MUST be
  shown.
- All **external systems** the system depends on or serves — APIs, legacy
  systems, third-party services — MUST be shown as boundaries, not internals.
- Every interaction MUST be a directional, labeled relationship describing the
  intent (for example `Submits payment`, `Views account`), not an unlabeled
  line.
- The system boundary MUST be unambiguous: a reader can tell what is inside the
  system from what is outside.
- The diagram SHOULD be legible to non-technical stakeholders; avoid internal
  jargon at this level.

## C2 — Container

The Container diagram zooms one level in and shows the major deployable or
executable units of the system in focus.

- A **container** is any independently deployable or runnable unit: web app,
  mobile app, backend API, database, message queue, serverless function, cache,
  and similar. It is not a class, module, or source file.
- For each container the diagram MUST document:
  - **Name** — how the team refers to it;
  - **Type** — what kind of unit it is (for example Web App, REST API,
    Database, Queue);
  - **Responsibilities** — a one-line summary of what it does;
  - **Technology** — the framework, language, platform, or engine.
- Relationships between containers MUST be directional and labeled with the
  runtime interaction (for example `Reads/writes`, `Publishes events`,
  including protocol when it matters).
- People and external systems from the C1 diagram that interact directly with a
  container SHOULD be carried through so the C2 stays consistent with the C1.
- The C2 MUST stay consistent with its C1: it does not add actors or external
  systems the C1 omitted, nor contradict its boundary.

## Consistency and audience

- Use one visual vocabulary within a diagram set: a shape or style for a person,
  a system, a container, and an external dependency, applied consistently.
- Every element and relationship SHOULD be labeled; unexplained boxes and lines
  are defects.
- State the audience and keep the diagram at the level that audience needs.
- Keep the diagram close to the code it describes and update it when the
  described structure changes; a stale diagram is worse than none.

See `references/c4-levels.md` for element checklists and worked examples.

## Definition of done

- The intended level and audience are stated, and the diagram stays at that
  level.
- A C1 shows exactly one system in focus, all actors and external systems, an
  unambiguous boundary, and directional labeled interactions.
- A C2 documents each container's name, type, responsibilities, and technology,
  with directional labeled runtime relationships, and stays consistent with its
  C1.
- One visual vocabulary is used, every element and relationship is labeled, and
  no level is mixed.
