# Inline review comments on a pull request

This reference gives a deterministic procedure for attaching review comments to
the correct lines of a pull request diff. It applies when the user asks for a
review that comments on specific lines, not merely for a commit or a plain
pull request.

Guessing line numbers from a raw diff produces off-by-one errors, because the
`@@` hunk header counts change with every hunk. Derive line numbers from the
diff itself instead.

## Step 1: Produce an annotated diff

Compute the new-file (right side) line number for every added and context line.
Write the script to a file and run it; inlining the `awk` program in a shell
one-liner breaks on quoting.

```bash
script="$(mktemp)"
cat > "$script" <<'ANNOTATE'
#!/usr/bin/env bash
set -euo pipefail
# Usage: annotate <pr-number-or-diff-command-output-on-stdin>
# Emits: <path> | line=<n> | <"+" added | " " context> <content>
awk '
/^diff --git/     { in_hunk = 0; file = "" }
/^\+\+\+ b\//      { file = substr($0, 7) }
/^@@ /            {
  split($3, a, ",")
  right = int(substr(a[1], 2))   # right = new-file start line of the hunk
  in_hunk = 1
  next
}
!in_hunk || file == "" { next }
/^\\/ || /^-/          { next }   # skip "No newline" markers and removed lines
{
  prefix = (substr($0, 1, 1) == "+") ? "+" : " "
  printf "%s | line=%-5d | %s %s\n", file, right, prefix, substr($0, 2)
  right++
}'
ANNOTATE
gh pr diff "$1" | bash "$script"
```

Example output:

```text
src/util.js | line=10    |   const a = 1;   (context)
src/util.js | line=11    | + const b = 2;   (added)
src/util.js | line=12    |   const c = 3;   (context)
```

Use only the `line` values from this output when addressing a line. A line that
never appears here is outside the diff; raise that point in the review body
instead of as an inline comment, because the host rejects inline comments on
lines it cannot map to the diff.

## Step 2: Build the review payload in a file

Write the whole review to a file and submit it once with `--input`. Do not
assemble nested fields with repeated `-f` flags; `side` must stay nested inside
each comment.

```bash
payload="$(mktemp)"
cat > "$payload" <<'REVIEW'
{
  "event": "COMMENT",
  "body": "Review summary.",
  "comments": [
    { "path": "src/util.js", "line": 11, "side": "RIGHT", "body": "Reason, then fix." }
  ]
}
REVIEW
gh api --method POST "repos/{owner}/{repo}/pulls/<number>/reviews" --input "$payload"
```

Comment fields:

| Field | Value |
| --- | --- |
| `path` | File path exactly as shown in the annotated diff |
| `line` | A `line` value from Step 1 (new-file/right side) |
| `side` | `"RIGHT"` for added or current content; `"LEFT"` only to comment on a removed line |
| `body` | Markdown; may contain a single-line suggestion block |

`event` MUST be exactly `APPROVE`, `REQUEST_CHANGES`, or `COMMENT`. Inflected
spellings such as `APPROVED` or `REQUEST_CHANGE` are rejected with an HTTP 422.

## Suggestions: single line only

A suggestion block replaces exactly the one line named by `line`. Explain the
change first, match the original indentation, and use one suggestion per
comment.

````markdown
Guard the empty case before iterating:

```suggestion
  if (items != null && !items.isEmpty()) {
```
````

Do not emit multi-line suggestions: applied suggestions replace only the target
line, so a multi-line block corrupts surrounding code. When a fix spans several
lines, describe it in prose and suggest at most the single most important line.

## Submit exactly once

Treat submission as non-idempotent. The reviews endpoint creates a new review on
every successful call, so a retry after a response that merely looked like a
failure produces duplicate comment threads.

- Submit the review once and read the response.
- Do not also post the same notes through the issue-comment or
  pull-request-comment endpoints; that duplicates them.
- If submission genuinely fails, correct the payload — most often an out-of-diff
  `line` or a malformed `event` — before resubmitting, rather than blindly
  retrying.

## Portability note

The field set above is the portable intersection. Some GitHub Enterprise Server
versions reject a `subject_type` field on review comments with an HTTP 422; omit
it unless a specific host is known to require it. Confirm current field support
against the [GitHub REST reference for pull request
reviews](https://docs.github.com/en/rest/pulls/reviews) for the target host.
