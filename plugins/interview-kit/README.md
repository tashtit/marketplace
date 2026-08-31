# Interview Kit

Interview Kit runs mock system design interviews about code you already wrote,
and grades them against a library in which every claim cites the source that
stated it. It ships two skills and that library.

The design constraint that shapes everything here: **the library is the answer
key.** It records the concerns an implementation is later interviewed against,
and `probes/` is literally the question list. So the plugin is built to be
enabled *after* you finish building, not while.

## Installation

```bash
# Claude Code
claude plugin marketplace add tashtit/marketplace
claude plugin install interview-kit@tashtit

# GitHub Copilot CLI
copilot plugin marketplace add tashtit/marketplace
copilot plugin install interview-kit@tashtit
```

Interview Kit is not published to the Codex catalog; it supports Claude Code and
GitHub Copilot CLI only.

### Enable it after the attempt, not during

Install once, then toggle enablement around the exercise:

```bash
# While building: keep it off, so nothing can read the answer key.
copilot plugin disable interview-kit@tashtit

# Ready to be interviewed:
copilot plugin enable interview-kit@tashtit
```

Disabling is the load-bearing step, and it is worth understanding why the
softer measures were not enough. Neither host lets a skill opt out of being
offered: a skill is advertised to the selector by its description, and the
strongest available wording is a description that argues against its own
selection. That is a request, not a mechanism. Removing the plugin from the
enabled set is the only hard guarantee, which is why this plugin is packaged
separately from the code you practice on.

## Maturity

**Experimental — 0.1.0.** Behavioral compatibility still requires review on the
target agent. The interview's prompted-versus-unprompted analysis depends on a
session store and is only verified on GitHub Copilot CLI; see
[Prerequisites](#prerequisites).

## Skills

`skills/interview-kit/SKILL.md` is a router; each skill also triggers on its own
description.

| Skill | What it does | Writes |
| --- | --- | --- |
| `mock-design-interview` | Interviews you about one implementation you built, then assesses a level | Nothing |
| `extract-design-concepts` | Mines one named source into the library, cited claim by claim | The library |

```text
extract-design-concepts  ──writes──▶  system-design-concerns  ──reads──▶  mock-design-interview
     (one source in)                 (the library — plain data)         (interviews one attempt)
```

### mock-design-interview

Scopes to one attempt directory, reads it and its git history, recovers session
transcripts to tell decisions you asked for from decisions an agent volunteered,
then asks questions one at a time and ends with a level assessment.

Two rules make it worth doing:

- **A probe never names the concern it tests.** It describes a symptom and lets
  you find the cause. "Reads are at 800ms, the index is used, CPU is flat" is a
  probe; "have you considered caching?" hands over the answer.
- **A thin answer gets a follow-up, not a nod.** Agreeableness is the single
  failure mode that makes the exercise worthless.

It refuses to interview code it helped write, which is the other reason to keep
the plugin disabled during the build.

### extract-design-concepts

The library's only writer. One run mines one source. Every claim carries a tag
(`[S1]`, `[S2]`) resolving to a `## Sources` entry, and the rule is absolute:
**if the source did not state it, it does not go in the file.** Gaps are recorded
as named questions under `## Not covered by sources` and never answered. Sources
that disagree are both recorded and never adjudicated.

A three-claim file is a success. A file with mixed provenance is worse than a
thin one, because a reader can no longer tell which claims are verified.

## The library

Bundled at `references/system-design-concerns/`: `concepts/` (what is true),
`level-expectations.md` (what is expected at each level, with the source's own
hedges preserved), `probes/` (how to ask), `rubric.md` (a generic 0–5 scale), and
`README.md` (the concept index and which sources have been processed).

It has **no frontmatter and is deliberately not a skill** — there is nothing to
select, and the two skills open it by path.

### Reading is bundled; writing is not

`scripts/library-path.sh` resolves two different paths on purpose:

| Mode | Resolves to | Why |
| --- | --- | --- |
| `read` | the bundled copy | Always correct to read; ships with the plugin |
| `write` | a versioned checkout, or **exit 3** | The bundled copy sits in a host-managed install directory with no history, so a reinstall or upgrade would silently discard anything written there |

On exit 3 the extractor asks where the library should live rather than writing
somewhere a later upgrade would erase. To contribute claims back, run the
extractor from a checkout of this repository; the script finds
`plugins/interview-kit/references/system-design-concerns/` and writes there.

## Prerequisites

- **A web-fetch capability** for `extract-design-concepts` when the source is a
  URL. Without one it asks for pasted text rather than extracting from a preview
  or an abstract.
- **A session store** for the interview's prompted-versus-unprompted axis. This
  is a host capability, currently verified only on GitHub Copilot CLI. Without
  it the interview still runs and still assesses the design, but reports that
  axis as unavailable rather than guessing — a level bar phrased "without being
  prompted" cannot be applied from the code alone.
- **Nothing else.** No manifest, no metadata file, no naming convention for
  sessions.

## Practice repository layout

The interview reads one convention, and only one:

```text
<problem>/<attempt>/     one directory per attempt
shared/                  reusable code, outside the attempt directories
```

Keep the problem name in the path — an `attempt-1` at a repository root cannot be
told apart from any other problem's first attempt. A directory beats a branch as
the boundary because the working directory is what a session store records and it
never changes, while a branch can be renamed mid-task and split a transcript in
two.

Shared code stays outside the attempt directories on purpose: reusing a cache is
a different claim about judgment than deciding this problem needs one, and the
separation is what lets an interview tell them apart.

Committing and branching are both optional. The transcript carries the decision
sequence either way.

## Non-goals

- **Not a design assistant.** It does not answer design questions, recommend
  architecture, or review code. A concept file existing is never a reason to add
  infrastructure — several of the library's own sources make the opposite point,
  that at low volume the simple thing is correct.
- **Not a knowledge base to consult while building.** That use is precisely what
  invalidates the assessment.
- **Not a complete treatment of system design.** Coverage is exactly as broad as
  the sources processed, and each concept file names its own gaps.
- **Not hand-authorable.** Content arriving without a citation defeats the
  library's purpose, so the extractor is the only writer.
