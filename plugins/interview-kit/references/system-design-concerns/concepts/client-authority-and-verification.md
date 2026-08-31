# Client-Reported State and Verification

Deciding how much to trust a client's report about work it performed out of the server's sight
[S2].

## When it applies

- The client interacts directly with a third component, so the server does not observe the work
  itself and learns about it only from the client's report [S2].
- The server keeps state that is supposed to mirror that work — progress, completion status, a
  count of finished parts [S2].

## Why it matters

Bypassing the server for the actual work is what created the gap: the server has no first-hand
evidence, so a client report is an assertion, not an observation. See
`bypassing-the-application-server.md`.

The source's concrete case: a malicious user marks every part complete without transferring
anything. The blast radius is narrow — they corrupt only their own record, not anyone else's —
but the result is an inconsistent state that is difficult to debug [S2]. That framing is worth
keeping: the argument for verification here is debuggability and integrity, not containment of a
cross-tenant attack.

## Approaches and tradeoffs

**Trust the client's report.** The client tells the server what completed and the server records
it. Simple and immediate, but the server's state is only as honest as the client [S2].

**Verify against the third component.** Have the client include a token the third component
issued for each completed piece — the source uses ETags from the storage service — and have the
server confirm them by querying that component's parts listing, which validates many at once
[S2].

**Trust but verify.** The source's stated resolution: accept client updates for real-time
progress so the user gets immediate feedback, and verify server-side before marking the record
complete [S2]. The split is by consequence — an unverified progress bar is cosmetic, an
unverified completion flag is corruption.

A constraint shapes the mechanism: the storage service's completion events fire only for the
assembled whole, not for individual parts, so there is no server-observable per-part event to
rely on and the parts listing has to be polled instead [S2].

## Failure modes

- **A client marking work complete that never happened**, leaving a record that cannot be read
  back [S2].
- **Inconsistent state that is difficult to debug**, which the source names as the real cost
  [S2].

## How to decide

Verify at the point where wrong state becomes durable damage, and accept unverified reports for
state that is only informational [S2].

## Not covered by sources

- How often the periodic server-side verification should run.
- What to do when verification finds a mismatch — whether the transfer is failed, retried, or
  reconciled.
- Whether the same trust boundary applies to other client-reported values, such as the content
  fingerprint.

## Sources

- **[S2]** Hello Interview — Design a File Storage Service Like Dropbox —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/dropbox>
