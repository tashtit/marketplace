---
name: extract-design-concepts
description: Mine one named system design source — a URL, article, talk transcript, or pasted text the user supplies — into cited concept files, level bars, and interview probe seeds. Invoke only on an explicit request to add, ingest, distill, or mine that source into the system-design-concerns reference library, which this skill is the sole writer of. Never invoke it to summarize a source, to answer a design question, or as background help while writing code — and never in a session building a practice attempt, which the library grades.
---

# Extract Design Concepts

Turn one source document into cited concept reference files. Run repeatedly across many
sources; the library grows and each concept accumulates knowledge from every source that
discussed it.

## When to run this, and when not to

Run it **only when the user explicitly asks for a named source to be mined into the library.**
This skill is never background help: it does not summarize a source for a reader, it does not
answer design questions, and it must not activate because a coding task happens to touch a
subject the library covers. Answering from recorded concepts is a matter of reading the bundled
`system-design-concerns` directory, not of running this skill, which only writes.

Do **not** run it in a session that is building an implementation this library would later be
used to assess. The library grades such work, so reading a source into it mid-build puts graded
material in front of the person being graded. Finish the implementation first, or mine the source
in a separate session with the rest of this plugin disabled.

If you find yourself reaching for this skill without an explicit request naming a source, that is
the signal to stop.

## The one rule

**If the source does not state it, it does not go in the file.**

Not "the source implies it." Not "this is well known." Not "the reader will need it." You are
an extraction and attribution tool, not an author. Your own knowledge of caching, consistency,
or queues is *out of scope* — it is exactly the thing that must not leak in.

When you notice the source omits something important, you may record it under
`## Not covered by sources` as a named gap. You may not answer it.

### Why this rule is strict

A concept file whose provenance is mixed is worse than a thin one, because a reader cannot
tell which parts are load-bearing. Thin and trustworthy beats thorough and unverifiable. A
file with three cited claims is a success.

### The template trap

Do not impose a fixed section template on a concept. A uniform structure creates empty
headings, and empty headings invite invention to fill them. **Sections are emergent: a
concept file contains only the sections its sources actually support.** A source that
discusses when to use a technique and its tradeoffs, but says nothing about testing it,
produces a file with no validation section. That is correct output.

## Inputs

Ask for whichever is missing:

- **The source.** A URL to fetch, or pasted text. Fetch the whole document — paginate to the
  end; truncated input silently produces missing concepts.
- **The library path.** Resolve it with `scripts/library-path.sh`, which distinguishes reading
  from writing because the two differ:
  - `library-path.sh read` prints the bundled library. Read it to decide create-vs-extend and to
    claim the next source tag.
  - `library-path.sh write` prints a versioned checkout, or **exits 3** if there is none. The
    bundled copy lives in a managed install directory with no history, so a reinstall would
    discard anything written there. On exit 3, relay the script's message and ask the user where
    the library should live; do not write into the bundled copy, and do not fall back silently.

  When the two paths differ, the write target may lag the bundled copy. Read the write target's
  own `README.md` for the source tags and index — that is the file this run updates — and treat
  the bundled copy as reference only. The library is a plain directory, **not** a skill: it has
  no frontmatter and must not be given any.

**Fetching a URL requires a web-fetch tool.** If none is available, or the fetch fails, is
rate-limited, or hits a paywall, say so and ask the user to paste the full text. Do not extract
from an abstract, a preview, or a partial page.

Every path this skill *writes* — `concepts/`, `level-expectations.md`, `probes/`, `README.md` —
resolves against the **write** path. The two `../../references/system-design-concerns/…` links
below are exceptions: they point at the bundled copy relative to this skill's own directory, and
are reading examples only.

### Citation tags

Source tags are **library-global and permanent**. Before writing anything, read the
**Sources processed** table in the library's `README.md` and take the next unused `S<n>`. Never
reuse a tag, never renumber an existing one, and never restart numbering per file — the tag is
embedded in probe filenames and in every citation across the library, so a collision silently
misattributes claims.

