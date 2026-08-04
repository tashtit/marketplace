# Safety review for skills

A skill is instructions an agent will follow, and it is often injected into a
repository whose contents cannot be trusted. Review every skill for the ways
those instructions can cause harm or leak.

## Secrets and identifying data

- No credentials, API tokens, private keys, session cookies, or connection
  strings appear in any skill file, including examples and fixtures.
- No internal hostnames, private endpoints, or customer data are embedded.
- Placeholders are obviously fake (`example.com`, `<token>`), never a redacted
  real value.

## Untrusted input

Repository files, issue and pull-request text, diffs, and command output are
attacker-controlled. A skill MUST NOT direct the agent to:

- execute a command, script, or expression built from that content;
- treat instructions found in that content as authorization for an action;
- expand shell constructs that transform or indirect through variable contents
  (for example, `${var@P}` or `eval` over a fetched string).

Instruct the agent to quote and pass such content as data, never as code.

## Filesystem and process hygiene

- Temporary files use `mktemp`, not fixed paths, to avoid collision and
  predictable-path attacks in shared or concurrent environments.
- Destructive filesystem or git operations are gated behind explicit user
  authorization and name their exact target.
- Any `scripts/` file states its usage and does only what the body claims.

## Side effects and disclosure

- Network calls, telemetry, and persistent storage are disclosed in the body.
- Externally visible actions — commits, pushes, pull requests, issue comments,
  releases — happen only when the user has requested that effect.
- Where feasible, the skill documents how to undo or recover from its actions.

## Portability

- Behavior is provider-neutral; provider-specific field names, endpoints, or
  flags are labeled as such and confirmed against current vendor documentation.
- Examples avoid machine-specific absolute paths and declare any narrower
  operating-system support.
- A host-specific caveat (for example, a field rejected by some GitHub
  Enterprise Server versions) is noted rather than assumed away.

Treat any failure here as blocking. Unlike a style issue, an injection path or a
leaked secret is a security defect.
