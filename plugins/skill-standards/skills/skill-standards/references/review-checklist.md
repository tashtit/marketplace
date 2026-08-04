# Skill review checklist

Work through every item against the diff for a new or changed skill. Flag a
failure rather than silently fixing it, so the author sees the behavioral
consequence.

## Frontmatter

- [ ] Block is delimited by `---` on both lines and is valid YAML.
- [ ] `name` is present, lowercase kebab-case, and matches the directory name.
- [ ] `description` is a single non-empty string, roughly 50–500 characters.
- [ ] Description is third person and states both capability and trigger.
- [ ] Description includes at least three concrete trigger phrases.

## Writing style

- [ ] Instructions use the imperative ("Read the diff"), not "you should" or
      "the agent must".
- [ ] No second-person pronoun as the subject of an instruction.
- [ ] Normative terms (`MUST`, `SHOULD`, `MAY`) are used deliberately.

## Content and length

- [ ] Body is roughly 500–2,000 words; over ~3,000 is flagged for splitting.
- [ ] The core procedure is followable without opening a reference.
- [ ] No long API specs, schemas, or extended examples inlined in the body.
- [ ] No guidance is duplicated between the body and a reference.
- [ ] Prerequisites, permissions, side effects, outputs, and a verification
      step are stated.

## Progressive disclosure

- [ ] Every reference named in the body exists on disk.
- [ ] No reference is an empty or placeholder stub.
- [ ] Each reference is listed once with a one-line "when to read it" summary.

## Structural soundness

- [ ] Any `scripts/` file is executable and carries a usage comment.
- [ ] Any `examples/` file is complete and produces the stated output.
- [ ] Bash examples write to `mktemp` files, not fixed paths.
- [ ] No hardcoded credentials, tokens, hostnames, or personal data.

## Contradictions

- [ ] The skill does not contradict another skill for the same task.
- [ ] The body does not contradict its own references.
- [ ] A rule removed since the prior version was removed on purpose.
- [ ] Any softening of `MUST` to `should`, or a mandatory step made optional,
      is intentional and noted in the change description.

## Anti-patterns

| Anti-pattern | Why it is a problem |
| --- | --- |
| `description: "Provides guidance for..."` | Vague, no triggers, not third person. |
| `description: "Use this skill when..."` | Bare second person; weak retrieval. |
| Multi-thousand-word body with no references | Loads on every trigger; wastes context. |
| Same content in the body and a reference | Redundant; wastes context tokens. |
| "You should start by..." | Second person; use "Start by...". |
| A reference named but absent on disk | The agent tries to read it and fails. |
| Fixed path such as `/tmp/out.json` | Collision and predictable-path risk. |