Probe numbers `P<n>` are **per probe file**. When extending an existing probe file, continue
from its highest existing number.

### First run against an empty library

If `library-path.sh write` found no library, confirm the location with the user — defaulting to
`references/system-design-concerns/` at the root of the repository they are working in — then
create, before step 1:

- The directory, plus `concepts/` and `probes/`.
- `README.md` with **no frontmatter** (the library is data, and frontmatter would make it a
  selectable skill), a **Concept index** table with the columns
  `Concept | Consider it when | Sources`, and a **Sources processed** table with the columns
  `Tag | Source | Date | Concepts touched`. Both tables start empty.

Do not hand-author concept content while scaffolding. The scaffold is structure only; every
claim still arrives through this workflow, cited.

## Workflow

### 1. Read the whole source, then inventory it

Fetch or read all of it before writing anything, including sections that look like framing
("what is expected at each level" often contains the sharpest technical claims). Confirm you
reached the end — the closing section, not a truncation marker or a "continue reading" prompt.

Build an inventory of every distinct **engineering claim**: a statement about when a technique
applies, why, what it costs, how it fails, or how to decide between options. Record each with
the section it came from **and the sentence that states it** — step 7 checks claims against
this inventory, so capturing it now is what makes that check mechanical rather than a
re-reading.

Skip: product description, interview meta-advice ("tell your interviewer"), navigation,
marketing, and anything specific to the example system that carries no transferable lesson.

### 2. Decide which concepts qualify

For each candidate concept, apply the **qualification bar**:

> The source must contain at least one *transferable* statement of reasoning — a when, a why,
> a tradeoff, a failure mode, or a decision criterion. A bare mention, a name-drop, or a
> statement true only of this one system does not qualify.

Worked examples:

- Source says "we use a cache to make reads fast" → mention only. **Does not qualify** on its
  own.
- Source says "reads vastly outnumber writes, so caching the read path is where the leverage
  is, and the cache TTL must not outlive the record's expiry" → two transferable claims.
  **Qualifies.**
- Source says "we picked Postgres" → no reasoning. **Does not qualify.**
- Source says "write volume is ~1/sec, so any mature engine works; pick the one you know" →
  a decision criterion. **Qualifies.**

Record rejected candidates — they belong in the run report and in the library index, so the
user can see what you found but deliberately did not write.

**If nothing qualifies**, stop and say so. Still append the **Sources processed** row (with
"none" under concepts touched) and list the rejects, so a future run does not re-mine the same
document. Do not lower the bar to produce output.

### 3. Choose create vs extend

Search the library for an existing concept covering this ground. Match on subject, not
filename.

- **No existing file** → create it.
- **Existing file, source adds new claims** → extend it. Add the new claims; leave existing
  cited content untouched.
- **Existing file, source repeats known claims** → add the source as a corroborating citation
  on those claims. Do not duplicate the prose.
- **Existing file, source contradicts it** → record both, attributed, under
  `## Disagreements between sources`. Never silently overwrite, and never adjudicate which
  source is right.

Prefer extending over creating. Two thin files on the same subject are a failure; one file
with two sources is the goal. Split only when each part has its own trigger condition — a
reader would consult one without the other. `read-heavy-workloads` and `caching-the-read-path`
split correctly: you can be read-heavy and index your way out, and you can cache data that is
not read-heavy. "Cache TTLs" and "cache invalidation" do not split — no reader reaches one
without the other.

### 4. Write the file

Naming: `concepts/<kebab-case-concept>.md`, named for the concern, not the source's example.
`caching-the-read-path.md`, not `url-redirect-caching.md`. For the canonical shape of a finished
file, see
[caching-the-read-path](../../references/system-design-concerns/concepts/caching-the-read-path.md)
in the library.

