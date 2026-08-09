"""Unit tests for scripts/scan_secrets.py.

Every synthetic credential below is assembled by concatenation so that this
file, which the scanner itself scans on every `make validate`, never contains
a contiguous string matching any rule.
"""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import support

import scan_secrets

FAKE_SECRETS = {
    "AWS access key id": "AKIA" + "0123456789ABCDEF",
    "GitHub token": "ghp" + "_" + "a" * 36,
    "GitHub fine-grained token": "github" + "_pat_" + "a" * 60,
    "Google API key": "AIza" + "0" * 35,
    "Slack token": "xoxb" + "-" + "0" * 12,
    "Stripe live key": "sk" + "_live_" + "a" * 24,
    "npm token": "npm" + "_" + "a" * 36,
    "private key block": "-----BEGIN RSA" + " PRIVATE" + " KEY-----",
    "OpenAI key": "sk-" + "a" * 20 + "T3Blb" + "kFJ" + "a" * 20,
}


class ScanCase(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(
            self.enterContext(tempfile.TemporaryDirectory())
        ).resolve()

    def scan(self, content: str) -> list[str]:
        path = self.root / "fixture.txt"
        support.write_text(path, content)
        with support.scan_paths(self.root):
            scan_secrets.scan_file(path)
            return list(scan_secrets.findings)


class RuleTests(ScanCase):
    def test_each_rule_matches_its_synthetic_credential(self) -> None:
        for label, value in FAKE_SECRETS.items():
            with self.subTest(label=label):
                findings = self.scan(f"token = {value}\n")
                self.assertEqual(len(findings), 1, findings)
                self.assertIn(f"possible {label}", findings[0])

    def test_findings_never_echo_the_matched_value(self) -> None:
        value = FAKE_SECRETS["AWS access key id"]
        findings = self.scan(f"token = {value}\n")
        self.assertNotIn(value, findings[0])

    def test_findings_include_path_and_line_number(self) -> None:
        value = FAKE_SECRETS["GitHub token"]
        findings = self.scan(f"line one\ntoken = {value}\n")
        self.assertIn("fixture.txt:2:", findings[0])


class NonFindingTests(ScanCase):
    def test_workflow_secret_references_are_not_findings(self) -> None:
        self.assertEqual(
            self.scan("password: ${{ secrets.NPM_TOKEN }}\n"), []
        )

    def test_prose_about_credentials_is_not_a_finding(self) -> None:
        self.assertEqual(
            self.scan("Store the API key in your secret manager.\n"), []
        )

    def test_allowlist_pragma_skips_the_line(self) -> None:
        value = FAKE_SECRETS["AWS access key id"]
        marker = scan_secrets.ALLOWLIST_MARKER
        self.assertEqual(self.scan(f"{value}  # {marker}\n"), [])

    def test_oversized_files_are_skipped(self) -> None:
        value = FAKE_SECRETS["AWS access key id"]
        with mock.patch.object(scan_secrets, "MAX_BYTES", 10):
            self.assertEqual(self.scan(f"token = {value}\n"), [])

    def test_undecodable_files_are_skipped(self) -> None:
        path = self.root / "binary.bin"
        path.write_bytes(b"\x00\xff\xfe" + b"\x80" * 8)
        with support.scan_paths(self.root):
            scan_secrets.scan_file(path)
            self.assertEqual(scan_secrets.findings, [])


class MainTests(ScanCase):
    def run_main(self) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with support.scan_paths(self.root):
            with contextlib.redirect_stdout(
                stdout
            ), contextlib.redirect_stderr(stderr):
                code = scan_secrets.main()
        return code, stdout.getvalue(), stderr.getvalue()

    def test_clean_tree_passes(self) -> None:
        support.write_text(self.root / "README.md", "No credentials here.\n")
        code, stdout, _ = self.run_main()
        self.assertEqual(code, 0)
        self.assertIn("passed", stdout)

    def test_planted_credential_fails_with_a_located_finding(self) -> None:
        value = FAKE_SECRETS["Slack token"]
        support.write_text(
            self.root / "config" / "app.yml", f"slack: {value}\n"
        )
        code, _, stderr = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("config/app.yml:1: possible Slack token", stderr)
        self.assertNotIn(value, stderr)

    def test_ignored_directories_are_not_scanned(self) -> None:
        value = FAKE_SECRETS["GitHub token"]
        support.write_text(
            self.root / "node_modules" / "dep" / "index.js", f"{value}\n"
        )
        code, _, _ = self.run_main()
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
