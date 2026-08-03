---
name: production-snippets
description: Design, implement, or review production reference implementations for Redis and cache lifecycle, retry with backoff and idempotency, cache-aside and stampede protection, database and HTTP client connection management, and health checks with graceful shutdown and readiness. Use when adding or reviewing connection setup, pooling, timeouts, TLS, retries, invalidation, or process lifecycle, or when a request asks for a copy-paste snippet that omits cleanup, timeouts, transport security, or failure handling.
---

# Production Snippets

Provide reference implementations, not paste-only fragments. A snippet enters a
long-lived system, so it MUST fail predictably, release every resource, protect
its transport and credentials, and be observable and testable. Apply repository
policy and any legal, privacy, or regulatory requirement first. Treat this skill
as a vendor-neutral baseline, not a compliance certification.

Use `MUST`, `SHOULD`, and `MAY` to distinguish requirements, strong defaults,
and optional practices. Examples are illustrative pseudocode; map them to the
project language, library, and runtime rather than mandating a specific SDK.
Never include real secrets, endpoints, or credentials — use named placeholders
such as `${REDIS_URL}` or a configuration provider.

## Reference implementation contract

Every snippet you produce or approve MUST document all seven dimensions. State
them explicitly; do not assume the reader will infer them.

1. **Supported versions.** Name the language, runtime, and library versions the
   code targets, and call out any version-specific behavior (for example a pool
   default or a TLS flag that changed).
2. **Failure behavior.** State what happens on timeout, connection loss,
   partial write, or dependency outage, and which layer owns the final failure.
3. **Resource cleanup.** Guarantee release of connections, sockets, file
   handles, timers, and background tasks on every path, including error and
   cancellation paths.
4. **Security.** Require transport security (TLS) where the channel leaves the
   host, authenticate the peer, keep credentials out of code and logs, and
   validate untrusted input.
5. **Observability.** Expose the signals an operator needs: bounded structured
   events, metrics (latency, errors, pool saturation), and health status.
   Never log secrets or payloads.
6. **Tests.** Describe how the behavior is verified, including the failure paths
   (timeout, exhausted pool, retry exhaustion, shutdown mid-request).
7. **Operational tradeoffs.** State the tuning knobs and their cost: pool size
   versus memory and peer limits, timeout versus tail latency, retry budget
   versus load amplification, cache TTL versus staleness.

A snippet that omits any dimension is incomplete. If a request asks for a
paste-only fragment without these, harden it and explain what you added rather
than emitting the unsafe version.

## Redis connection lifecycle, pooling, timeouts, and TLS

Create one shared, long-lived client or pool per process; do not open a
connection per operation. The pool MUST bound its size, acquire timeout, and
idle lifetime, and MUST be closed on shutdown.

- **Connect timeout, command timeout, and pool-acquire timeout MUST all be
  set.** An unbounded wait turns a slow dependency into a stalled process.
- **Enable TLS when the connection leaves the host** and verify the server
  certificate; authenticate with a credential from configuration, never a
  literal. Disabling certificate verification is prohibited outside an isolated
  test.
- **Release every connection back to the pool**, including on error and
  cancellation. Use the language's scoped-cleanup construct.
- **Expose health and saturation:** a bounded ping for readiness, and metrics
  for in-use versus idle connections and acquire wait time.

```text
# Supported: illustrative; pin your client's major version and note pool defaults.
config:
  url: ${REDIS_URL}            # rediss:// selects TLS; credentials come from config
  tls: { verify: true, ca: ${REDIS_CA_FILE} }
  pool: { max: 20, acquire_timeout: 500ms, idle_ttl: 60s }
  connect_timeout: 1s
  command_timeout: 250ms

client = create_pool(config)   # created once at startup, shared across the process

function get_user(id):
  with client.acquire() as conn:        # cleanup: released on every path
    return conn.get("user:" + id)       # command_timeout bounds this call
  # on acquire timeout -> typed PoolExhausted error, owned by the caller
  # on command timeout -> typed Timeout error; do not retry a non-idempotent write here

on_shutdown:
  client.close()                        # drains and closes pooled connections
```

- **Failure behavior:** acquire timeout raises a typed pool-exhaustion error;
  command timeout raises a typed timeout; the calling layer decides fallback.
