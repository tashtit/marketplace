"""Unit tests for scripts/sync.py."""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import support

import sync


class SyncCase(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(
            self.enterContext(tempfile.TemporaryDirectory())
        ).resolve()


class TargetsCodexTests(unittest.TestCase):
    def test_defaults_to_codex_when_platforms_are_omitted(self) -> None:
        self.assertTrue(sync.targets_codex({"name": "alpha"}))

    def test_respects_an_explicit_platform_list(self) -> None:
        self.assertTrue(sync.targets_codex({"platforms": ["codex"]}))
        self.assertFalse(sync.targets_codex({"platforms": ["claude-code"]}))


class BuildCodexMarketplaceTests(unittest.TestCase):
    def test_translates_entries_and_drops_non_codex_plugins(self) -> None:
        marketplace = {
            "name": "tashtit",
            "plugins": [
                {"name": "alpha", "category": "testing"},
                {
                    "name": "beta",
                    "category": "testing",
                    "platforms": ["claude-code"],
                },
            ],
        }
        built = sync.build_codex_marketplace(marketplace)
        self.assertEqual(built["name"], "tashtit")
        self.assertEqual(built["interface"], {"displayName": "Tashtit"})
        self.assertEqual(len(built["plugins"]), 1)
        self.assertEqual(
            built["plugins"][0],
            {
                "name": "alpha",
                "source": {"source": "local", "path": "./plugins/alpha"},
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": "testing",
            },
        )

    def test_render_is_pretty_printed_with_trailing_newline(self) -> None:
        rendered = sync.render({"a": 1})
        self.assertEqual(rendered, '{\n  "a": 1\n}\n')


class LoadSharedMarketplaceTests(SyncCase):
    def setUp(self) -> None:
        super().setUp()
        support.build_repo(self.root, plugins=("alpha", "beta"))
        self.shared = self.root / ".claude-plugin" / "marketplace.json"

    def test_accepts_the_fixture_marketplace(self) -> None:
        with support.sync_paths(self.root):
            marketplace = sync.load_shared_marketplace()
        self.assertEqual(
            [plugin["name"] for plugin in marketplace["plugins"]],
            ["alpha", "beta"],
        )

    def test_rejects_unsorted_plugins(self) -> None:
        support.mutate_json(
            self.shared, lambda data: data["plugins"].reverse()
        )
        with support.sync_paths(self.root):
            with self.assertRaisesRegex(sync.SyncError, "sorted by name"):
                sync.load_shared_marketplace()

    def test_rejects_a_non_semver_version(self) -> None:
        support.mutate_json(
            self.shared,
            lambda data: data["plugins"][0].update(version="1.0"),
        )
        with support.sync_paths(self.root):
            with self.assertRaisesRegex(sync.SyncError, "Semantic Versioning"):
                sync.load_shared_marketplace()

    def test_rejects_an_unknown_platform(self) -> None:
        support.mutate_json(
            self.shared,
            lambda data: data["plugins"][0].update(platforms=["mystery"]),
        )
        with support.sync_paths(self.root):
            with self.assertRaisesRegex(sync.SyncError, "unknown platforms"):
                sync.load_shared_marketplace()


class LoadSharedManifestTests(SyncCase):
    def load(self, manifest: dict) -> str:
        path = self.root / "plugin.json"
        support.write_json(path, manifest)
        return sync.load_shared_manifest(path, "alpha")

    def manifest(self, **overrides) -> dict:
        base = {
            "name": "alpha",
            "version": "1.0.0",
            "description": "Fixture plugin alpha.",
            "skills": "./skills",
        }
        base.update(overrides)
        return base

    def test_returns_the_manifest_text_verbatim(self) -> None:
        content = self.load(self.manifest())
        self.assertEqual(
            content, (self.root / "plugin.json").read_text(encoding="utf-8")
        )

    def test_rejects_a_name_mismatch(self) -> None:
        with self.assertRaisesRegex(sync.SyncError, "name must be 'alpha'"):
            self.load(self.manifest(name="beta"))

    def test_rejects_a_missing_required_field(self) -> None:
        manifest = self.manifest()
        del manifest["skills"]
        with self.assertRaisesRegex(sync.SyncError, "skills"):
            self.load(manifest)

    def test_rejects_a_skills_path_without_dot_slash(self) -> None:
        with self.assertRaisesRegex(sync.SyncError, "start with './'"):
            self.load(self.manifest(skills="skills"))


class SyncArtifactTests(SyncCase):
    def test_current_file_passes_check_mode(self) -> None:
        path = self.root / "generated.json"
        support.write_text(path, "expected\n")
        self.assertTrue(sync.sync_artifact(path, "expected\n", check=True))

    def test_stale_file_fails_check_mode_with_a_diff(self) -> None:
        path = self.root / "generated.json"
        support.write_text(path, "stale\n")
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            result = sync.sync_artifact(path, "expected\n", check=True)
        self.assertFalse(result)
        self.assertIn("-stale", stderr.getvalue())
        self.assertIn("+expected", stderr.getvalue())

    def test_write_mode_creates_the_expected_content(self) -> None:
        path = self.root / "nested" / "generated.json"
        with contextlib.redirect_stdout(io.StringIO()):
            result = sync.sync_artifact(path, "expected\n", check=False)
        self.assertTrue(result)
        self.assertEqual(path.read_text(encoding="utf-8"), "expected\n")

    def test_symlink_fails_check_mode_and_is_replaced_in_write_mode(
        self,
    ) -> None:
        target = self.root / "target.json"
        support.write_text(target, "expected\n")
        link = self.root / "generated.json"
        link.symlink_to(target)

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            self.assertFalse(sync.sync_artifact(link, "expected\n", check=True))
        self.assertIn("symlink", stderr.getvalue())

        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(sync.sync_artifact(link, "expected\n", check=False))
        self.assertFalse(link.is_symlink())
        self.assertEqual(link.read_text(encoding="utf-8"), "expected\n")


class MainTests(SyncCase):
    def setUp(self) -> None:
        super().setUp()
        support.build_repo(self.root, plugins=("alpha", "beta"))
        self.codex_marketplace = (
            self.root / ".agents" / "plugins" / "marketplace.json"
        )

    def run_main(self, *argv: str) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with support.sync_paths(self.root):
            with mock.patch("sys.argv", ["sync.py", *argv]):
                with contextlib.redirect_stdout(
                    stdout
                ), contextlib.redirect_stderr(stderr):
                    code = sync.main()
        return code, stdout.getvalue(), stderr.getvalue()

    def test_check_passes_on_a_synchronized_fixture(self) -> None:
        code, stdout, stderr = self.run_main("--check")
        self.assertEqual(code, 0, stderr)
        # One codex marketplace plus one adapter per plugin.
        self.assertIn("(3 files)", stdout)

    def test_check_fails_on_a_stale_generated_file(self) -> None:
        support.mutate_json(
            self.codex_marketplace,
            lambda data: data["plugins"][0].update(category="drifted"),
        )
        code, _, stderr = self.run_main("--check")
        self.assertEqual(code, 1)
        self.assertIn("stale", stderr)

    def test_write_mode_regenerates_a_stale_file(self) -> None:
        expected = self.codex_marketplace.read_text(encoding="utf-8")
        support.mutate_json(
            self.codex_marketplace,
            lambda data: data["plugins"][0].update(category="drifted"),
        )
        code, stdout, _ = self.run_main()
        self.assertEqual(code, 0)
        self.assertIn("updated", stdout)
        self.assertEqual(
            self.codex_marketplace.read_text(encoding="utf-8"), expected
        )

    def test_invalid_canonical_source_fails_before_generation(self) -> None:
        support.mutate_json(
            self.root / ".claude-plugin" / "marketplace.json",
            lambda data: data.update(name="wrong"),
        )
        code, _, stderr = self.run_main("--check")
        self.assertEqual(code, 1)
        self.assertIn("canonical source validation failed", stderr)

    def test_non_codex_plugin_gets_no_adapter(self) -> None:
        shared = self.root / ".claude-plugin" / "marketplace.json"
        support.mutate_json(
            shared,
            lambda data: data["plugins"][1].update(platforms=["claude-code"]),
        )
        with support.sync_paths(self.root):
            artifacts = sync.collect_artifacts()
        paths = [path for path, _ in artifacts]
        self.assertEqual(len(artifacts), 2)
        self.assertNotIn(
            self.root / "plugins" / "beta" / ".codex-plugin" / "plugin.json",
            paths,
        )


if __name__ == "__main__":
    unittest.main()
