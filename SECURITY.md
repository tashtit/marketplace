# Security Policy

## Supported versions

Tashtit is pre-release. Security fixes apply to the latest revision of the
default branch. A version support table will be published with the first stable
release.

## Reporting a vulnerability

Do not open a public issue for suspected vulnerabilities, exposed secrets,
unsafe command execution, permission bypasses, or supply-chain concerns.

Use GitHub private vulnerability reporting for this repository. If that feature
is unavailable, contact the maintainers through a private channel listed on the
repository owner profile and include:

- the affected plugin, file, and version or commit;
- the impact and realistic attack or failure scenario;
- reproduction steps or a minimal proof of concept;
- any known mitigation;
- whether the issue is already public.

Do not include real credentials, personal data, or third-party confidential
information.

Maintainers aim to acknowledge a report within three business days, provide an
initial assessment within seven business days, and coordinate disclosure after
a fix is available. These are response targets, not guarantees.

## Security model

Plugin content can influence agents that read files, execute commands, access
external systems, or modify repositories. Reviews therefore consider:

- prompt injection and untrusted input boundaries;
- least-privilege tool and network access;
- secret handling and log redaction;
- command injection and shell portability;
- dependency integrity and version pinning;
- destructive actions, confirmation, and rollback;
- data retention, telemetry, and external side effects;
- provenance of snippets and third-party content.

Stable plugins must document their trust boundaries and required permissions.
