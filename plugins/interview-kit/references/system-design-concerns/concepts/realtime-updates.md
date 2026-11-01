# Real-time Updates

## Solve both hops

- Design both the client connection and the route from the event producer to the server holding that connection. Choosing WebSockets alone leaves the second hop unanswered. [S12]
- Start with polling if its delay meets requirements. Poll frequency sets latency and aggregate query load: the source's example of a million clients polling every ten seconds creates 100,000 reads/second. [S12]

## Choose a client transport

- Long polling holds an HTTP request until an update or timeout, then reconnects. It is simple for infrequent updates but repeated request/response cycles add latency for closely spaced events; intermediary timeouts must agree. [S12]
- SSE streams one-way updates over HTTP and can pair with ordinary HTTP writes. Streaming support must extend through proxies; buffering can hide events until the response finishes. Event IDs support catching up across reconnects. [S12]
- WebSockets suit frequent bidirectional communication but introduce persistent connection state, reconnection, and deployment concerns. Verify intermediary support; a dedicated connection tier confines state while other services scale independently. [S12]
- Balance connection load and keep endpoint work lightweight. Existing long-lived connections constrain redistribution; deployments commonly close them and require clients to reconnect. [S12]
- WebRTC enables peer communication for media or other justified peer workloads. It requires signaling and NAT traversal via STUN/TURN and is more complex than ordinary server push. [S12]

## Route events to connections

- Database polling decouples producers and readers but costs queries even when no events arrive and tolerates delay. [S12]
- Deterministic ownership routes a user/entity to its connection server. Modulo hashing moves most assignments when membership changes; consistent hashing limits moved segments but still requires routing coordination and recovery of lost connection state. [S12]
- During ownership transitions, record old and new assignments, move connections gradually, and route updates to both until transition completes. This is useful when rebuilding entity state is expensive. [S12]
- Pub/sub lets any lightweight endpoint subscribe to relevant topics and forward updates through its local connections. This avoids fixed endpoint ownership, but the broker becomes a bottleneck/failure dependency and adds routing indirection. [S12]
- Sharded pub/sub adds many-to-many connections between brokers and endpoint servers. Least-connections balancing suits an endpoint tier mainly consuming resources per connection. [S12]

## Recovery and fan-out

- Heartbeats detect connections that appear alive after a failure. Track received updates and replay missed ones on reconnection with sequence references or per-user retained messages; reconnecting the socket alone is insufficient. [S12]
- For a shared popular update, cache once and distribute through regional or hierarchical nodes rather than writing independently to every recipient from one component. [S12]
- Related messages can be ordered through a single server or partition, trading some scalability for simpler ordering. The source mentions logical/vector clocks but does not develop their algorithms. [S12]

## Not covered by sources

- How long should disconnected clients retain a replay entitlement, and what happens after that window?
- How should topic authorization and subscription access be enforced?
- How do collaborative-editing conflict-resolution algorithms work?

## Sources

- **[S12]** Hello Interview — Real-time Updates — <https://www.hellointerview.com/learn/system-design/patterns/realtime-updates> (user-supplied saved HTML, processed 2026-11-01).
