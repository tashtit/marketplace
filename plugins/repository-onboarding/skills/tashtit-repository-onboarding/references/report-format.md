# Repository onboarding report

Use this structure. Omit a subsection only when it is genuinely irrelevant;
write `Unknown` when it is relevant but unsupported.

## 1. Orientation

- repository purpose;
- primary users or consumers;
- architecture in one short paragraph;
- confidence and inspection limits.

## 2. Repository map

Summarize major components and their responsibilities in a compact table:

| Component | Responsibility | Evidence | Confidence |
| --- | --- | --- | --- |

Use repository-relative evidence paths. Add a field, target, section, or line
reference when it materially improves verification.

## 3. Developer workflow

List discovered prerequisites and commands for:

- setup;
- build;
- test;
- lint and format;
- type checking;
- local development;
- migrations or generated code.

State `Documented, not executed` for every command because this skill does not
run project code. Flag contradictory commands or missing prerequisites.

## 4. Delivery and operations

Describe CI gates, release flow, deployment targets, runtime services,
configuration interfaces, observability, rollback evidence, and operational
documentation. Never include credential values.

## 5. Ownership and change control

Identify maintainers, ownership rules, contribution workflow, review policy,
security reporting, support channels, and architecture-decision records.

## 6. Risks and gaps

Order findings by impact:

| Priority | Finding | Why it matters | Evidence | Confidence |
| --- | --- | --- | --- | --- |

Use `P0` only for an immediate safety or data-loss concern, `P1` for a blocker,
`P2` for material friction, and `P3` for an improvement.

## 7. Recommended next steps

Provide a short, ordered list. Tie every recommendation to a finding. Keep
suggested changes separate from repository facts and do not apply them.

## 8. Open questions

Ask only questions whose answers would change an engineer's next action or the
assessment's confidence.

## 9. Evidence index

List the most important inspected paths and what each established. Include
notable exclusions and inaccessible paths.