- **Observability:** emit acquire-wait and command-latency metrics and a
  bounded readiness ping; never log the key values or credentials.
- **Tests:** cover pool exhaustion, command timeout, TLS handshake failure, and
  clean shutdown while requests are in flight.
- **Tradeoffs:** larger `max` improves concurrency but consumes memory and peer
  connection slots; tighter `command_timeout` sheds load faster but fails more
  borderline requests.

## Retry, exponential backoff, jitter, and idempotency

Retry only when it is safe and useful. A retry that repeats a non-idempotent
side effect can double-charge, double-send, or corrupt state.

- **Retry only idempotent operations,** or make the operation idempotent with a
  caller-supplied idempotency key that the server deduplicates.
- **Use a bounded retry budget** (max attempts and a max total elapsed time),
  **exponential backoff, and full jitter** to avoid synchronized retry storms.
- **Retry only transient, retryable failures** (timeouts, connection resets,
  `429`/`503` with honored `Retry-After`). Never retry validation, auth, or
  `4xx` client errors except an explicit rate-limit signal.
- **Own the final failure once:** emit one exhaustion event with the attempt
  count; do not log an indistinguishable error per attempt.

```text
# Supported: illustrative; note that jitter and Retry-After handling are library-specific.
function with_retry(op, key):
  attempt = 0
  deadline = now() + max_elapsed(10s)
  while true:
    try:
      return op(idempotency_key = key)          # server dedupes replays of key
    except err:
      attempt += 1
      if not is_retryable(err) or attempt >= max_attempts(4) or now() >= deadline:
        raise Exhausted(cause = err, attempts = attempt)   # single final failure
      sleep(full_jitter(base = 100ms, cap = 2s, attempt = attempt))
```

- **Failure behavior:** on exhaustion the caller receives one typed `Exhausted`
  error carrying attempt count and the last cause.
- **Resource cleanup:** each attempt acquires and releases its own connection or
  request; a cancelled outer call stops further attempts.
- **Security:** the idempotency key MUST be unguessable and scoped to the
  caller; never log it or the payload.
- **Observability:** count attempts, retries, and exhaustions; record final
  outcome and total elapsed time.
- **Tests:** transient-then-success, non-retryable-first-attempt,
  budget-exhaustion, and idempotent replay returning the original result.
- **Tradeoffs:** a larger budget hides more transient faults but amplifies load
  during an outage; more jitter smooths load but widens latency variance.

## Cache-aside, stampede protection, and invalidation

Cache-aside keeps the datastore authoritative: read cache, on miss read the
source, then populate the cache. Guard the miss path against stampedes and keep
invalidation explicit.

- **Set a TTL on every entry** so a missed invalidation cannot serve stale data
  forever. Add small per-key jitter to the TTL to avoid synchronized expiry.
- **Protect the miss path from stampedes** with a per-key lock or
  single-flight, so one loader repopulates while others wait or serve a slightly
  stale value.
- **Invalidate on write.** Prefer delete-on-write over write-through unless the
  value is cheap and consistent to recompute; a delete is safe to repeat.
- **Never cache secrets or per-user authorization decisions** under a shared
  key, and namespace keys to prevent collisions.

```text
# Supported: illustrative; single-flight primitives differ by language.
function read(id):
  hit = cache.get(key(id))                 # command_timeout applies
  if hit is not MISS: return hit
  return single_flight(key(id), loader = function():
    value = source.load(id)                # authoritative datastore
    cache.set(key(id), value, ttl = jittered(300s))
    return value)

function write(id, value):
  source.save(id, value)                   # datastore is source of truth
  cache.delete(key(id))                     # idempotent invalidation
```

- **Failure behavior:** a cache outage MUST degrade to the source, not fail the
  request; a loader failure is not cached (avoid negative-cache poisoning unless
  a short, explicit negative TTL is chosen).
- **Resource cleanup:** the single-flight lock is released on both success and
  error; no waiter is left blocked.
- **Observability:** track hit rate, miss rate, loader latency, and
  stampede-lock waits.
- **Tests:** hit, miss-populate, concurrent-miss single-flight, write-then-read
  invalidation, and cache-down fallback.
