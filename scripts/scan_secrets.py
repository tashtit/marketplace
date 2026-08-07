#!/usr/bin/env python3
"""Scan the repository for committed secrets without third-party dependencies.

The scanner is deliberately conservative. Tashtit documentation discusses
tokens, secret names, and workflow expressions constantly, so only patterns
that identify real key *material* are reported. A reference such as
``${{ secrets.NPM_TOKEN }}`` or prose about an API key is never a finding.

Add ``pragma: allowlist secret`` on the same line to accept a deliberate
fixture.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
# Mirrors scripts/validate.py: version control, editor state, and installed
# dependencies never carry repository content.
IGNORED_DIRECTORIES = {".git", ".idea", "node_modules"}
ALLOWLIST_MARKER = "pragma: allowlist secret"
MAX_BYTES = 2_000_000

# Each rule matches issued credential material, not a name or a reference.
RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "private key block",
        re.compile(r"-----BEGIN(?: [A-Z0-9]+)* PRIVATE KEY-----"),
    ),
    ("AWS access key id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("GitHub fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{60,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[0-9A-Za-z-]{10,}\b")),
    ("Stripe live key", re.compile(r"\bsk_live_[0-9A-Za-z]{24,}\b")),
    ("npm token", re.compile(r"\bnpm_[A-Za-z0-9]{36}\b")),
    ("PyPI token", re.compile(r"\bpypi-AgEIcHlwaS5vcmc[A-Za-z0-9_-]{50,}\b")),
    ("OpenAI key", re.compile(r"\bsk-[A-Za-z0-9]{20}T3BlbkFJ[A-Za-z0-9]{20}\b")),
)

findings: list[str] = []


def report(path: Path, line_number: int, label: str) -> None:
    """Record a finding without echoing the matched secret value."""
    try:
        display_path = path.relative_to(ROOT)
    except ValueError:
        display_path = path
    findings.append(f"{display_path}:{line_number}: possible {label}")


def is_ignored(path: Path) -> bool:
    """Report whether a path sits inside a directory that is never scanned."""
    return any(part in IGNORED_DIRECTORIES for part in path.parts)


def scan_file(path: Path) -> None:
    try:
        if path.stat().st_size > MAX_BYTES:
            return
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return

    for line_number, line in enumerate(content.splitlines(), start=1):
        if ALLOWLIST_MARKER in line:
            continue
        for label, pattern in RULES:
            if pattern.search(line):
                report(path, line_number, label)


def main() -> int:
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.is_symlink() or is_ignored(path):
            continue
        scan_file(path)

    if findings:
        print("Tashtit secret scan failed:", file=sys.stderr)
        for finding in findings:
            print(f"- {finding}", file=sys.stderr)
        print(
            "\nRotate any real credential before removing it from history. "
            f"Append '{ALLOWLIST_MARKER}' to accept a deliberate fixture.",
            file=sys.stderr,
        )
        return 1

    print("Tashtit secret scan passed (no credential material found).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
