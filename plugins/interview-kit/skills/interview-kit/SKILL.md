---
name: interview-kit
description: Route a request to the right interview-kit tool — conduct a mock system design interview about an implementation the user already built, or mine one named source document into the cited concept library that grades those interviews. Invoke only on an explicit request to be interviewed about a design, or to ingest a source into the library. Never invoke it to design, write, review, or debug code, and never in a session that is building the implementation an interview would later assess — this plugin is the answer key, so reading it during the build invalidates the assessment.
---

# Interview Kit

Two tools and the cited library between them. The library is the answer key for
the interview, which is why **the whole plugin is meant to be enabled only after
an implementation is finished** — see [When not to use this plugin](#when-not-to-use-this-plugin).

```text
extract-design-concepts  ──writes──▶  system-design-concerns  ──reads──▶  mock-design-interview
     (one source in)                 (the library — plain data)         (interviews one attempt)
```

## Choosing a skill

| The user wants to… | Use | Writes |
| --- | --- | --- |
| Be interviewed, grilled, or assessed on something they built | `mock-design-interview` | Nothing |
| Add, ingest, distill, or mine a named source into the library | `extract-design-concepts` | The library |

Both trigger directly on their own descriptions, so an explicit request reaches
them without this router. Route here only when the intent is general ("help me
practice system design") and hand off once it is clear.

## When not to use this plugin

**Not while an implementation is being built.** The library records the concerns
an implementation is later interviewed and graded against, and `probes/` is
literally the question list. Work built while consulting it scores well on
concerns it was handed, which measures the library rather than the person, so the
resulting assessment is worthless. Keep the plugin disabled during the build and
enable it for the interview.

Also not for: designing, writing, reviewing, or debugging code; answering a design
question; or supplying background context because a task involves a cache, an ID
scheme, or a read path. The library existing is never a reason to recommend
infrastructure — several of its own sources make the opposite point, that at low
volume the simple thing is correct.

If a request arrives that is really one of those, say what this plugin is for and
stop. Do not open `references/system-design-concerns/` to answer it.

## The library

Bundled at `references/system-design-concerns/`, cited claim by claim. It is
**data, not a skill**: no frontmatter, nothing to select, opened by path only by
the two skills above.

Resolve its path with `scripts/library-path.sh`, which distinguishes two cases
that are easy to conflate:

- `library-path.sh read` — the bundled copy. Always correct to read.
- `library-path.sh write` — a versioned checkout. The bundled copy sits in a
  managed install directory with no history, so a reinstall discards anything
  written there; the script fails closed rather than write somewhere that a
  later upgrade would silently erase.

Only `extract-design-concepts` writes, and only with a cited source.
