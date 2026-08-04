# Skill Standards

Skill Standards holds an agent skill to a verifiable bar: a discoverable
third-person description, a lean instructional body, honest references, and a
safety review for skills that are loaded into untrusted repositories.

## Maturity

**Experimental — 0.1.0.** Behavioral compatibility still requires review on
each target agent.

## Defaults

- require valid frontmatter with a third-person description and real triggers;
- keep the body imperative and lean, with detail pushed into references;
- require every named reference to exist with real content;
- forbid secrets, fixed temp paths, and execution of untrusted content;
- flag contradictions between skills, and between a body and its references;
- treat removing or weakening a rule as a behavioral change.

The plugin is guidance only. It does not execute skills, call the network, or
change repository state.

## Threat model

| Threat | Control |
| --- | --- |
| Undiscoverable skill | Require capability plus concrete trigger phrases in the description |
| Context bloat | Cap body length and push detail into on-demand references |
| Dangling reference | Require every named reference to exist with real content |
| Secret or PII leakage | Forbid credentials, hosts, and personal data in every skill file |
| Prompt injection via untrusted input | Forbid executing strings built from repository, issue, or diff content |
| Predictable-path attack | Require `mktemp` over fixed temporary paths |
| Silent behavioral regression | Treat rule removal or softening as a reviewed change |

See [CHANGELOG.md](CHANGELOG.md). Maintainer-only evaluation material lives
outside the distributed plugin in the
[repository test suite](../../tests/plugins/skill-standards/).
