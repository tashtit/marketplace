# Client-Cached Responses

Choosing response semantics that determine whether clients cache a result, and understanding
what control you give up when they do [S1].

## When it applies

- A protocol offers more than one status code for the same outcome, differing only in whether
  clients are permitted to cache it — the source's case is permanent versus temporary redirects
  [S1].
- The underlying mapping may later be updated, expired, or deleted [S1].
- You need server-side visibility into every request, for example to record usage [S1].

## Why it matters

Client caching moves work off your servers, but it also removes your ability to change the
answer. A permanent response is typically cached by clients, meaning subsequent requests may go
straight to the target and bypass your server entirely [S1]. A temporary response is not
cached, ensuring future requests always come through your server first [S1].

That is the whole tradeoff: bypassing your server is a performance win and a control loss.

## Approaches and tradeoffs

**Permanent (cacheable) response.** Clients cache it and stop asking you. Fewer requests reach
your infrastructure, but you can no longer update, expire, or observe them [S1].

**Temporary (non-cacheable) response.** The source prefers this one for its case, with three
reasons that generalize [S1]:

- It gives more control over the operation, allowing entries to be updated or expired as
  needed.
- It prevents clients from caching, which would cause problems if the mapping needs to change or
  be deleted later.
- It allows per-request statistics to be tracked.

The decision rule the source implies: **if the mapping is mutable or expirable, do not let
clients cache it.** Mutability and client caching are in direct conflict [S1].

Either way the behavior is invisible to the user — the client follows the redirect
automatically and the user never knows it happened [S1].

## Method semantics

The source pairs this with conventional verb selection: creating a new resource uses POST,
reading an existing one uses GET, updating uses PUT, deleting uses DELETE [S1]. The reasoning
it applies is to match the verb to what actually happens to state — POST for creating a new
record, GET for reading an existing one [S1].

## Failure modes

- **Clients pinned to a stale target** after choosing a cacheable response for a mapping that
  later changes or expires [S1].
- **Loss of request-level observability**, since cached requests never reach the server [S1].
- **Inability to revoke**, because a cached response cannot be recalled from clients [S1].

## Not covered by sources

- How long clients actually cache a permanent response, or how to bound it.
- How to recover mappings already cached by clients when a change becomes necessary.
- Explicit cache-control directives as a middle ground between the two options.

## Sources

- **[S1]** Hello Interview — Design Bit.ly —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/bitly>
