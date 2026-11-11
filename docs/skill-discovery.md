# Skill discovery and directory submissions

All entries below are **experimental**. These are preparation notes, not
claims of acceptance, approval, or behavioral review. No external submission
has been made.

## Skill-only audit

The Vercel CLI found 33 skills and copied all 33 into a temporary Codex project.
Discovery also found 33 when `skills.sh.json` was omitted: the marketplace
manifests already expose these nested paths. The file is retained for its
curated skills.sh page groupings, not for CLI discovery. This is a discovery
and packaging check, not execution of every skill or an acceptance review.

- `engineering-standards` has no bundled resource dependency;
  `github-actions-standards` includes its reference inside its skill directory.
- `maturity` requires its four `evaluate-*` skills for a full report. Install
  those together, or install the plugin.
- `agent-parity` and its four `parity-*` skills depend on each other. Install
  all five together, or install the plugin.
- `repository-governance` and `evalkit` route to sibling skills. Evalkit's
  review skills require its plugin agent; its dynamic evaluation skills need
  plugin-root scripts and host references. Install the complete plugin.
- Interview Kit skills use a plugin-root script and reference library. Install
  the complete plugin. A copied individual skill does not contain these files.
- Other skills with `references/` links have those resources inside the
  corresponding skill directory. A copy install preserves that directory.

A successful CLI install does not establish that the agent can execute a skill,
that external tools are available, or that any acceptance scenario has passed.
Review the source and platform requirements before use.

## Submission inventory

Common fields: repository `tashtit/marketplace`; author `Tashtit contributors`;
license `Apache-2.0`; maturity **Experimental**. The authoritative description
and version for each entry are in the [marketplace manifest](../.claude-plugin/marketplace.json)
and its linked plugin manifest. Verify those values against the release to be
submitted; do not submit a moving branch.

| Plugin and submission path | Suggested keywords |
| --- | --- |
| [engineering-standards](../plugins/engineering-standards/) | `engineering-standards`, `code-review` |
| [github-actions-standards](../plugins/github-actions-standards/) | `github-actions`, `ci-cd` |
| [maturity](../plugins/maturity/) | `repository-quality`, `code-review` |
| [agent-parity](../plugins/agent-parity/) | `agent-skills`, `configuration` |
| [api-design-standards](../plugins/api-design-standards/) | `api-design`, `rest-api` |
| [architecture-diagrams](../plugins/architecture-diagrams/) | `architecture`, `diagrams` |
| [dependency-standards](../plugins/dependency-standards/) | `dependencies`, `software-supply-chain` |
| [evalkit](../plugins/evalkit/) | `evaluation`, `agent-skills` |
| [git-workflow](../plugins/git-workflow/) | `git`, `pull-requests` |
| [interview-kit](../plugins/interview-kit/) | `system-design`, `interviews` |
| [logging-standards](../plugins/logging-standards/) | `logging`, `observability` |
| [repository-governance](../plugins/repository-governance/) | `github`, `governance` |
| [repository-onboarding](../plugins/repository-onboarding/) | `onboarding`, `repositories` |
| [typescript-library-build](../plugins/typescript-library-build/) | `typescript`, `libraries` |
| [typescript-style-standards](../plugins/typescript-style-standards/) | `typescript`, `code-style` |

## External submission checklist

- [ ] For each plugin, select and verify a release tag and its full 40-character
  commit SHA; package versions are not substitutes for immutable release refs.
- [ ] For each [Awesome Copilot external plugin submission](https://github.com/github/awesome-copilot/blob/main/CONTRIBUTING.md#adding-external-plugins),
  supply its name, description, repository, path, tag, SHA, version, license,
  author, and relevant keywords. Follow the issue-based review workflow.
- [ ] For each [Claude directory submission](https://claude.com/resources/articles/build-plugins-for-claude),
  verify current eligibility, package requirements, and review materials in the
  developer portal. Prepare a separate submission per plugin.
- [ ] For each [OpenAI directory submission](https://developers.openai.com/plugins/deploy/submission),
  verify account and identity requirements, package the plugin, and resolve
  validation findings before requesting review. Check the
  [Claude conversion guide](https://developers.openai.com/plugins/guides/submit-claude-plugin)
  for supported skill and local-execution requirements.
- [ ] Review platform eligibility and portability for each individual plugin,
  including plugin-level resources, local execution, and supported hosts.
- [ ] Obtain explicit approval before submitting to any external directory.

Suggested discovery keywords: `agent-skills`, `ai-agents`, `code-review`,
`engineering-standards`, `github-actions`, `repository-quality`, and
`developer-tools`. Select only keywords relevant to the individual plugin.
