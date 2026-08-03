# Worked examples

These examples expand the SKILL sections into fuller reference implementations.
They remain language-illustrative pseudocode: map each construct to your
language's real client, scoped-cleanup, and concurrency primitives. Every value
that would be a secret or an endpoint is a named placeholder. None of these are
paste-only fragments; complete the seven required dimensions for your context
before shipping.

## Resilient Redis read-through with all seven dimensions

```text
# 1. Supported versions
#    - Illustrative. Pin the client major version and record the pool defaults
#      it applies (max size, idle eviction) so an upgrade is a reviewed change.
#    - `rediss://` (double s) selects TLS; confirm your client parses it.

config = {
  url:             ${REDIS_URL},          # rediss://host:port, no credentials inline
  username:        ${REDIS_USERNAME},     # from config/secret manager
  password:        ${REDIS_PASSWORD},     # from config/secret manager
  tls:             { verify: true, ca: ${REDIS_CA_FILE} },   # 4. security
  connect_timeout: 1s,
  command_timeout: 250ms,
  pool:            { max: 20, acquire_timeout: 500ms, idle_ttl: 60s },
}

pool = create_pool(config)                # created once at startup, shared

metrics.gauge("redis.pool.in_use", pool.in_use)     # 5. observability
metrics.gauge("redis.pool.idle",   pool.idle)

function read_through(id):
  start = now()
  try:
    with pool.acquire(timeout = config.pool.acquire_timeout) as conn:  # 3. cleanup
      cached = conn.get("user:" + id)      # bounded by command_timeout
      if cached is not MISS:
        metrics.count("redis.hit"); return decode(cached)
      metrics.count("redis.miss")
      value = source.load(id)              # authoritative datastore
      conn.setex("user:" + id, ttl = jittered(300s), encode(value))
      return value
  except PoolExhausted as e:               # 2. failure behavior: typed, owned by caller
    metrics.count("redis.pool_exhausted")
    return source.load(id)                 # degrade to source, do not fail the request
  except Timeout as e:
    metrics.count("redis.timeout")
    return source.load(id)                 # cache is optional, source is required
  finally:
    metrics.histogram("redis.read.latency", now() - start)

on_shutdown:
  pool.close()                             # 3. cleanup: drain and close pooled sockets
```

- **Failure behavior:** pool exhaustion and command timeout are typed and
  degrade to the source; a cache outage never fails a request that the datastore
  can still serve.
- **Resource cleanup:** the scoped `with` releases the connection on hit, miss,
  and error; `pool.close()` runs on shutdown.
- **Security:** TLS with verification, credentials from configuration, and no
  key value or credential in logs or metrics labels.
- **Observability:** hit/miss/timeout counters, read latency histogram, and pool
  gauges; no payloads.
- **Tests:** hit, miss-populate, pool-exhaustion fallback, timeout fallback, TLS
  handshake failure, and shutdown while a read is in flight.
- **Operational tradeoffs:** `max: 20` bounds memory and peer slots at some
  concurrency cost; `command_timeout: 250ms` sheds slow calls quickly at the
  cost of failing borderline-slow reads.

## Idempotent retry around a non-idempotent operation

```text
# 1. Supported: illustrative. `full_jitter` and Retry-After parsing are
#    library-specific; verify your HTTP client honors Retry-After.

function charge_once(order_id, amount):
  key = idempotency_key(order_id)          # 4. unguessable, scoped to caller
  attempt = 0
  deadline = now() + 10s                   # total budget
  while true:
    try:
      resp = payments.charge(              # 3. each attempt owns its request/conn
        amount = amount,
        idempotency_key = key)             # server dedupes replays -> safe to retry
      metrics.count("charge.outcome", labels = { result: "ok", attempts: attempt + 1 })
      return resp
    except err:
      attempt += 1
      retryable = is_transient(err) or is_rate_limited(err)   # 2. failure classes
      if not retryable or attempt >= 4 or now() >= deadline:
        metrics.count("charge.exhausted", labels = { attempts: attempt })
        raise Exhausted(cause = err, attempts = attempt)      # single final failure
      wait = retry_after(err) or full_jitter(base = 100ms, cap = 2s, attempt = attempt)
      sleep(wait)
```

- **Failure behavior:** validation/auth errors are never retried; only transient
  and honored rate-limit errors are; exhaustion raises one typed error.
- **Resource cleanup:** every attempt acquires and releases its own connection;
  an outer cancellation stops further attempts.
- **Security:** the idempotency key is unguessable, caller-scoped, and never
  logged; the amount and order are not placed in log messages.
- **Observability:** outcome counter with attempt count and an exhaustion
  counter; total elapsed can be added as a histogram.
- **Tests:** transient-then-success, non-retryable first error, rate-limit with
  Retry-After, budget exhaustion, and idempotent replay returning the original
  charge.
- **Operational tradeoffs:** four attempts over ten seconds absorbs brief blips
  but adds tail latency and load during an outage; full jitter avoids
  synchronized retry storms at the cost of less predictable timing.
