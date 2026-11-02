# Probe Seeds — Handling Large Blobs

Tashtit-authored scenarios derived from [S14]. Adapt them to the named attempt;
never speak the Concern or Looking for fields before the debrief.

Technical criteria come from the linked concept. This source establishes no
career-level thresholds.

## P1 — The API fleet moves every byte twice

- **Concern:** [Handling Large Blobs](../concepts/large-blobs.md#separate-bytes-from-permissions) — never spoken aloud.
- **Symptom:** Large uploads enter an application server and are then forwarded to storage; transfer traffic dominates the fleet.
- **Looking for:** Authorize and issue scoped temporary transfer permission, keep metadata in the application, and let the client send bytes directly to storage. Explain when inspection requirements justify a proxy. [S14]
- **Bar:** No seniority bar established by this source.
- **Follow-up if thin:** Which work needs application authorization, and which work is just moving bytes?

## P2 — An upload fails near completion

- **Concern:** [Handling Large Blobs](../concepts/large-blobs.md#resume-and-complete-transfers) — never spoken aloud.
- **Symptom:** A multi-gigabyte upload loses its connection after nearly all data has transferred.
- **Looking for:** Retain the upload identity, query completed parts, send missing data, and finalize the object. Explain progress and cleanup of unfinished parts. [S14]
- **Bar:** No seniority bar established by this source.
- **Follow-up if thin:** Does having every part stored mean the final file already exists?

## P3 — The database and storage disagree

- **Concern:** [Handling Large Blobs](../concepts/large-blobs.md#synchronize-metadata-with-storage) — never spoken aloud.
- **Symptom:** Some records say pending despite a complete object; another record says complete after only a client notification.
- **Looking for:** Use an application-chosen storage key and pending metadata, storage-originated completion events, and reconciliation of stuck records. Do not claim cross-store atomicity. [S14]
- **Bar:** No seniority bar established by this source.
- **Follow-up if thin:** What evidence does the storage service provide that the client cannot reliably provide?

## P4 — A harmful file is immediately shared

- **Concern:** [Handling Large Blobs](../concepts/large-blobs.md#inspect-before-publishing) — never spoken aloud.
- **Symptom:** A user uploads a file labelled as an image and distributes its public link before any inspection runs.
- **Looking for:** Quarantine uploads, validate and scan actual content, and publish only after checks. Distinguish scoped upload permission from content safety. [S14]
- **Bar:** No seniority bar established by this source.
- **Follow-up if thin:** When should the database mark the file available?

## P5 — A download starts from zero again

- **Concern:** [Handling Large Blobs](../concepts/large-blobs.md#downloads-and-simpler-alternatives) — never spoken aloud.
- **Symptom:** A distant user loses a large download near completion and must fetch the entire object again.
- **Looking for:** Combine geographic caching with byte-range resumability; check serving-layer and signed-permission support. Explain why parallelism may not beat the user’s total bandwidth limit. [S14]
- **Bar:** No seniority bar established by this source.
- **Follow-up if thin:** What state lets the client ask only for the missing bytes?

## Coverage note

Score only the cited mechanisms in Looking for. Questions in the concept’s
Not covered by sources section have no answer key here. Do not infer a seniority
level from a deep dive or add mechanisms absent from the source.

## Sources

- **[S14]** Hello Interview — Handling Large Blobs — <https://www.hellointerview.com/learn/system-design/patterns/large-blobs> (user-supplied saved HTML, processed 2026-11-01).
