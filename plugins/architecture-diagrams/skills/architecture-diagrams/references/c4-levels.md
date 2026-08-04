# C4 levels reference

Element checklists and worked examples for the C1 and C2 contracts in
`SKILL.md`. The notation below is illustrative; use whatever diagram tool or
language the repository already uses.

> Reference: the C4 model — <https://c4model.com>

## C1 — System Context checklist

- [ ] Exactly one system in focus, at the center.
- [ ] Every human actor or role that interacts with it.
- [ ] Every external system it depends on or serves, shown as a boundary.
- [ ] Every relationship directional and labeled with intent.
- [ ] An unambiguous boundary between inside and outside.
- [ ] Legible to non-technical stakeholders.

### Example (illustrative)

```plaintext
[ Customer ]
     | Views balance, submits payments
     v
[ Internet Banking System ]   <-- system in focus
     |                         \
     | Gets account data        \ Sends notifications
     v                           v
[ Mainframe Banking System ]   [ Email Service ]   <-- external systems
```

## C2 — Container checklist

- [ ] Each container has a name, type, responsibilities, and technology.
- [ ] A "container" is a deployable/runnable unit, not a class or module.
- [ ] Relationships are directional and labeled with the runtime interaction.
- [ ] Actors and external systems from the C1 that touch a container are carried
      through.
- [ ] The C2 does not contradict the C1's boundary, actors, or externals.

### Example (illustrative)

```plaintext
[ Customer ]
     | HTTPS
     v
[ Single-Page App ]        Type: Web App        Tech: browser SPA
     | JSON over HTTPS
     v
[ API Application ]        Type: REST API       Tech: backend service
     |  \
     |   \ Sends email
     v    v
[ Database ]  [ Email Service (external) ]
Type: Database    Reads/writes account data
```

## Level discipline

- C1 answers "what is this system, who uses it, what does it touch?"
- C2 answers "what is it built from and what runs where?"
- Do not expand containers inside a C1, and do not drill into code inside a C2.
- Draw the smallest set of diagrams that answers the reader's question.

## Reference

- The C4 model (Simon Brown). <https://c4model.com>
