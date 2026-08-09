"""Unit tests for scripts/validate.py."""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import support

import validate


class ValidateCase(unittest.TestCase):
    """Base case with a resolved temporary root the validator can traverse."""

    def setUp(self) -> None:
        # resolve() matters: macOS temp directories live behind a /var symlink,
        # and the validator compares resolved paths against ROOT.
        self.root = Path(
            self.enterContext(tempfile.TemporaryDirectory())
        ).resolve()


class FrontmatterTests(ValidateCase):
    def parse(self, content: str) -> dict[str, str]:
        path = self.root / "SKILL.md"
        support.write_text(path, content)
        return validate.parse_frontmatter(path)

    def test_parses_scalar_fields(self) -> None:
        with support.validate_paths(self.root):
            fields = self.parse(
                "---\nname: alpha\ndescription: A skill.\n---\nBody.\n"
            )
            self.assertEqual(validate.errors, [])
        self.assertEqual(
            fields, {"name": "alpha", "description": "A skill."}
        )

    def test_unquotes_double_quoted_values(self) -> None:
        with support.validate_paths(self.root):
            fields = self.parse(
                '---\ndescription: "A \\"quoted\\" value"\n---\n'
            )
            self.assertEqual(validate.errors, [])
        self.assertEqual(fields["description"], 'A "quoted" value')

    def test_rejects_missing_opening_marker(self) -> None:
        with support.validate_paths(self.root):
            self.assertEqual(self.parse("name: alpha\n"), {})
            self.assertIn("must begin with a '---'", validate.errors[0])

    def test_rejects_unclosed_block(self) -> None:
        with support.validate_paths(self.root):
            self.parse("---\nname: alpha\n")
            self.assertIn("never closed", validate.errors[0])

    def test_rejects_duplicate_field(self) -> None:
        with support.validate_paths(self.root):
            self.parse("---\nname: alpha\nname: beta\n---\n")
            self.assertIn("duplicate frontmatter field", validate.errors[0])

    def test_rejects_non_scalar_line(self) -> None:
        with support.validate_paths(self.root):
            self.parse("---\n- a list item\n---\n")
            self.assertIn("cannot parse", validate.errors[0])


class CatalogTableTests(ValidateCase):
    def test_maps_rows_and_skips_non_plugin_lines(self) -> None:
        path = self.root / "README.md"
        support.write_text(
            path,
            "| Plugin | Version | Maturity |\n"
            "| --- | --- | --- |\n"
            "| [alpha](plugins/alpha/) | 1.0.0 | Experimental |\n"
            "| [docs](docs/notes.md) | x | y |\n"
            "Prose outside the table.\n",
        )
        with support.validate_paths(self.root):
            listed = validate.parse_catalog_table(path, "plugins/")
            self.assertEqual(validate.errors, [])
        self.assertEqual(listed, {"alpha": ("1.0.0", "Experimental")})

    def test_rejects_duplicate_rows(self) -> None:
        path = self.root / "README.md"
        support.write_text(
            path,
            "| [alpha](plugins/alpha/) | 1.0.0 | Experimental |\n"
            "| [alpha](plugins/alpha/) | 1.0.0 | Experimental |\n",
        )
        with support.validate_paths(self.root):
            validate.parse_catalog_table(path, "plugins/")
            self.assertIn("duplicate catalog row", validate.errors[0])


class ManifestComponentTests(ValidateCase):
    def check(self, manifest: dict) -> list[str]:
        with support.validate_paths(self.root):
            validate.validate_manifest_components(
                self.root / "plugin.json", self.root, manifest
            )
            return list(validate.errors)

    def test_accepts_existing_component_paths(self) -> None:
        support.write_text(self.root / "agents" / "a.md", "agent\n")
        (self.root / "skills").mkdir()
        errors = self.check(
            {"skills": "./skills", "agents": ["./agents/a.md"]}
        )
        self.assertEqual(errors, [])

    def test_rejects_string_where_array_is_required(self) -> None:
        errors = self.check({"agents": "./agents/"})
        self.assertIn("must be a non-empty array of file paths", errors[0])

    def test_rejects_missing_string_component_path(self) -> None:
        errors = self.check({"skills": "./skills"})
        self.assertIn("does not exist", errors[0])

    def test_rejects_list_entry_that_is_not_a_file(self) -> None:
        errors = self.check({"commands": ["./missing.md"]})
        self.assertIn("is not a file", errors[0])


