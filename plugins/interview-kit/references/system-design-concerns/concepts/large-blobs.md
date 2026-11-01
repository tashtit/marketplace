# Handling Large Blobs

## Separate bytes from permissions

- Store large file bytes in object storage and queryable metadata in a database. Proxying the bytes through application servers adds transfer load, latency, and a bandwidth bottleneck; direct transfer lets the application focus on authorization and metadata. [S14]
- After validating the user and quotas, issue temporary permission for a particular operation and storage location. A presigned URL is usable by anyone holding it, so its scope and expiry matter. Storage validates the request rather than routing every byte through the application. [S14]
- The source calls for file-size and content-type restrictions as part of upload permission. It describes these conceptually without establishing which provider API supports each policy condition; do not assume every condition is enforceable through every signed URL form. [S14]
- Storage and CDN download permissions are validated by different serving components. Direct storage access is simpler for infrequent downloads; a CDN adds cost and distribution complexity in exchange for caching and geographic performance. [S14]

## Resume and complete transfers

- Split a large upload into parts using the provider's multipart or resumable-upload protocol. Persist the upload/session identity, query storage for completed parts after an interruption, and retransmit missing parts rather than restarting the file. Part completion also supplies progress information. [S14]
- In the multipart example, uploaded parts are not yet the completed file. Finalization supplies the part numbers and returned checksums so storage can assemble the object. Incomplete uploads consume storage; the source suggests lifecycle cleanup after roughly one to two days. [S14]
- Provider APIs and session models differ. The transferable requirement is resumable state, not memorizing product-specific chunk sizes or assuming one vendor's completion protocol applies everywhere. [S14]

## Synchronize metadata with storage

- Create a pending metadata record when issuing upload permission, including an application-chosen storage key. That key associates later storage events with the right database record and prevents arbitrary client-chosen overwrite targets. [S14]
- Client completion reports can be premature, malicious, or lost. Prefer storage-originated completion events to establish that an object exists; handle delayed or lost event processing with a periodic check of pending records against storage. This gives eventual synchronization, not an atomic cross-store transaction. [S14]
- Keep rich, searchable metadata in the database. Object tags and headers can carry limited attributes but do not replace efficient database queries over uploader, type, and time. [S14]

## Inspect before publishing

- Upload to quarantine, validate content and type, and scan before making the object publicly available. Update availability only after these checks; immediate publication makes later abuse detection too late to prevent access. [S14]
- Permission limits constrain resource consumption, while actual content checks address what the file contains. A claimed image type does not by itself establish that the bytes are a safe image. [S14]

## Downloads and simpler alternatives

- CDN caching moves popular bytes closer to readers. Range requests let downloads resume missing byte ranges after interruption; storage, CDN behavior, and signed permissions must support the required requests. [S14]
- Parallel range downloads add client assembly complexity and help mainly when individual connections, rather than total client bandwidth, are limiting throughput. [S14]
- Direct-transfer orchestration adds overhead. The article uses about 10 MB as an infrastructure-dependent signal, not a universal cutoff. Small payloads may use ordinary endpoints; requirements for inspecting bytes before acceptance or storage can justify a proxy path. [S14]

## Not covered by sources

- Which signed upload API enforces each proposed size or content-type condition?
- How should duplicate or out-of-order storage events be handled?
- How should a pending upload and its storage object be reconciled when they disagree on ownership or version?
- How should already-issued download access be revoked immediately?

## Sources

- **[S14]** Hello Interview — Handling Large Blobs — <https://www.hellointerview.com/learn/system-design/patterns/large-blobs> (user-supplied saved HTML, processed 2026-11-01).
