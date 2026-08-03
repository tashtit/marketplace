#!/usr/bin/env python3
"""Validate the Tashtit repository without third-party dependencies."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jsonschema_mini import SchemaError, validate_instance  # noqa: E402


ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = ROOT / "schemas"
MARKETPLACES = {
    "shared": ROOT / ".claude-plugin" / "marketplace.json",
    "codex": ROOT / ".agents" / "plugins" / "marketplace.json",
}
PLUGIN_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
ACTION_REFERENCE = re.compile(r"^\s*uses:\s+([^@\s]+)@([^\s#]+)", re.MULTILINE)
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
SCENARIO_TYPES = {"positive", "failure", "unsafe"}
SCENARIO_FIELDS = {
    "id",
    "type",
    "platforms",
    "prompt",
    "setup",
    "expected",
    "must_not",
}
PLATFORMS = {"claude-code", "codex", "cursor", "github-copilot"}
MATURITY_LEVELS = ("experimental", "candidate", "stable")
# Experimental makes no behavioral claim, so it needs no recorded results.
REVIEWED_MATURITY = set(MATURITY_LEVELS) - {"experimental"}
ACCEPTANCE_FIELDS = {"plugin", "maturity", "results"}
RESULT_FIELDS = {
    "scenario",
    "platform",
    "plugin_version",
    "commit",
    "reviewed_on",
    "reviewer",
    "outcome",
}
RESULT_OPTIONAL_FIELDS = {"notes"}
RESULT_OUTCOMES = {"pass", "fail"}
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
MATURITY_CLAIM = re.compile(
    r"\b(Experimental|Candidate|Stable)\b\s*[—-]\s*(\d+\.\d+\.\d+[0-9A-Za-z.-]*)"
)

errors: list[str] = []


def fail(path: Path, message: str) -> None:
    """Record a validation error relative to the repository root."""
    try:
        display_path = path.relative_to(ROOT)
    except ValueError:
        display_path = path
    errors.append(f"{display_path}: {message}")


def load_json(path: Path) -> Any:
    """Load JSON and return an empty object after recording a failure."""
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        fail(path, "required file is missing")
    except json.JSONDecodeError as error:
        fail(path, f"invalid JSON at line {error.lineno}, column {error.colno}")
    return {}


def require_object(path: Path, value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(path, f"{context} must be an object")
        return {}
    return value


def require_text(path: Path, value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(path, f"{field} must be a non-empty string")
        return ""
    return value


def validate_marketplaces() -> dict[str, dict[str, dict[str, Any]]]:
    catalogs: dict[str, dict[str, dict[str, Any]]] = {}

    for platform, path in MARKETPLACES.items():
        data = require_object(path, load_json(path), "marketplace")
        name = require_text(path, data.get("name"), "name")
        if name != "tashtit":
            fail(path, "name must be 'tashtit'")

        plugins = data.get("plugins")
        if not isinstance(plugins, list):
            fail(path, "plugins must be an array")
            plugins = []

        entries: dict[str, dict[str, Any]] = {}
        for index, raw_entry in enumerate(plugins):
            entry = require_object(path, raw_entry, f"plugins[{index}]")
            plugin_name = require_text(path, entry.get("name"), f"plugins[{index}].name")
            if plugin_name and not PLUGIN_NAME.fullmatch(plugin_name):
                fail(path, f"invalid plugin name: {plugin_name!r}")
            if plugin_name in entries:
                fail(path, f"duplicate plugin entry: {plugin_name}")
            entries[plugin_name] = entry

            if platform == "shared":
                expected_source = f"./plugins/{plugin_name}"
                if entry.get("source") != expected_source:
                    fail(path, f"{plugin_name} source must be {expected_source!r}")
            else:
                source = require_object(path, entry.get("source"), f"{plugin_name}.source")
                if source != {"source": "local", "path": f"./plugins/{plugin_name}"}:
                    fail(path, f"{plugin_name} must use the repository-local source object")
                policy = require_object(path, entry.get("policy"), f"{plugin_name}.policy")
                if policy.get("installation") not in {
                    "NOT_AVAILABLE",
                    "AVAILABLE",
                    "INSTALLED_BY_DEFAULT",
                }:
                    fail(path, f"{plugin_name} has an invalid installation policy")
                if policy.get("authentication") not in {"ON_INSTALL", "ON_USE"}:
                    fail(path, f"{plugin_name} has an invalid authentication policy")
                require_text(path, entry.get("category"), f"{plugin_name}.category")

        names = list(entries)
        if names != sorted(names):
            fail(path, "plugins must be sorted by name")
        catalogs[platform] = entries

    shared_names = set(catalogs.get("shared", {}))
    codex_names = set(catalogs.get("codex", {}))
    if codex_names != shared_names:
        fail(
            MARKETPLACES["codex"],
            f"plugin set differs from shared marketplace: "
            f"{sorted(codex_names ^ shared_names)}",
        )

    return catalogs


def validate_plugins(shared: dict[str, dict[str, Any]]) -> None:
    plugins_root = ROOT / "plugins"
    plugin_dirs = sorted(
        path
        for path in plugins_root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    )
    catalog_names = set(shared)
    directory_names = {path.name for path in plugin_dirs}

    if directory_names != catalog_names:
        missing = sorted(directory_names - catalog_names)
        stale = sorted(catalog_names - directory_names)
        if missing:
            fail(plugins_root, f"plugins missing from marketplaces: {missing}")
        if stale:
            fail(plugins_root, f"marketplace entries without plugin directories: {stale}")

    for plugin_dir in plugin_dirs:
        name = plugin_dir.name
        if not PLUGIN_NAME.fullmatch(name):
            fail(plugin_dir, "directory name must use lowercase kebab-case")

        manifests = {
            "shared": plugin_dir / ".claude-plugin" / "plugin.json",
            "codex": plugin_dir / ".codex-plugin" / "plugin.json",
        }

        redundant_manifest = plugin_dir / "plugin.json"
        if redundant_manifest.exists() or redundant_manifest.is_symlink():
            fail(
                redundant_manifest,
                "duplicate manifest is prohibited; no supported host reads it",
            )

        loaded: dict[str, dict[str, Any]] = {}
        for platform, path in manifests.items():
            if path.is_symlink():
                fail(
                    path,
                    "manifest must be a regular file; a symlink becomes plain "
                    "text when core.symlinks=false and no host can parse it",
                )
            manifest = require_object(path, load_json(path), "plugin manifest")
            loaded[platform] = manifest
            if manifest.get("name") != name:
                fail(path, f"name must match plugin directory {name!r}")

        portable_version = shared.get(name, {}).get("version")
        portable_description = shared.get(name, {}).get("description")
        for platform, manifest in loaded.items():
            if manifest.get("version") != portable_version:
                fail(manifests[platform], "version differs across provider adapters")
            if manifest.get("description") != portable_description:
                fail(
                    manifests[platform],
                    "description differs from the shared marketplace",
                )
            if manifest.get("license") != "Apache-2.0":
                fail(manifests[platform], "license must be 'Apache-2.0'")

        skill_file = plugin_dir / "skills" / name / "SKILL.md"
        if not skill_file.is_file():
            fail(skill_file, "canonical skill is missing")


def parse_catalog_table(path: Path, prefix: str) -> dict[str, tuple[str, str]]:
    """Map plugin name to its listed version and maturity for each table row."""
    listed: dict[str, tuple[str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        targets = MARKDOWN_LINK.findall(cells[0])
        if len(targets) != 1:
            continue
        target = targets[0].strip()
        if not target.endswith("/"):
            continue
        if prefix and not target.startswith(prefix):
            continue
        name = target[len(prefix):].strip("./")
        if not PLUGIN_NAME.fullmatch(name):
            continue
        if name in listed:
            fail(path, f"duplicate catalog row for {name}")
        listed[name] = (cells[1], cells[2])
    return listed


def validate_catalog_tables(
    shared: dict[str, dict[str, Any]],
    maturity_by_plugin: dict[str, str],
) -> None:
    """Keep advertised catalogs identical to the canonical marketplace.

    A published table that disagrees with the marketplace is drift, so it is
    validated like any other generated-from-canonical artifact.
    """
    tables = {
        ROOT / "README.md": "plugins/",
        ROOT / "plugins" / "README.md": "",
    }
    for path, prefix in tables.items():
        if not path.is_file():
            fail(path, "required file is missing")
            continue

        listed = parse_catalog_table(path, prefix)
        expected_names = set(shared)
        missing = sorted(expected_names - set(listed))
        unexpected = sorted(set(listed) - expected_names)
        if missing:
            fail(path, f"catalog table is missing plugins: {missing}")
        if unexpected:
            fail(path, f"catalog table lists unknown plugins: {unexpected}")

        for name, (version, maturity) in sorted(listed.items()):
            expected_version = shared.get(name, {}).get("version")
            if expected_version and version != expected_version:
                fail(
                    path,
                    f"{name} is listed as version {version!r} but the "
                    f"marketplace declares {expected_version!r}",
                )
            expected_maturity = maturity_by_plugin.get(name)
            if expected_maturity and maturity.lower() != expected_maturity:
                fail(
                    path,
                    f"{name} is listed as maturity {maturity!r} but its "
                    f"acceptance record declares {expected_maturity!r}",
                )

        names = list(listed)
        if names != sorted(names):
            fail(path, "catalog table rows must be sorted by plugin name")


def validate_string_list(path: Path, value: Any, field: str) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item.strip() for item in value)
    ):
        fail(path, f"{field} must be a non-empty array of non-empty strings")
        return []
    return value


def validate_scenarios() -> dict[str, dict[str, set[str]]]:
    """Validate scenario shape and index each plugin's scenario platforms.

    The returned index is what makes the acceptance gate enforceable: it states
    exactly which scenario and platform pairs a non-experimental plugin must
    have recorded results for.
    """
    index: dict[str, dict[str, set[str]]] = {}
    seen_ids: set[str] = set()
    plugins_root = ROOT / "plugins"
    for plugin_dir in sorted(
        path
        for path in plugins_root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    ):
        plugin_scenarios = index.setdefault(plugin_dir.name, {})
        tests_root = ROOT / "tests" / "plugins" / plugin_dir.name
        review_path = tests_root / "REVIEW.md"
        if not review_path.is_file():
            fail(review_path, "human review checklist is missing")

        scenarios_dir = tests_root / "scenarios"
        scenario_paths = (
            sorted(scenarios_dir.glob("*.json"))
            if scenarios_dir.is_dir()
            else []
        )
        if not scenario_paths:
            fail(scenarios_dir, "at least one acceptance scenario is required")
            continue

        found_types: set[str] = set()
        for path in scenario_paths:
            scenario = require_object(path, load_json(path), "scenario")
            unknown_fields = set(scenario) - SCENARIO_FIELDS
            if unknown_fields:
                fail(path, f"unsupported fields: {sorted(unknown_fields)}")
            missing_fields = SCENARIO_FIELDS - set(scenario)
            if missing_fields:
                fail(path, f"missing fields: {sorted(missing_fields)}")

            scenario_id = require_text(path, scenario.get("id"), "id")
            if scenario_id:
                if not PLUGIN_NAME.fullmatch(scenario_id):
                    fail(path, "id must use lowercase kebab-case")
                if scenario_id in seen_ids:
                    fail(path, f"duplicate scenario id: {scenario_id}")
                seen_ids.add(scenario_id)

            scenario_type = require_text(path, scenario.get("type"), "type")
            if scenario_type not in SCENARIO_TYPES:
                fail(path, f"type must be one of {sorted(SCENARIO_TYPES)}")
            else:
                found_types.add(scenario_type)

            platforms = validate_string_list(
                path, scenario.get("platforms"), "platforms"
            )
            unknown_platforms = sorted(set(platforms) - PLATFORMS)
            if unknown_platforms:
                fail(
                    path,
                    f"unsupported platforms {unknown_platforms}; "
                    f"expected values from {sorted(PLATFORMS)}",
                )
            if scenario_id:
                plugin_scenarios[scenario_id] = set(platforms) & PLATFORMS

            require_text(path, scenario.get("prompt"), "prompt")
            validate_string_list(path, scenario.get("setup"), "setup")
            validate_string_list(path, scenario.get("expected"), "expected")
            validate_string_list(path, scenario.get("must_not"), "must_not")

        missing_types = SCENARIO_TYPES - found_types
        if missing_types:
            fail(
                scenarios_dir,
                f"missing required scenario types: {sorted(missing_types)}",
            )

    return index


def validate_acceptance_results(
    path: Path,
    scenarios: dict[str, set[str]],
    results: Any,
) -> dict[tuple[str, str], set[str]]:
    """Validate recorded review results and index passes by scenario platform.

    Each entry records one reviewed scenario and platform pair. The index maps
    that pair to the plugin versions it passed on, so the gate can require a
    pass at the version being published rather than at any version ever
    reviewed.
    """
    passes: dict[tuple[str, str], set[str]] = {}
    if not isinstance(results, list):
        fail(path, "results must be an array")
        return passes

    seen: set[tuple[str, str, str]] = set()
    for position, entry in enumerate(results):
        label = f"results[{position}]"
        if not isinstance(entry, dict):
            fail(path, f"{label} must be an object")
            continue

        unknown = set(entry) - RESULT_FIELDS - RESULT_OPTIONAL_FIELDS
        if unknown:
            fail(path, f"{label} has unsupported fields: {sorted(unknown)}")
        missing = RESULT_FIELDS - set(entry)
        if missing:
            fail(path, f"{label} is missing fields: {sorted(missing)}")
            continue

        scenario = entry["scenario"]
        platform = entry["platform"]
        version = entry["plugin_version"]
        commit = entry["commit"]
        reviewed_on = entry["reviewed_on"]
        outcome = entry["outcome"]

        if not require_text(path, entry.get("reviewer"), f"{label}.reviewer"):
            continue
        if scenario not in scenarios:
            fail(path, f"{label} references unknown scenario {scenario!r}")
            continue
        if platform not in scenarios[scenario]:
            fail(
                path,
                f"{label} reviews {scenario!r} on {platform!r}, which the "
                "scenario does not claim",
            )
            continue
        if not isinstance(version, str) or not SEMVER.fullmatch(version):
            fail(path, f"{label}.plugin_version must be a semantic version")
            continue
        if not isinstance(commit, str) or not FULL_SHA.fullmatch(commit):
            fail(
                path,
                f"{label}.commit must be a full lowercase 40-character commit "
                "SHA so the reviewed content is unambiguous",
            )
        if not isinstance(reviewed_on, str) or not ISO_DATE.fullmatch(
            reviewed_on
        ):
            fail(path, f"{label}.reviewed_on must be an ISO 8601 date")
        if outcome not in RESULT_OUTCOMES:
            fail(path, f"{label}.outcome must be one of {sorted(RESULT_OUTCOMES)}")
            continue

        key = (scenario, platform, version)
        if key in seen:
            fail(
                path,
                f"{label} duplicates the review of {scenario!r} on "
                f"{platform!r} at version {version}",
            )
        seen.add(key)

        if outcome == "pass":
            passes.setdefault((scenario, platform), set()).add(version)

    return passes


def validate_acceptance(
    shared: dict[str, dict[str, Any]],
    scenario_index: dict[str, dict[str, set[str]]],
) -> dict[str, str]:
    """Enforce the maturity gate against recorded behavioral review results.

    Scenarios describe required behavior but nothing executes them, so a
    maturity claim above experimental is only credible when a human or
    evaluation runner has recorded a passing result for every scenario and
    platform pair at the published version.
    """
    maturity_by_plugin: dict[str, str] = {}
    for name in sorted(scenario_index):
        path = ROOT / "tests" / "plugins" / name / "acceptance.json"
        if not path.is_file():
            fail(path, "acceptance record is missing")
            continue

        record = require_object(path, load_json(path), "acceptance record")
        unknown = set(record) - ACCEPTANCE_FIELDS
        if unknown:
            fail(path, f"unsupported fields: {sorted(unknown)}")
        missing = ACCEPTANCE_FIELDS - set(record)
        if missing:
            fail(path, f"missing fields: {sorted(missing)}")

        if record.get("plugin") != name:
            fail(path, f"plugin must be {name!r}")

        maturity = record.get("maturity")
        if maturity not in MATURITY_LEVELS:
            fail(path, f"maturity must be one of {list(MATURITY_LEVELS)}")
            continue
        maturity_by_plugin[name] = maturity

        scenarios = scenario_index.get(name, {})
        passes = validate_acceptance_results(
            path, scenarios, record.get("results")
        )
        if maturity not in REVIEWED_MATURITY:
            continue

        version = shared.get(name, {}).get("version")
        if not isinstance(version, str):
            continue

        unreviewed = sorted(
            f"{scenario} on {platform}"
            for scenario, platforms in scenarios.items()
            for platform in sorted(platforms)
            if version not in passes.get((scenario, platform), set())
        )
        if unreviewed:
            fail(
                path,
                f"maturity {maturity!r} requires a recorded pass at version "
                f"{version} for every scenario and platform; missing: "
                f"{unreviewed}",
            )

    return maturity_by_plugin


def validate_maturity_claims(maturity_by_plugin: dict[str, str]) -> None:
    """Keep each plugin's advertised maturity aligned with its record."""
    for name, maturity in sorted(maturity_by_plugin.items()):
        path = ROOT / "plugins" / name / "README.md"
        if not path.is_file():
            continue
        claims = MATURITY_CLAIM.findall(path.read_text(encoding="utf-8"))
        if not claims:
            fail(
                path,
                "must state maturity and version as "
                "'<Experimental|Candidate|Stable> — <version>'",
            )
            continue
        for level, _version in claims:
            if level.lower() != maturity:
                fail(
                    path,
                    f"advertises maturity {level!r} but the acceptance record "
                    f"declares {maturity!r}",
                )


