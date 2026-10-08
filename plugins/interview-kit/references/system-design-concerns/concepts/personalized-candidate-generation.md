# Personalized Candidate Generation

A personalized candidate list can be built on demand with indexed filters, precomputed for fast first access, or combined so a cached start gives way to fresh results [S6].

## Approaches and tradeoffs

- **Indexed real-time queries.** Index commonly filtered attributes, including geospatial location, to retrieve nearby candidates without a slow scan and reflect current preferences [S6]. Keeping a separate search index synchronized with the primary store is difficult: delays or failures can expose outdated profiles or omit new ones. The source proposes change data capture and, when update rates warrant it, batching index writes [S6].
- **Precompute and cache.** Background jobs build personalized lists for quick retrieval, potentially off peak; active users can exhaust them, and changed locations, preferences, or profiles make them stale [S6]. Computing for everyone several times daily is expensive, so warming only recently active users is an option [S6].
- **Combine both paths.** Serve a cached initial list and obtain additional candidates from the index as the client approaches the end, initiating the refresh before the list is exhausted [S6].

## Freshness controls

A source-suggested cached-list TTL of less than one hour, periodic refresh, and refresh after significant location or preference changes limit staleness; TTL, list size, and the population whose lists are warmed are tunable operational parameters, not universal constants [S6].

## Not covered by sources

- How is a cache refresh coordinated with concurrent requests for the same personalized list?
- How are updates to a search index ordered or retried after a synchronization failure?
- What bounds the cost of real-time fallback during a cache miss surge?

## Sources

- **[S6]** Hello Interview — Design a Dating App Like Tinder —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/tinder>