Structure — a menu, not a form. Use only the parts the source supports, in whatever order reads
best, and add concept-specific headings where the material calls for them (`## Method`,
`## Interaction with <other concept>`, `## Limits of <technique>`):

```markdown
# <Concept name>

<One or two sentences stating the concern in general terms. Must be a
faithful generalization of the sources, and carries a citation like any
other claim.>

## When it applies
## Why it matters
## Approaches and tradeoffs
## Failure modes
## How to decide
## Validation
## Disagreements between sources
## Not covered by sources
## Sources
```

Only the last two are mandatory, because a file always has sources and always has edges — they
are the one exception to "sections are emergent," and if a source leaves no open questions,
say so in one line rather than deleting the heading. `## Disagreements between sources`
appears only when step 3 found a contradiction.

Rules for the body:

- **Every claim carries a citation** to the source that supports it, as a short tag: `[S1]`,
  `[S2]`. Multiple sources on one claim: `[S1][S2]`.
- **Generalize the reasoning, drop the specifics.** The source's example system is a vehicle.
  "A counter shared by horizontally scaled writers needs a single source of truth" is the
  concept; "the Write Service calls Redis INCR" is the instance. Keep at most one brief
  concrete illustration where it aids understanding, and mark it as an example.
- **Preserve the source's numbers** when they illustrate a method (sizing arithmetic, latency
  targets, ratios) — they teach estimation. Attribute them; do not present a source's example
  figures as universal.
- **Named technologies** stay only where the source gave a reason. "A single-threaded store
  with atomic increments suits a shared counter `[S1]`" keeps the reasoning; "use Redis" does
  not.
- **Do not smooth over gaps.** If a source names a failure mode without a fix, write the
  failure mode and stop.
- **`## Not covered by sources`** lists open questions a practitioner would still have.
  Questions only — no answers, no hints at answers. This section is the honest map of the
  library's edges and it is where future sources plug in.
- **Generalize, do not transcribe.** Keep any single quotation under roughly 25 words; beyond
  that, state the reasoning in your own words and cite it.
- **Rubric anchors are out of scope.** `rubric.md` holds one generic 0–5 scale. Do not write
  per-level anchors into concept files — a source that does not state what "level 4 caching"
  looks like cannot support one, and inventing it is the failure this skill exists to prevent.

End every file with:

```markdown
## Sources

- **[S1]** <Title> — <URL or citation>
```

### 5. Extract level bars and probe seeds

Concept files say what is true. Two other artifacts say **what is expected** and **how to ask**
— and they are what `mock-design-interview` actually consumes. Extract them in the same pass,
under the same no-invention rule.

**Level bars.** If the source states what it expects at different seniority levels, add them to
`level-expectations.md`, preserving the source's own hedges verbatim — "with some prompting"
versus "without being prompted" is the load-bearing distinction, not a stylistic one. Sources
often bury this in a section that looks like framing.

**Probe seeds.** For each concept, if the source supports it, add a seed to
`probes/<source-tag>-<problem-class>.md` — the source tag from Inputs, and a kebab-case name
for the *class* of problem the source works through, not its example system. A source walking
through a URL shortener yields `s1-identifier-mapping.md`. One file per source and problem
class; for the canonical shape, including its header table and closing `## Sources` block, see
[s1-identifier-mapping](../../references/system-design-concerns/probes/s1-identifier-mapping.md).

```markdown
## P<n> — <short label>

- **Concern:** <concept file> — never spoken aloud
- **Symptom:** <an observable situation that does not name the concern>
- **Looking for:** <what a good answer contains> [Sn]
- **Bar:** <level, from the source's stated expectations> [Sn]
- **Follow-up if thin:** <where to push>
```

The seed is raw material, not a script — the interviewer generates wording live. Two rules:

- **The symptom must not name the concern.** "Reads are slow, the index is used, CPU is flat"
  is a probe. "Have you considered caching?" is the answer.