def validate_json_files() -> None:
    for path in ROOT.rglob("*.json"):
        if ".git" in path.parts or ".idea" in path.parts:
            continue
        data = load_json(path)
        try:
            raw = path.read_text(encoding="utf-8")
        except (FileNotFoundError, UnicodeDecodeError):
            continue
        if isinstance(data, (dict, list)) and data and "\n" not in raw.strip():
            fail(
                path,
                "JSON must be pretty-printed across multiple lines, not "
                "collapsed onto a single line",
            )


def validate_action_pins() -> None:
    workflows = ROOT / ".github" / "workflows"
    for path in workflows.glob("*.yml"):
        content = path.read_text(encoding="utf-8")
        for action, reference in ACTION_REFERENCE.findall(content):
            if not FULL_SHA.fullmatch(reference):
                fail(
                    path,
                    f"{action} must be pinned to a full 40-character commit SHA",
                )


def validate_retired_branding() -> None:
    retired_name = "open" + "rigor"
    for path in ROOT.rglob("*"):
        if (
            not path.is_file()
            or path.is_symlink()
            or ".git" in path.parts
            or ".idea" in path.parts
        ):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if retired_name in content.casefold():
            fail(path, "contains the retired project name")


def validate_links() -> None:
    for directory, directory_names, file_names in os.walk(ROOT, followlinks=False):
        directory_path = Path(directory)
        if ".git" in directory_path.parts or ".idea" in directory_path.parts:
            directory_names[:] = []
            continue
        for name in [*directory_names, *file_names]:
            path = directory_path / name
            if not path.is_symlink():
                continue
            if Path(os.readlink(path)).is_absolute():
                fail(path, "link target must be repository-relative")
            try:
                resolved = path.resolve(strict=True)
            except FileNotFoundError:
                fail(path, "link target does not exist")
                continue
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                fail(path, "link target escapes the repository")

    redundant_marketplace = ROOT / ".github" / "plugin" / "marketplace.json"
    if redundant_marketplace.exists() and not redundant_marketplace.is_symlink():
        fail(
            redundant_marketplace,
            "duplicate marketplace is prohibited; Copilot reuses .claude-plugin",
        )


