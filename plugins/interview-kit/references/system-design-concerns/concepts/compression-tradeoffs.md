# Compression as a Conditional Optimization

Trading CPU time for bytes on the wire, only where the trade actually pays [S2].

## When it applies

- Transfer size is a material cost in latency or bandwidth [S2].
- The payload's compressibility varies by type, so the answer is not the same for every payload
  [S2].

## Why it is conditional

Compression pays only when the time saved transferring fewer bytes exceeds the time spent
compressing and decompressing [S2]. That comparison depends on the payload, so the source's
conclusion is a runtime decision rather than a global setting: decide per payload based on type,
size, and network conditions [S2].

The type effect is large enough to be decisive [S2]:

- **Already-compressed media** — images, video — has a compression ratio so low it is not worth
  the time; the source's example is a PNG, where you would be lucky to shed a few percent [S2].
- **Text** compresses far better; the source's example is a 5GB text payload reducing to 1GB or
  less depending on content [S2].

## Where it runs

When the client transfers directly to storage, compression is entirely a client-side concern: the
client compresses before sending, the compressed bytes are stored as-is, and the client
decompresses after retrieving [S2]. This keeps the application server out of the data path while
still getting the smaller transfer [S2]. See `bypassing-the-application-server.md`.

## Choosing an algorithm

The source's comparison, with the property that drives each choice [S2]:

- **Gzip** — most widely used, broad support everywhere.
- **Brotli** — generally better ratios than Gzip, especially for text; supported by all modern
  browsers.
- **Zstandard** — compresses and decompresses significantly faster than Gzip at comparable
  ratios, and tunable across a range of speed/ratio tradeoffs.

Its recommendation is conditional on where compression runs: for client-side compression,
Zstandard is a strong choice because compression speed is the binding constraint — but the best
algorithm depends on the use case and what the client supports [S2].

## Ordering with encryption

**Always compress before encrypting.** Encryption introduces randomness, which makes the output
difficult to compress; compressing first achieves a much higher ratio [S2].

## Failure modes

- **Compressing incompressible payloads**, paying CPU on both ends for a few percent [S2].
- **Encrypting before compressing**, which destroys the compression ratio [S2].

## Not covered by sources

- How to measure network conditions on the client in order to make the decision.
- The size threshold below which compression is not worth attempting at all.
- Known attacks arising from compressing before encrypting.
- How to record which algorithm was used so the reader can decompress.

## Sources

- **[S2]** Hello Interview — Design a File Storage Service Like Dropbox —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/dropbox>