- **`Looking for` comes from a concept file, never from you.** If the source never explained the
  mechanism, there is nothing to check an answer against, so there is no seed.

Close the probe file with a `## Coverage note` section listing concerns the source does *not*
establish a bar for, and stating plainly that they must not be probed or scored. This is what
stops a later interviewer grading against an invented standard.

### 6. Update the library index

The library's `README.md` carries a **Concept index** and a **Sources processed** table. Both
must reflect this run, or the next run cannot tell what has already been mined:

- Add or update one **Concept index** row per concept touched, with three cells: a markdown link
  whose text is the concept name and whose target is `concepts/<concept>.md`, then
  `<Consider it when>`, then `<source tags>`. The middle column is the trigger condition — when a
  reader should reach for the file.
- Append one **Sources processed** row with four cells: `<tag>`, a markdown link whose text is the
  source title and whose target is its URL, then `<YYYY-MM>`, then `<concepts touched>`.
- Add the rejected candidates under a `### Rejected from <tag>` heading below that table, each
  with its reason. One heading per source — never merge this run's rejects into an earlier
  source's heading. If a heading already bears *this* run's tag, a previous run was interrupted:
  treat it as a resumption, reconcile its contents against what you found, and do not claim a
  new tag. This is what stops a future run re-litigating the same material.

### 7. Verify before reporting

Run these checks and fix anything they catch:

- **Citation coverage.** Every substantive claim has a tag. Untagged prose is either framing
  or contraband — decide which and act.
- **Traceability.** For every claim in every file you created or extended, name the inventory
  entry from step 1 that produced it. Any claim without one is invention: delete it. If more
  than one claim fails this check, re-verify the whole file rather than patching it — a leak
  that happened once happened by habit.
- **Invention sweep.** Re-read each file asking "which sentence in the source produced this?"
  Mechanisms, failure modes, and test techniques are the usual leak points — they are where
  general knowledge feels most obviously "correct" and is least likely to be in the source.
- **Tag resolution.** Every `[Sn]` resolves to a `## Sources` entry, and the run's own tag is
  the one you claimed from **Sources processed** — not one already in use.
- **Index consistency.** Every concept file appears in the library index and every index row
  points at a file that exists. A file missing from the index is invisible to future readers.
- **Cross-references resolve.** Any `<concept>.md` you reference exists.
- **No empty sections.** Delete any heading you could not fill from the source — except
  `## Not covered by sources` and `## Sources`, which stay.
- **Probe hygiene.** No seed's symptom names its own concern, and every `Looking for` traces to a
  cited claim in a concept file.
- **Naming.** No filename or heading names the source's example system.
- **Generality.** Each file states reasoning that would transfer to a different system, rather
  than summarizing this source's architecture.

### 8. Report the run

Report concisely, in this shape:

```markdown
**Source:** <title> — tag <Sn>

- **Created:** <concept> (<n> claims), <concept> (<n> claims)
- **Extended:** <concept> — gained <what>
- **Rejected:** <candidate> — <reason>
- **Disagreements:** <concept> — <source A> vs <source B>
- **Level bars / probes:** <n> bars, <n> seeds → <probe file>
- **Thinness:** <honest note, or "none">
```

The rejected line matters — it shows the bar was applied rather than everything being swept
in. If the source was introductory and yielded shallow files, say so plainly rather than
padding them.

## Anti-patterns

- **Rounding up a mention.** Treating "we cache this" as a caching concept.
- **Importing the canon.** Adding the standard list of cache invalidation strategies, or the
  standard consistency taxonomy, because it's what a good file "should" contain.
- **Sanding off the specifics.** Dropping a source's arithmetic or numbers loses the
  transferable method.
- **Copying the architecture.** Producing a summary of the source's solution instead of the
  concerns it illustrates.
- **Padding to look complete.** A three-claim file is an honest three-claim file.
