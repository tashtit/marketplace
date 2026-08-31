# Delegating a Sensitive External Operation

When an external provider performs an operation on your behalf — the source's case is payment —
the boundary decisions are what your servers are allowed to see and how you tolerate the
provider's retries [S3].

## When it applies

- A third party performs the operation, and your system's state must be updated based on its
  outcome [S3].
- The provider reports the outcome asynchronously by calling back into your system, rather than in
  the response to your request [S3].
- The data involved carries a compliance obligation [S3].

## Keep the sensitive data out of your servers

The client tokenizes the sensitive input using the provider's own client-side library, so your
server never receives the raw value — it receives only a token, which it forwards along with your
internal identifier [S3]. The source states this is standard practice for the relevant compliance
regime [S3]. The general shape: the provider's client library and the provider are the only parties
that see the sensitive data, and your system handles a reference to it.

## Make the callback handler idempotent

The provider can retry callbacks on failure, so the same event may be delivered more than once, and
processing it twice must not produce duplicate state changes [S3]. The source's method [S3]:

- Embed your own identifier in the metadata you send the provider, and read it back out of the
  callback.
- Use that identifier as the **idempotency key**.
- **Check the current status of the record before updating it**, which is what makes the retry
  safe.

The generalizable rule: any handler for a callback you do not control is an at-least-once handler,
so it needs a key and a status check, not just a write.

## Commit the resulting state changes together

The source's callback updates two tables in one database transaction — marking the item sold and
the enclosing order confirmed — so the outcome is recorded atomically rather than leaving the two
records able to disagree [S3].

## When the external operation is a read, not a write

S4 delegates a *computation* rather than a state change: an external service estimates travel time,
including live conditions its own system has no access to [S4]. Two boundary decisions differ from
the callback case:

- **The call is synchronous and on the critical read path**, so its cost is per-request rather than
  per-event. That is what makes the number of calls the design problem — S4's rejected approach fails
  precisely by querying the external service once per candidate [S4]. See
  `proximity-candidate-filtering.md` for the two-stage filter that bounds the fan-out.
- **Local data can shrink the delegated work.** S4 keeps its own copy of the slow-changing candidate
  set and uses cheap local arithmetic to prune before delegating [S4]. The external service is
  consulted only where its answer is actually in doubt.

The transferable rule: when you delegate a per-request computation, the cost is proportional to how
much you ask, so the design work is reducing the question before you ask it.

## Failure modes

- **Duplicate state changes** from a retried callback with no idempotency key [S3].
- **Sensitive data landing in your infrastructure** when the client posts it to your server
  instead of tokenizing it [S3].
- **A successful external operation with no corresponding internal state**, which the source
  handles in the specific case of a lapsed hold by issuing an automatic refund — see
  `preventing-double-allocation.md` [S3].
- **Overwhelming a synchronous external dependency** by delegating for every candidate rather than
  only the plausible ones [S4].

## Not covered by sources

- What happens if the callback never arrives at all, and whether the outcome is polled as a
  fallback.
- How long to retain idempotency keys.
- How to authenticate that the callback genuinely came from the provider.
- How to reconcile your records against the provider's periodically.
- What to do when a synchronous external dependency on the read path is slow, down, or throttling;
  S4 names no fallback or timeout behaviour.
- Whether the external computation's results can be cached, and for how long, given that the
  conditions feeding it change.

## Sources

- **[S3]** Hello Interview — Design Ticketmaster —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster>
- **[S4]** Hello Interview — Design a Local Delivery Service like Gopuff —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/gopuff>
