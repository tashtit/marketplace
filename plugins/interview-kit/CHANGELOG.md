# Changelog

## 0.1.0 - 2026-08-31

Initial release. Two skills and a cited concept library, extracted from a
personal practice repository and packaged so the library can be turned off.

- `mock-design-interview` interviews the candidate about one implementation they
  built and ends with a level assessment. Probes describe a symptom and never
  name the concern under test; thin answers get a follow-up rather than a nod. It
  refuses to interview code it helped write.
- `extract-design-concepts` is the library's only writer. One run mines one
  named source; every claim cites the source that stated it, gaps are recorded
  as unanswered questions, and sources that disagree are both recorded without
  adjudication.
- `interview-kit` routes between the two and states when the plugin should not
  be used at all.
- Bundles `references/system-design-concerns/` — 30 concept files, 5 probe files
  (S1–S5), level bars, and a 0–5 rubric. It carries no frontmatter and is not a
  skill: there is nothing to select, and both skills open it by path.

### Why this is a plugin

The library is the answer key for the interview, so reading it while building an
implementation invalidates the later assessment. Keeping it in the practice
repository made that unenforceable: a skill is advertised to the host's selector
by its description, and the strongest available wording is a description that
argues against its own selection — a request, not a mechanism. Successive
attempts to fix it in place (negative clauses in the description, removing broad
positive triggers, demoting the library from a skill to a plain directory) each
reduced the pressure without removing it, because the files still sat in the
repository being worked in.

Packaging it separately makes enablement the control surface: disabled during the
build, enabled for the interview.

### Writes go to a checkout, not to the install

`scripts/library-path.sh` resolves `read` and `write` to different paths. The
bundled library ships inside a host-managed install directory with no version
history, so an extraction run that wrote there would lose its work on the next
reinstall. `write` resolves a versioned checkout and **fails closed (exit 3)**
when there is none, rather than writing somewhere an upgrade would erase.

### Known limitations

- The prompted-versus-unprompted axis depends on a host session store and is
  verified only on GitHub Copilot CLI. Without one, the interview still assesses
  the design but reports that axis as unavailable instead of inferring it.
- Library coverage is exactly as broad as the five processed sources. Each
  concept file names its own gaps, and probe files close with a coverage note
  listing concerns that must not be scored.
