# Unique Identifier Generation

Generating short, collision-free identifiers for records that users reference directly. The
design pulls against itself: uniqueness, shortness, and generation efficiency cannot all be
optimized simultaneously [S1].

## When it applies

- A system mints an identifier that users receive and share, where the identifier is the only
  handle for retrieving the record [S1].
- Three constraints hold at once: identifiers must be unique, as short as possible, and
  efficiently generated [S1].
- Users may optionally supply their own identifier (a custom alias), which must be validated
  as not already existing before use [S1].

## Why it matters

Uniqueness is a correctness requirement: each identifier must resolve to exactly one record.
The source demonstrates the failure concretely with an identifier derived from a prefix of the
input — any two inputs sharing their first N characters map to the same identifier, and on
lookup the system cannot know which of the countless matching records the caller wanted [S1].

## Approaches and tradeoffs

**Derive the identifier from a prefix of the input.** Presented by the source as the naive
option and rejected: it fails the uniqueness constraint outright [S1].

**Random number generation.** Does not provide enough entropy on its own to ensure identifiers
are unique [S1].

**Hash the input, encode it, and truncate.** Hash functions return a deterministic, fixed-size
output with high entropy, so the output appears random and is unlikely to collide for
different inputs [S1]. Encode the output compactly and take the first N characters, where N is
chosen to minimize collisions [S1].

- **Determinism cuts both ways.** The same input always maps to the same identifier without
  needing to query the database. That is desirable for deduplication and undesirable when you
  need multiple identifiers per input, or want to prevent guessability and adversarial
  preimages — for those cases add a secret salt or nonce [S1].
- **Canonicalize the input before hashing** — lowercase the host, strip default ports,
  normalize the trailing slash — so equivalent inputs hash consistently [S1].
- **Collisions remain possible and their likelihood grows with scale.** With a code space of
  size `|S|` and `n` identifiers already in use, the probability the next randomly generated
  identifier collides is `n / |S|`. At large scale this becomes non-negligible, requiring
  retries and database checks to enforce uniqueness [S1].
- **Lowering collision probability requires more entropy, which means longer identifiers**,
  which negates the benefit of being short. Detecting and resolving collisions also adds a
  database lookup on insertion, introducing latency and complexity [S1].

**Increment a counter and encode it.** Guarantees no collisions because every counter value is
unique, eliminating the risk without additional checks [S1]. Incrementing and encoding is
computationally efficient, supporting high throughput [S1]. The identifier can also be decoded
back to the original numeric id, which aids database lookups [S1].

- **It requires a single global counter**, which is challenging to maintain in a distributed
  environment due to synchronization — every service instance must agree on the counter value
  [S1]. See `shared-counter-coordination.md`.
- **Sequential counters produce predictable identifiers, making enumeration possible.** An
  attacker can iterate through them to discover every record. Mitigate with a reversible
  transformation such as XOR with a secret key before encoding, or accept the tradeoff when
  the identifiers are meant to be shared publicly anyway [S1].
- **Identifier length grows over time**, but slowly enough to be a non-issue at realistic
  scale: 1 billion values encodes to 6 characters, and 7 characters covers over 3.5 trillion
  [S1].

### Choosing the encoding alphabet

A 62-character alphabet (a–z, A–Z, 0–9) gives a compact representation of numbers. The source's
reason for preferring it over the more common 64-character variant is specific and worth
keeping: two of the latter's characters are unsafe in a URL, because the slash is a path
separator and the plus sign can be interpreted as a space in a query string [S1].

Sizing example from the source: 8 characters of a 62-symbol alphabet yields roughly 218
trillion possible identifiers [S1].

## Deduplication is a product decision, not just a storage one

You can check whether an input was already processed and return the existing identifier. But
the source notes most systems of this kind deliberately allow multiple identifiers for the same
input, because different users may want separate expiration dates, independent analytics, or
different custom aliases. Deduplication trades those features away for storage efficiency [S1].

S2 arrives at the same tension from the other side and separates the two roles: it keeps the
record's identifier unique per record and stores a content-derived fingerprint as a *separate*
field used only for deduplication and resumability, precisely because two users can hold the same
content and still need distinct records [S2]. See `content-addressed-identity.md`.

## Failure modes

- **Collision on insert**, with likelihood rising as the keyspace fills [S1].
- **Enumeration of the whole keyspace** when identifiers are sequential and predictable [S1].
- **A generated identifier colliding with a user-supplied custom alias.** Keep them from
  competing: prefix generated identifiers with a character custom aliases cannot use, or store
  the two in separate namespaces [S1].

## How to decide

- **Prefer the hash approach when** deduplication is wanted, or identifiers must resist
  guessing and a salt can be applied [S1].
- **Prefer the counter approach when** guaranteed uniqueness without collision-handling
  machinery matters more than unpredictability [S1].
- **Enforce uniqueness in the database regardless of the approach.** Put a UNIQUE constraint on
  the identifier column; on violation retry with a bounded number of attempts — the source
  suggests 3–5 — before falling back to a different strategy or returning an error [S1]. When
  retrying a hash, add a random salt [S1].

The database constraint is the safety net for uniqueness, independent of how identifiers are
generated [S1].

## Not covered by sources

- How to size the retry budget, or what to do when bounded retries are exhausted in production.
- Whether the reversible-transformation mitigation for predictability has drawbacks of its own.
- How to migrate identifiers already issued if the generation scheme changes.
- How to derive N (identifier length) from projected volume rather than by worked example.

## Sources

- **[S1]** Hello Interview — Design Bit.ly —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/bitly>
- **[S2]** Hello Interview — Design a File Storage Service Like Dropbox —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/dropbox>