class AcceptanceResultTests(ValidateCase):
    SCENARIOS = {"alpha-positive-case": {"claude-code"}}

    def entry(self, **overrides) -> dict:
        base = {
            "scenario": "alpha-positive-case",
            "platform": "claude-code",
            "plugin_version": "1.0.0",
            "commit": "0" * 40,
            "reviewed_on": "2026-01-01",
            "reviewer": "reviewer",
            "outcome": "pass",
        }
        base.update(overrides)
        return base

    def check(self, results) -> tuple[dict, list[str]]:
        with support.validate_paths(self.root):
            passes = validate.validate_acceptance_results(
                self.root / "acceptance.json", self.SCENARIOS, results
            )
            return passes, list(validate.errors)

    def test_indexes_passing_reviews_by_version(self) -> None:
        passes, errors = self.check([self.entry()])
        self.assertEqual(errors, [])
        self.assertEqual(
            passes, {("alpha-positive-case", "claude-code"): {"1.0.0"}}
        )

    def test_rejects_non_array_results(self) -> None:
        passes, errors = self.check("not-a-list")
        self.assertEqual(passes, {})
        self.assertIn("results must be an array", errors[0])

    def test_rejects_unknown_scenario(self) -> None:
        _, errors = self.check([self.entry(scenario="alpha-unknown")])
        self.assertIn("unknown scenario", errors[0])

    def test_rejects_platform_the_scenario_does_not_claim(self) -> None:
        _, errors = self.check([self.entry(platform="codex")])
        self.assertIn("does not claim", errors[0])

    def test_rejects_short_commit(self) -> None:
        _, errors = self.check([self.entry(commit="abc123")])
        self.assertIn("40-character commit", errors[0])

    def test_rejects_duplicate_review(self) -> None:
        _, errors = self.check([self.entry(), self.entry()])
        self.assertIn("duplicates the review", errors[0])

    def test_failing_review_is_not_indexed_as_pass(self) -> None:
        passes, errors = self.check([self.entry(outcome="fail")])
        self.assertEqual(errors, [])
        self.assertEqual(passes, {})


class ActionPinTests(ValidateCase):
    def pin_errors(self, step_lines: str) -> list[str]:
        support.write_text(
            self.root / ".github" / "workflows" / "ci.yml",
            "jobs:\n  build:\n    steps:\n" + step_lines,
        )
        with support.validate_paths(self.root):
            validate.validate_action_pins()
            return list(validate.errors)

    def test_accepts_full_sha_and_exact_github_tag(self) -> None:
        errors = self.pin_errors(
            f"      - uses: third/party@{'0' * 40}\n"
            "      - name: Checkout\n"
            "        uses: actions/checkout@v7.0.1\n"
        )
        self.assertEqual(errors, [])

    def test_rejects_movable_major_tag_on_github_action(self) -> None:
        errors = self.pin_errors("      - uses: actions/cache@v7\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("exact release tag", errors[0])

    def test_rejects_release_tag_on_third_party_action(self) -> None:
        errors = self.pin_errors("      - uses: third/party@v1.2.3\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("full 40-character commit SHA", errors[0])

    def test_rejects_branch_reference(self) -> None:
        errors = self.pin_errors("      - uses: actions/checkout@main\n")
        self.assertEqual(len(errors), 1)


class EndToEndTests(ValidateCase):
    """Run main() against a complete fixture repository."""

    def setUp(self) -> None:
        super().setUp()
        support.build_repo(self.root, plugins=("alpha", "beta"))
        self.shared = self.root / ".claude-plugin" / "marketplace.json"

    def run_main(self) -> tuple[int, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with support.validate_paths(self.root):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(
                stderr
            ):
                code = validate.main()
        return code, stderr.getvalue()

    def test_clean_fixture_passes(self) -> None:
        code, stderr = self.run_main()
        self.assertEqual(code, 0, stderr)

    def test_unsorted_marketplace_fails(self) -> None:
        support.mutate_json(
            self.shared, lambda data: data["plugins"].reverse()
        )
        code, stderr = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("plugins must be sorted by name", stderr)

    def test_catalog_version_drift_fails(self) -> None:
        readme = self.root / "README.md"
        content = readme.read_text(encoding="utf-8")
        support.write_text(
            readme,
            content.replace(
                "| [alpha](plugins/alpha/) | 1.0.0 |",
                "| [alpha](plugins/alpha/) | 2.0.0 |",
            ),
        )
        code, stderr = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("listed as version '2.0.0'", stderr)

    def test_missing_scenario_type_fails(self) -> None:
        scenarios = self.root / "tests" / "plugins" / "alpha" / "scenarios"
        (scenarios / "unsafe-case.json").unlink()
        code, stderr = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("missing required scenario types", stderr)
        self.assertIn("unsafe", stderr)

    def test_collapsed_json_fails(self) -> None:
        path = self.root / "tests" / "plugins" / "alpha" / "acceptance.json"
        support.write_text(
            path,
            '{"plugin": "alpha", "maturity": "experimental", "results": []}\n',
        )
        code, stderr = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("pretty-printed", stderr)

    def test_manifest_version_drift_fails(self) -> None:
        manifest = (
            self.root / "plugins" / "alpha" / ".claude-plugin" / "plugin.json"
        )
        support.mutate_json(
            manifest, lambda data: data.update(version="9.9.9")
        )
        code, stderr = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("version differs across provider adapters", stderr)

    def test_overlong_skill_description_fails(self) -> None:
        skill = self.root / "plugins" / "alpha" / "skills" / "alpha" / "SKILL.md"
        support.write_text(
            skill,
            "---\nname: alpha\ndescription: " + "x" * 1100 + "\n---\n\nBody.\n",
        )
        code, stderr = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("skill description limit", stderr)

    def test_duplicate_skill_name_fails(self) -> None:
        skill = self.root / "plugins" / "beta" / "skills" / "beta" / "SKILL.md"
        support.write_text(
            skill,
            "---\nname: alpha\ndescription: Duplicate of alpha.\n---\n\nBody.\n",
        )
        code, stderr = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("must match the skill directory", stderr)

    def test_broken_markdown_link_fails(self) -> None:
        support.write_text(
            self.root / "docs.md", "See [missing](missing/file.md).\n"
        )
        code, stderr = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("broken local link", stderr)


if __name__ == "__main__":
    unittest.main()
