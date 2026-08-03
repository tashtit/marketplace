#!/usr/bin/env python3
"""Scan the repository for probable committed secrets, dependency-free.

The quality standard forbids real secrets in examples or fixtures. This scanner
is a fast, high-signal guard for the most dangerous, unambiguous credential
shapes so a leak fails CI before it is published. It is intentionally
conservative: it targets provider tokens and private keys with distinctive
prefixes rather than generic high-entropy strings, so it stays quiet on the
placeholder examples plugins are expected to contain.

It is not a replacement for GitHub secret scanning or push protection; it is the
local, offline first line of defense. Findings are reported by path and line
with the secret value masked.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

# Directories and files that never contain source we author.
SKIP_DIRS = {".git", ".idea", ".vscode", "node_modules", "build", "dist", ".cache"}
# This scanner lists the very patterns it hunts for, so exclude it from itself.
SKIP_FILES = {Path("scripts/check_secrets.py")}

# Only scan text we plausibly wrote. Binary and lockfiles are skipped.
TEXT_SUFFIXES = {
    ".md",
    ".json",
    ".yml",
    ".yaml",
    ".py",
    ".sh",
    ".txt",
    ".toml",
    ".cfg",
    ".ini",
    ".env",
    ".example",
    "",
}

# High-signal, low-false-positive credential shapes. Each pattern targets a
# distinctive provider prefix or an unambiguous private-key header.
PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("AWS access key id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[0-9A-Za-z]{36,}\b")),
    (
        "GitHub fine-grained token",
        re.compile(r"\bgithub_pat_[0-9A-Za-z_]{22,}\b"),
    ),
    ("Slack token", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("Stripe secret key", re.compile(r"\bsk_(?:live|test)_[0-9A-Za-z]{16,}\b")),
    ("OpenAI key", re.compile(r"\bsk-(?:proj-)?[0-9A-Za-z_\-]{20,}\b")),
    ("Private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
    (
        "Slack webhook",
        re.compile(r"https://hooks\.slack\.com/services/T[0-9A-Za-z_/]{20,}"),
    ),
]


def mask(value: str) -> str:
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"


def iter_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        relative = path.relative_to(ROOT)
        if relative in SKIP_FILES:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        files.append(path)
    return sorted(files)


def scan() -> list[str]:
    findings: list[str] = []
    for path in iter_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        relative = path.relative_to(ROOT)
        for line_number, line in enumerate(text.splitlines(), start=1):
            for label, pattern in PATTERNS:
                match = pattern.search(line)
                if match:
                    findings.append(
                        f"{relative}:{line_number}: possible {label} "
                        f"({mask(match.group(0))})"
                    )
    return findings


def main() -> int:
    findings = scan()
    if findings:
        print("Possible secrets detected:", file=sys.stderr)
        for finding in findings:
            print(f"  {finding}", file=sys.stderr)
        print(
            "\nIf a match is a placeholder, choose an obviously fake value that "
            "does not match a real credential shape. Never commit a real secret.",
            file=sys.stderr,
        )
        return 1
    print("Secret scan passed (no probable credentials found).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
