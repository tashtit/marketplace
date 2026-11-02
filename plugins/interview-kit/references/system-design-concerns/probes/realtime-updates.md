# Probe Seeds — Real-time Updates

Tashtit-authored scenarios derived from [S12]. Adapt them to the named attempt;
never speak the Concern or Looking for fields before the debrief.

Technical criteria come from the linked concept. Seniority is assessed only where
[level expectations](../level-expectations.md) explicitly supplies a bar.

## P1 — The socket is open but nothing arrives

- **Concern:** [Real-time Updates](../concepts/realtime-updates.md#route-events-to-connections) — never spoken aloud.
- **Symptom:** A producer commits updates, but clients connected to different hosts never receive them.
- **Looking for:** Address both hops: route to a known owner or publish to topics subscribed by the endpoint hosts, then forward on local connections. [S12]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** How does the producer find the host that can reach this client?

## P2 — The stream arrives all at once

- **Concern:** [Real-time Updates](../concepts/realtime-updates.md#choose-a-client-transport) — never spoken aloud.
- **Symptom:** A one-way incremental response works locally but only appears at completion behind a proxy.
- **Looking for:** Check streaming support and buffering throughout the HTTP path; SSE is suitable for one-way streaming without frequent upstream messages. [S12]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** Which intermediary might be waiting for the response to finish?

## P3 — A healthy reconnect loses messages

- **Concern:** [Real-time Updates](../concepts/realtime-updates.md#recovery-and-fan-out) — never spoken aloud.
- **Symptom:** A mobile client reconnects successfully but is missing events from its offline interval.
- **Looking for:** Detect failures, retain replayable updates, and resume from received sequence/event references. Transport recovery alone does not recover missed events. [S12]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** What must the client report and what must the server retain?

## P4 — A deployment moves everyone

- **Concern:** [Real-time Updates](../concepts/realtime-updates.md#route-events-to-connections) — never spoken aloud.
- **Symptom:** Adding one endpoint node forces most clients to rebuild expensive shared state.
- **Looking for:** Explain ownership changes under modulo hashing versus consistent hashing, coordination, and gradual transition routing. [S12]
- **Bar:** Use only the scoped expectations in `level-expectations.md`; no other seniority bar is established.
- **Follow-up if thin:** What happens to events while old and new assignments both exist?

## Coverage note

Score only the cited mechanisms in Looking for. Questions in the concept’s
Not covered by sources section have no answer key here. Do not infer a seniority
level from an article heading, a deep dive, or the difficulty of this scenario.

## Sources

- **[S12]** Hello Interview — Real-time Updates — <https://www.hellointerview.com/learn/system-design/patterns/realtime-updates> (user-supplied saved HTML, processed 2026-11-01).
