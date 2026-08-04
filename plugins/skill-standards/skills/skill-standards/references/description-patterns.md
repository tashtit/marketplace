# Description patterns

The `description` is the only text most retrieval systems match against, so it
decides whether the skill is ever loaded. Make it state the capability and the
situations that should trigger it.

## Shape

Write one string that answers two questions:

1. What does the skill do? (the capability)
2. When should it be used? (concrete triggers)

Prefer the third person and lead with the capability:

```yaml
description: Author and review agent skills that are discoverable and safe. Use when writing a new SKILL.md, reviewing a skill change, or auditing skill frontmatter and triggers.
```

## Trigger phrases

Include at least three phrases that resemble real user requests. Draw them from
the actual verbs and nouns a user would type, not paraphrases:

- "writing a new SKILL.md"
- "reviewing a skill change"
- "auditing skill frontmatter"

More specific triggers improve matching. "Use when working with skills" is too
broad to distinguish this skill from any other.

## Length

Aim for roughly 50–500 characters. Too short omits triggers; too long dilutes
the match and is often a sign that body content leaked into the description.

## Anti-patterns

| Description | Problem |
| --- | --- |
| `Provides guidance for skills.` | Vague; no triggers; states no concrete capability. |
| `Use this skill when you want help.` | Bare second person; no capability; no specific trigger. |
| `Skill for skills stuff and other things.` | Filler; nothing to match against. |
| A 900-character paragraph | Body content in the description; dilutes retrieval. |
