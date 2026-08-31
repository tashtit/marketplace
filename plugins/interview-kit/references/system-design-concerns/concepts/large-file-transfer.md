# Large File Transfer

Moving a payload too large to survive a single request, by splitting it into independently
transferable pieces [S2].

## When it applies

- A single request would carry a payload large enough to hit a timeout, a size limit, or a
  network interruption [S2].
- The user needs to see progress, or to resume after a failure rather than restart [S2].

## Why a single request fails

The source enumerates four distinct limits, and they fail for different reasons — worth keeping
separate, because fixing one does not fix the others [S2]:

- **Timeouts.** Servers and clients set timeouts to avoid waiting indefinitely; a large transfer
  can exceed them [S2].
- **Payload limits.** Browsers and servers cap request body size. Raw web servers can be
  reconfigured, but managed services often have hard limits that cannot be raised — the source's
  example is a 10MB cap on a managed API gateway [S2].
- **Network interruptions.** The larger the payload, the likelier an interruption, and without
  resumption the whole transfer restarts [S2].
- **No progress signal.** The user cannot tell whether the transfer is working or how long it
  will take [S2].

The transfer-time arithmetic is what makes the scale of the problem concrete: 50GB over a
100Mbps connection is `50GB × 8 bits/byte / 100Mbps = 4000 seconds ≈ 1.11 hours` [S2]. See
`capacity-estimation.md`.

## Approaches and tradeoffs

**Chunk on the client.** Split the payload into pieces — the source uses 5–10MB, adjustable for
network conditions and payload size — and transfer them one at a time or in parallel [S2].

- **Chunking must happen on the client.** The source names chunking on the server as a common
  mistake: it defeats the purpose, because the whole payload still has to reach the server in
  one transfer first [S2].
- **Progress falls out of chunking.** Track completed chunks and report the fraction done [S2].
- **Parallelism uses the available bandwidth.** Bandwidth is fixed, but sending chunks in
  parallel and adapting chunk size to network conditions makes fuller use of it [S2].

**Track chunk state to resume.** Persist per-chunk status alongside the payload's metadata, so a
resumed transfer sends only the missing chunks instead of starting over [S2]. Keeping that state
honest is its own problem — see `client-authority-and-verification.md`.

**Use the storage provider's multipart API.** The source notes this is a solved problem: object
stores expose a multipart upload that does the same thing — initiate, transfer parts, then a
completion call that assembles them — and only mark the payload complete after the store
confirms assembly [S2].

Two operational consequences the source calls out [S2]:

- Completion events fire only when the whole multipart transfer is assembled, not per part, so
  per-part progress requires querying the parts listing separately.
- Knowing the API exists is not a substitute for being able to explain the mechanism.

## Chunking for downloads and for sync

**Downloads do not need the same chunking.** Once the parts are assembled, the stored object is a
single object; the client fetches it normally, and the original chunk boundaries are invisible to
it. For very large payloads, HTTP range requests already allow parallel or resumed downloads
without any application-level chunk scheme [S2].

**Sync does reuse chunking.** When a payload changes, transferring only the changed chunks rather
than the whole payload makes synchronization much faster [S2].

## Fixed-size chunking breaks delta sync

Fixed-size boundaries are anchored to byte offsets, so inserting a single byte near the start
shifts every subsequent boundary and changes the fingerprint of every chunk after the edit —
making delta sync nearly useless [S2].

The fix is **content-defined chunking**: derive boundaries from the content itself using a
rolling hash, so a small edit affects only the chunks immediately around it and the rest stay
identical [S2]. See `content-addressed-identity.md`.

## Failure modes

- **Restarting a long transfer from zero** after an interruption, when no chunk state is kept
  [S2].
- **Chunking on the server**, which leaves the original single-request limits in place [S2].
- **A hard payload limit in a managed component** that no configuration can raise [S2].
- **Delta sync degenerating to full transfer** when fixed-size chunking is used and an edit
  shifts boundaries [S2].

## How to decide

- **Chunk when** the payload can exceed a request limit or timeout, or when resumption and
  progress are requirements [S2].
- **Prefer the storage provider's multipart primitive** over a hand-rolled scheme, while
  understanding the mechanism well enough to implement it [S2].
- **Choose content-defined boundaries when** the payload will be edited and re-synced; fixed-size
  boundaries are adequate only for write-once payloads [S2].

## Not covered by sources

- How to pick a chunk size for a given network, beyond the 5–10MB range and "adapt to
  conditions".
- How many chunks to transfer in parallel, or how to detect the point of diminishing return.
- What to do with the storage cost of an abandoned partial transfer that is never resumed.
- How long resumable state should remain valid before the partial transfer is discarded.
- Rolling-hash parameter choice, or the average chunk size content-defined chunking should
  target.

## Sources

- **[S2]** Hello Interview — Design a File Storage Service Like Dropbox —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/dropbox>
