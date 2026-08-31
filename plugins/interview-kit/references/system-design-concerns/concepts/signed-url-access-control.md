# Access Control for Direct Storage Access

Restricting who can reach a payload when the payload is served by a component that does not know
your users [S2].

## When it applies

- Clients transfer directly to or from a storage service or CDN, so your application server is
  not in the request path and cannot check permissions at fetch time [S2]. See
  `bypassing-the-application-server.md`.
- A link handed to an authorized user could be forwarded, posted publicly, or otherwise reach
  someone unauthorized [S2].

## The layers the source names

Three separate protections, addressing different threats [S2]:

1. **Encryption in transit**, so the payload cannot be read as it crosses the network [S2].
2. **Encryption at rest**, so possession of the stored bytes is not enough to read them — the
   storage service encrypts with a key held separately from the data [S2].
3. **Access control**, an explicit record of who may reach a given payload, consulted when a link
   is issued [S2].

Access control at issue time is the only one of the three that addresses an authorized user
leaking the link onward — and it does not, on its own [S2].

## Signed URLs, and what they actually guarantee

A signed URL carries a signature over the path, an expiry timestamp, and optionally further
restrictions; the serving component validates the signature and the expiry and refuses if either
fails [S2]. The signature is produced with the content provider's private key and verified with
the registered public key, which is why the CDN can enforce it without consulting your servers
[S2].

The property the source is careful to state: **a signed URL is a bearer token.** Anyone holding a
valid, unexpired URL can fetch the payload. A short expiry — the source's example is five minutes
— limits exposure; it does not prevent sharing [S2].

For higher-security cases the source names further restrictions: binding the URL to an IP
address, or requiring it to be used together with authentication cookies [S2].

## Failure modes

- **A leaked link fetched by an unauthorized party** within the validity window, because
  possession is sufficient [S2].
- **Treating a short expiry as prevention** rather than as exposure-limiting [S2].

## How to decide

Set the expiry to the shortest window the legitimate use actually needs, and add binding
restrictions when bearer semantics are not acceptable for the payload [S2].

## Not covered by sources

- How to choose the expiry window, beyond the five-minute example.
- How to revoke a signed URL before it expires.
- The usability cost of IP binding for clients behind changing addresses.
- Whether the access control list is consulted again on re-issue, or how revoked access
  interacts with URLs already handed out.

## Sources

- **[S2]** Hello Interview — Design a File Storage Service Like Dropbox —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/dropbox>