def validate_markdown_links() -> None:
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts or ".idea" in path.parts:
            continue
        content = path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK.findall(content):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if (
                not target
                or target.startswith(("#", "http://", "https://", "mailto:"))
            ):
                continue
            relative_target = unquote(target.split("#", 1)[0])
            resolved = (path.parent / relative_target).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                fail(path, f"local link escapes repository: {target}")
                continue
            if not resolved.exists():
                fail(path, f"broken local link: {target}")


def _load_schema(name: str) -> dict[str, Any] | None:
    path = SCHEMAS_DIR / name
    schema = load_json(path)
    if not isinstance(schema, dict):
        fail(path, "schema must be a JSON object")
        return None
    return schema


def validate_schemas() -> None:
    """Check scenario and acceptance files against their published schemas.

    The schema files in `schemas/` are the canonical structural contract. The
    richer cross-file rules (id uniqueness, sorting, and the maturity gate) stay
    in this script; schema validation guarantees each document's shape matches
    the contract consumers can read.
    """
    scenario_schema = _load_schema("scenario.schema.json")
    acceptance_schema = _load_schema("acceptance.schema.json")
    if scenario_schema is None or acceptance_schema is None:
        return

    tests_root = ROOT / "tests" / "plugins"
    if not tests_root.is_dir():
        return

    try:
        for path in sorted(tests_root.rglob("scenarios/*.json")):
            for message in validate_instance(load_json(path), scenario_schema):
                fail(path, f"schema: {message}")
        for path in sorted(tests_root.glob("*/acceptance.json")):
            for message in validate_instance(load_json(path), acceptance_schema):
                fail(path, f"schema: {message}")
    except SchemaError as error:
        fail(SCHEMAS_DIR, f"schema definition is invalid: {error}")


def main() -> int:
    catalogs = validate_marketplaces()
    shared = catalogs.get("shared", {})
    validate_plugins(shared)
    scenario_index = validate_scenarios()
    maturity_by_plugin = validate_acceptance(shared, scenario_index)
    validate_maturity_claims(maturity_by_plugin)
    validate_catalog_tables(shared, maturity_by_plugin)
    validate_schemas()
    validate_json_files()
    validate_action_pins()
    validate_retired_branding()
    validate_links()
    validate_markdown_links()

    if errors:
        print("Tashtit validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Tashtit validation passed "
        f"({len(shared)} shared marketplace entries)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
