# Probe Seeds — S2

Question seeds for the `mock-design-interview` skill. Each seed is raw material, **not a
script**: the interviewer generates the actual wording live from the seed plus the candidate's
repo and transcript.

## How to read a seed

| Field | Meaning |
| --- | --- |
| **Concern** | The concept being probed. **Never say this out loud.** |
| **Symptom** | The observable situation to describe to the candidate. |
| **Looking for** | What a good answer contains. Grounded in a concept file, never invented. |
| **Bar** | The level at which this is expected unprompted, per `level-expectations.md`. |
| **Follow-up if thin** | Where to push when the first answer is shallow. |

**The symptom is the question.** Describe what is observed and let the candidate name the cause.
The moment you name the concern, you have handed over the answer and the probe is spent.

---

## P1 — The payload crosses the network twice

- **Concern:** bypassing-the-application-server
- **Symptom:** "Your upload endpoint receives the bytes and then writes them to the object store.
  Egress costs are double what you modelled and p99 upload time is roughly twice the raw transfer
  time. What's going on?"
- **Looking for:** recognition that the payload is transferred twice — client to server, server
  to store — and that the fix is to let the client transfer directly to storage using a signed
  URL, leaving the server to write metadata and issue URLs [S2].
- **Bar:** senior unprompted. S2 explicitly does not expect a mid-level candidate to know about
  presigned URLs, but does expect them to reason to it when asked "You're uploading the file
  twice right now, how can we avoid that?" [S2].
- **Follow-up if thin:** "Trace one byte from the user's disk to the object store and count the
  hops." Then: "If the server never sees the bytes, how does it know the upload finished?"

## P2 — Metadata and payload disagree

- **Concern:** bypassing-the-application-server — the transactional gap
- **Symptom:** "You have rows in the metadata table with no object behind them, and objects in
  the store that nothing in the database references. Both happen at low rates. Where does that
  come from?"
- **Looking for:** that the transfer and the metadata write are two separate events that can each
  fail independently; the source's answer is a transactional approach — commit metadata only if
  the transfer succeeded and vice versa — implemented via a pending status set at URL-issue time
  and completed on the storage notification [S2].
- **Bar:** senior. S2 raises this as a challenge of the direct-transfer design [S2].
- **Follow-up if thin:** "Which of the two writes happens first, and what happens if the process
  dies between them?"

## P3 — One request, one hour

- **Concern:** large-file-transfer
- **Symptom:** "A user reports that uploading a large file fails after about a minute, every
  time, with no error from your application. Your API gateway is in front. Walk me through it."
- **Looking for:** the enumeration of why a single request cannot carry a large payload —
  timeouts, hard payload limits in managed components that cannot be raised, network
  interruptions, and no progress signal; and the arithmetic that makes it concrete
  (50GB at 100Mbps ≈ 1.11 hours) [S2].
- **Bar:** senior unprompted — S2 expects senior candidates to spend their time here and be
  proactive about it. Mid-level acceptable with the prompt "how would you show progress and let
  them resume?" [S2].
- **Follow-up if thin:** "Roughly how long does 50GB take on a 100Mbps connection? Do the math
  out loud." Then: "Which of the limits you named does raising the gateway's timeout actually
  fix?"

## P4 — Resuming an interrupted transfer

- **Concern:** large-file-transfer — chunk state
- **Symptom:** "The connection drops 40GB into a 50GB upload. The user reconnects. What does the
  client do first?"
- **Looking for:** per-chunk status persisted with the payload's metadata, so the client learns
  which chunks are already across and sends only the rest; and that chunking must happen on the
  client — chunking on the server defeats the purpose because the whole payload still has to
  arrive in one transfer [S2].
- **Bar:** senior. S2 names server-side chunking as a common mistake [S2].
- **Follow-up if thin:** "Where does the chunk state live, and who writes it?" Then: "Suppose you
  chunked on the server instead — what have you gained?"

## P5 — Identifying the same content twice

- **Concern:** content-addressed-identity
- **Symptom:** "Two users upload the same 2GB file, and the same user re-uploads a file they
  renamed. You want to recognize all three as the same content. What do you key on?"
- **Looking for:** that the name cannot serve as identity because it collides across and within
  users; a fingerprint — a hash over the content, e.g. SHA-256 — identifies the content
  regardless of name or origin [S2].
- **Bar:** senior.
- **Follow-up if thin:** "Two different users upload identical content. Same record or two
  records?" — looking for the split between the record's own identifier and the fingerprint as a
  separate field [S2].

## P6 — A one-byte edit resyncs the whole file

- **Concern:** large-file-transfer — content-defined chunking
- **Symptom:** "You added delta sync so only changed pieces move. A user inserts one character at
  the top of a 500MB log file and your system transfers all 500MB. Every piece hashes
  differently, and the hashing is correct. Why?"
- **Looking for:** fixed-size boundaries are anchored to byte offsets, so an insertion shifts
  every subsequent boundary and changes every downstream chunk's fingerprint; content-defined
  chunking derives boundaries from content via a rolling hash, so an edit affects only nearby
  chunks [S2].
- **Bar:** staff+ — S2 presents this as a subtlety worth calling out [S2].
- **Follow-up if thin:** "The hashes are all different but the bytes are almost all the same.
  What decides where one chunk ends?"

## P7 — Trusting the client's progress report

- **Concern:** client-authority-and-verification
- **Symptom:** "Your client PATCHes the backend after each chunk lands in the object store. A
  file is marked complete in your database but downloads are corrupt. No errors anywhere. How did
  you get here?"
