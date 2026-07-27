# Commit message standard

Tashtit defaults to [Conventional Commits
1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) when a repository does
not define another convention.

Use:

```text
type(optional-scope): imperative summary

optional rationale and material context

optional trailers
```

Choose the narrowest accurate type:

- `feat`: user-visible capability;
- `fix`: defect correction;
- `docs`: documentation only;
- `test`: tests only;
- `refactor`: behavior-preserving code structure;
- `perf`: performance improvement;
- `build`: build system or dependencies;
- `ci`: continuous integration;
- `chore`: maintenance not covered above;
- `revert`: revert of an earlier commit.

Keep the summary specific and omit a final period. Add `!` and a
`BREAKING CHANGE:` trailer only for a real incompatible change. Explain why in
the body when the diff does not make the reason obvious.