- **Tradeoffs:** longer TTL raises hit rate but increases staleness;
  delete-on-write is simple but adds a miss after every write.

## Database and HTTP client connection management

Reuse a single configured pool or client per process. Per-request creation
exhausts sockets, skips connection reuse, and leaks handles under load.

- **Bound the pool** (max connections, acquire timeout, max lifetime) and set
  **connect, statement/read, and total timeouts.** For HTTP, cap connections
  per host and total, and set a request deadline.
- **Return connections deterministically** with scoped cleanup; run
  multi-statement work inside an explicit transaction that commits or rolls back
  on every path.
- **Use TLS and verify the peer** for any network hop off-host; keep the DSN and
  tokens in configuration or a secret manager, never in code or logs.
- **Health-check the pool** with a cheap bounded query or request for readiness.

```text
# Supported: illustrative; pin your driver/client and note its pool defaults.
db = create_db_pool(dsn = ${DATABASE_URL}, max = 10, acquire_timeout = 1s,
                    max_lifetime = 30m, statement_timeout = 2s, tls = verify)

function transfer(a, b, amount):
  with db.begin() as tx:              # cleanup: commit on success, rollback on error
    tx.exec("update accounts set bal = bal - $1 where id = $2", amount, a)
    tx.exec("update accounts set bal = bal + $1 where id = $2", amount, b)

http = create_http_client(connect_timeout = 1s, request_timeout = 3s,
                         max_conns_per_host = 20, tls = verify)  # shared, reused
on_shutdown: db.close(); http.close()
```

- **Failure behavior:** acquire and statement timeouts raise typed errors; a
  transaction rolls back atomically; the caller decides retry (idempotent only).
- **Observability:** pool in-use/idle, acquire wait, query and request latency,
  and error rates by class.
- **Tests:** pool exhaustion, statement timeout, transaction rollback, TLS
  verification failure, and shutdown draining in-flight work.
- **Tradeoffs:** a small pool protects the database but queues requests; a large
  pool improves throughput until the database becomes the bottleneck.

## Health checks, graceful shutdown, and readiness

Separate liveness from readiness and drain in-flight work on shutdown. A process
that reports ready while its dependencies are down sends traffic into failure.

- **Liveness** answers "is the process healthy enough to keep running"; keep it
  cheap and dependency-free so a slow dependency does not trigger a restart
  loop.
- **Readiness** answers "can it serve now" and MAY check bounded dependency
  health (a short pool ping). A failing readiness check MUST remove the instance
  from rotation without killing it.
- **On shutdown:** stop accepting new work, fail readiness, finish or time-box
  in-flight requests, then close pools, clients, timers, and background tasks.
- **Bound every check and the drain window** so shutdown cannot hang; escalate
  to a forced stop after the deadline.

```text
# Supported: illustrative; signal handling and probe wiring are platform-specific.
liveness():  return OK                       # no external dependency
readiness(): return db.ping(timeout=200ms) and cache.ping(timeout=200ms)

on_signal(TERM):
  server.stop_accepting()                    # readiness now fails; LB drains us
  server.await_inflight(timeout = 25s)       # bounded drain
  db.close(); http.close(); cache.close()    # cleanup of every resource
  cancel_background_tasks()
```

- **Failure behavior:** if drain exceeds the deadline, force-close and log the
  count of abandoned requests; never block shutdown indefinitely.
- **Security:** health endpoints MUST NOT expose secrets, versions, or internal
  topology to unauthenticated callers.
- **Observability:** expose readiness state transitions and drain duration;
  alert on repeated readiness flaps.
- **Tests:** signal-triggered drain with in-flight requests, readiness-fails
  path, and drain-timeout force-close.
- **Tradeoffs:** a longer drain window loses fewer requests but slows deploys
  and scale-in; probing dependencies in readiness is accurate but can cause
  correlated instance removal during a shared outage.

## Non-goals

This skill does not mandate a programming language, runtime, client library,
cache or database product, or deployment platform, and it makes no compliance
certification claim. It does not provide copy-paste fragments to ship
unmodified; every example MUST be adapted and completed against the seven
required dimensions.

Read [references/examples.md](references/examples.md) for fuller worked
reference implementations that demonstrate all seven required dimensions.
