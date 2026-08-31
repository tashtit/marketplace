# Content-Addressed Identity

Deriving a record's identity from a hash of its content rather than from its name or its
uploader, so that identical content is recognizable as identical [S2].

## When it applies

- You need to answer "have I seen this exact content before?" — for deduplication, or to decide
  whether an interrupted transfer can be resumed [S2].
- The obvious handle, the name, is not unique: two users, or the same user twice, can supply
  different content under the same name [S2].

## Why it matters

Names are assigned; content is intrinsic. The source's term for the content-derived value is a
**fingerprint** — a hash computed over the content, often with a cryptographic function such as
SHA-256, serving as a unique identifier for the content regardless of its name or where it came
from [S2].

## Identity of the content is not identity of the record

The distinction the source draws is the load-bearing part: the fingerprint identifies the
*content*, not the *record*. Two different users uploading the same content produce the same
fingerprint, and they still need separate records [S2].

The resulting shape: the record keeps its own unique identifier — the source suggests a UUID —
and stores the fingerprint as a **separate field**, used for deduplication and resumability
checks rather than as the primary key [S2].

Compare `unique-identifier-generation.md`, which treats deterministic hashing of the *input* as
one option for minting the record's identifier itself. S2 keeps the two roles apart.

## Fingerprinting at more than one granularity

For resumable transfers, fingerprint each chunk as well as the whole payload [S2]:

- **The whole-payload fingerprint** answers "have I uploaded this before, and is there an
  in-progress transfer to resume?" [S2]
- **Per-chunk fingerprints** identify precisely which parts already made it across [S2].

The source's assembled flow makes the sequencing explicit: the client fingerprints the chunks and
the whole payload, asks the server whether that fingerprint already exists for this user, and if
it exists with an in-progress status, fetches the existing chunk statuses and resumes [S2]. See
`large-file-transfer.md`.

## Failure modes

- **Using the name as identity**, which collides across users and across a single user's own
  uploads [S2].
- **Treating the fingerprint as the record's primary key**, which cannot represent two users
  holding the same content [S2].

## Not covered by sources

- What to do on a fingerprint match across *different* users — whether the bytes are stored once
  and shared, and what that implies for deletion.
- Hash collision handling, or why a cryptographic hash is treated as collision-free here.
- The cost of fingerprinting a large payload on the client, and whether it is worth it for
  payloads that are unlikely to be duplicates.
- Whether the fingerprint is recomputed or trusted when the client reports it.

## Sources

- **[S2]** Hello Interview — Design a File Storage Service Like Dropbox —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/dropbox>