- **Looking for:** the server does not observe the transfer, so a client report is an assertion;
  a client can mark chunks complete without transferring them, and the cost is inconsistent state
  that is hard to debug. The resolution is trust-but-verify — accept client updates for live
  progress, verify server-side (via part ETags and the store's parts listing) before marking the
  record complete [S2].
- **Bar:** staff+. S2 presents the client-orchestrated version as the merely-good solution and
  verification as the better one [S2].
- **Follow-up if thin:** "Who is the only party that actually knows whether that chunk landed?"
  Then: "Which pieces of that state can you afford to be wrong, and which can't you?"

## P8 — Files shared with me

- **Concern:** bidirectional-relationship-queries
- **Symptom:** "Listing a user's own files is instant. Listing files shared *with* them takes
  seconds and gets worse as the corpus grows. The share list is stored on each file record."
- **Looking for:** the embedded list is only indexable from the side that owns it, so the reverse
  query has to scan every record; the options are an inverse mapping kept in sync, or normalizing
  into a join table keyed by the pair, which removes the sync obligation at the cost of an index
  lookup instead of a key-value get [S2].
- **Bar:** senior.
- **Follow-up if thin:** "You cache the inverse mapping. What new obligation did you just take
  on?" — looking for the sync problem, and that keeping both in one transaction makes it a table
  rather than a cache [S2].

## P9 — A client that missed the notification

- **Concern:** propagating-changes-to-clients
- **Symptom:** "You push change events over a WebSocket. A user's laptop sleeps, wakes on a
  different network, and shows a stale file for hours until they restart the app. The socket
  reconnected fine."
- **Looking for:** persistent connections drop and messages get missed, so push alone cannot
  guarantee delivery; the hybrid is push for latency plus periodic polling (every few minutes) of
  a changes-since-timestamp endpoint as the safety net that makes the guarantee eventual
  consistency [S2].
- **Bar:** senior unprompted; staff+ to reach the hybrid without prompting.
- **Follow-up if thin:** "The socket reconnected. What did it miss while it was down, and how
  would it ever find out?" Then: "How many connections per device — one per file, or one total?"

## P10 — Two devices edited the same file

- **Concern:** propagating-changes-to-clients — conflict resolution
- **Symptom:** "The same file is edited on a phone and a laptop within the same minute, both
  offline, and both sync when they reconnect. What does the user end up with?"
- **Looking for:** last-write-wins as the stated strategy — the most recent edit is the one saved
  — and the accompanying caution that you would not overwrite the only copy: write a new copy or
  the new chunks and advance a version number and pointer on the metadata [S2].
- **Bar:** senior. Versioning itself is out of scope in S2, so **do not grade a full versioning
  design** [S2].
- **Follow-up if thin:** "Which edit survives, and what happened to the other one?"

## P11 — The download link got posted publicly

- **Concern:** signed-url-access-control
- **Symptom:** "An authorized user pastes their download link into a public forum. Your ACL
  check ran correctly when the link was issued. Strangers download the file. What's the gap?"
- **Looking for:** the permission check happens at issue time, but the CDN or store serves the
  request without consulting you; a signed URL carries a signature over path and expiry that the
  serving component validates itself — and it is a **bearer token**, so a short expiry limits
  exposure without preventing sharing. Stronger cases need IP binding or pairing with auth
  cookies [S2].
- **Bar:** staff+ for the bearer-token framing; senior for reaching signed URLs at all.
- **Follow-up if thin:** "Your ACL was right. Who checked it when the stranger clicked?" Then:
  "Does a five-minute expiry stop this, or just shrink it?"

## P12 — Compression made it slower

- **Concern:** compression-tradeoffs
- **Symptom:** "You turned on client-side compression for all uploads. Text files got much
  faster. Photo and video uploads got slower. Same code path."
- **Looking for:** compression pays only when time saved on the wire exceeds compress plus
  decompress time; already-compressed media has a ratio so low it is not worth it (a PNG might
  shed a few percent), while text can compress several-fold — so the decision belongs at runtime,
  on type, size, and network conditions [S2].
- **Bar:** staff+ — S2 raises this as a deep dive.
- **Follow-up if thin:** "Why would a JPEG behave differently from a log file here?" Then: "If
  you also encrypt, does the order matter?" — looking for compress-before-encrypt, since
  encryption's randomness destroys the ratio [S2].

## P13 — Which reads must see the latest write

- **Concern:** requirements-scoping — the consistency criterion
- **Symptom:** "You wrote 'strongly consistent' in your non-functional requirements. Talk me
  through what breaks if a user in another region sees this data three seconds late."
- **Looking for:** the criterion — prioritize consistency only if **every** read must receive the
  most recent write, otherwise the system breaks; contrasted with a case where seconds of
  staleness is merely a delay [S2].
- **Bar:** senior. S2 notes many candidates struggle with this tradeoff [S2].
- **Follow-up if thin:** "Give me a system where three seconds of staleness is a bug, and one
  where it isn't. What's the difference?"

---

## Coverage note

These seeds cover the concepts S2 developed for large-payload storage and sync. S2 places
**file editing, in-place viewing, per-user storage limits, file versioning, virus and malware
scanning, and the design of blob storage itself** explicitly out of scope [S2] — **do not probe
those**, and do not let a candidate's failure to mention them affect a score. P10 may surface
versioning; grade only the last-write-wins reasoning, not a versioning design.

S2 also says nothing about observability, rate limiting, idempotency, multi-region replication of
the metadata store, or how the push tier scales — no bar exists for them here. Add seeds only
when a source establishes the bar.

## Sources

- **[S2]** Hello Interview — Design a File Storage Service Like Dropbox —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/dropbox>
