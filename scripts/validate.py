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


ROOT = Path(__file__).resolve().parent.parent
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
        if redundant_manifest.exists() and not redundant_manifest.is_symlink():
            fail(
                redundant_manifest,
                "duplicate manifest is prohibited; reuse or link the shared manifest",
            )

        loaded: dict[str, dict[str, Any]] = {}
        for platform, path in manifests.items():
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


def validate_string_list(path: Path, value: Any, field: str) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item.strip() for item in value)
    ):
        fail(path, f"{field} must be a non-empty array of non-empty strings")
        return []
    return value


def validate_scenarios() -> None:
    seen_ids: set[str] = set()
    plugins_root = ROOT / "plugins"
    for plugin_dir in sorted(
        path
        for path in plugins_root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    ):
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

            validate_string_list(path, scenario.get("platforms"), "platforms")
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


def main() -> int:
    catalogs = validate_marketplaces()
    shared = catalogs.get("shared", {})
    validate_plugins(shared)
    validate_scenarios()
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
