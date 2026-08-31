# Keeping Bulk Data Off the Application Server

Letting clients transfer large payloads directly to and from storage, while the application
server only coordinates [S2].

## When it applies

- A payload passes through an application server on its way to or from a storage service,
  meaning it is transferred twice [S2].
- The same double transfer appears on the way back out: fetching from storage to the server, then
  from the server to the client [S2].

## Why it matters

The source's progression through three designs is the argument, and each step is driven by a
concrete defect rather than by preference [S2]:

1. **Store the payload on the application server's own disk.** Simple, and reasonable for a small
   application, but it does not scale and is not reliable: storage must grow with the data, and
   a server failure takes all payloads with it [S2].
2. **Server relays the payload to a storage service.** Fixes scale and durability — the storage
   service handles both — but the payload is now transferred twice, which is redundant [S2].
3. **Client transfers directly to storage using a signed URL.** Faster and cheaper, because the
   payload crosses the network once [S2].

The same reasoning applies in reverse for reads: relaying a download through the server is
"both slow and expensive" for the same reason [S2].

## The control plane / data plane split

Once the payload bypasses it, the application server's job is narrowed to coordination: it
writes metadata, issues signed URLs, and enforces permissions, while the bytes flow directly
between client and storage [S2].

One property makes this cheap: generating a signed URL is a purely local operation — the service
signs it cryptographically with its own credentials and makes no call to the storage service to
do so [S2].

## Approaches and tradeoffs

**Signed URL, then notification.** The client requests a URL and the server records metadata with
a pending status; the client transfers directly; the storage service notifies the server on
completion, and the server marks the metadata complete [S2].

The status field exists because the transfer and the metadata write are now two separate events
that can diverge — see the transactional problem below.

**Serve reads from a CDN rather than from storage directly.** A signed URL pointed at the
storage service is nearly optimal, but the storage lives in one region, so distant users see
higher latency; a CDN caches near the user and serves subsequent requests from the edge [S2].
The cost is real: CDNs are expensive, so be deliberate about what is cached and for how long, via
cache-control headers, and invalidate on update or delete [S2]. See `caching-the-read-path.md`.

## Failure modes

- **Payload transferred but metadata not saved, or metadata saved but payload never transferred.**
  The source names both directions and proposes a transactional approach — commit the metadata
  only if the transfer succeeded, and vice versa [S2].
- **Losing everything on a single server failure**, in the local-disk design [S2].
- **Paying twice for every byte**, in the relay design [S2].
- **Caching payloads at the edge that are rarely accessed**, wasting CDN spend [S2].

## How to decide

- **Move to a storage service when** the data volume grows with usage or a single server's
  failure would lose it [S2].
- **Bypass the application server when** the payload is large enough that relaying it is a
  material cost in time or money [S2].
- **Add a CDN when** the user base is geographically distributed and single-region latency is the
  remaining bottleneck [S2].

## Not covered by sources

- How to implement the "transactional approach" across a database and an external storage
  service, which do not share a transaction.
- How to reconcile metadata whose transfer never completed and never will.
- What cache-control lifetime to choose, or how to decide which payloads are worth caching.
- Whether the completion notification can be lost, and what recovers the metadata if it is.

## Sources

- **[S2]** Hello Interview — Design a File Storage Service Like Dropbox —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/dropbox>
