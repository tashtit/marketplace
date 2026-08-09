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
# A step may open with "- uses:" or carry "uses:" on its own line; both forms
# reference an action and both must satisfy the pinning rule.
ACTION_REFERENCE = re.compile(
    r"^\s*(?:-\s+)?uses:\s+([^@\s]+)@([^\s#]+)", re.MULTILINE
)
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
# A GitHub-authored action may use an exact release tag. A movable major tag
# such as "v7" or a branch name stays forbidden because it is not immutable.
GITHUB_AUTHORED_OWNERS = ("actions/", "github/")
EXACT_RELEASE_TAG = re.compile(r"^v\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
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
# Platforms a plugin targets by default when it declares no `platforms` list.
# Cursor is optional research, so it is opt-in rather than a default target.
CORE_TARGETS = {"claude-code", "codex", "github-copilot"}
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
    r"\b(Experimental|Candidate|Stable)\b\s*[—-]\s*"
    r"(\d+\.\d+\.\d+(?:[0-9A-Za-z.-]*[0-9A-Za-z])?)"
)
FRONTMATTER_FIELD = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$")
# The portable Agent Skills convention caps a skill description. A longer one
# risks truncation or rejection by a host, which silently weakens triggering.
SKILL_DESCRIPTION_LIMIT = 1024

errors: list[str] = []

# Directories that never carry repository content: version control and editor
# state, plus installed dependencies. Kept in one place so every traversal
# skips the same paths.
IGNORED_DIRECTORIES = {".git", ".idea", "node_modules"}


def is_ignored(path: Path) -> bool:
    """Report whether a path sits inside a directory that is never validated."""
    return any(part in IGNORED_DIRECTORIES for part in path.parts)


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


def plugin_platforms(entry: dict[str, Any]) -> set[str]:
    """Return a plugin's declared target platforms, defaulting to core targets."""
    platforms = entry.get("platforms")
    if platforms is None:
        return set(CORE_TARGETS)
    # validate_marketplaces records the error for a malformed declaration;
    # fall back to the default so validation can continue past it.
    if not isinstance(platforms, list):
        return set(CORE_TARGETS)
    return {item for item in platforms if isinstance(item, str)} & PLATFORMS


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
                raw_platforms = entry.get("platforms")
                if raw_platforms is not None:
                    values = validate_string_list(
                        path, raw_platforms, f"{plugin_name}.platforms"
                    )
                    unknown = sorted(set(values) - PLATFORMS)
                    if unknown:
                        fail(
                            path,
                            f"{plugin_name}.platforms has unknown platforms "
                            f"{unknown}; expected values from {sorted(PLATFORMS)}",
                        )
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

    codex_targets = {
        name
        for name, entry in catalogs.get("shared", {}).items()
        if "codex" in plugin_platforms(entry)
    }
    codex_names = set(catalogs.get("codex", {}))
    if codex_names != codex_targets:
        fail(
            MARKETPLACES["codex"],
            f"plugin set differs from codex-targeted shared plugins: "
            f"{sorted(codex_names ^ codex_targets)}",
        )

    return catalogs


# Component fields in a Claude Code plugin manifest and the JSON type each
# must have. Claude Code rejects a manifest whose component field has the wrong
# type with a load error such as "agents: Invalid input", which silently breaks
# marketplace installation. `agents` and `commands` are arrays of file paths;
# the rest are string directory or file paths. See the plugin manifest schema:
# https://code.claude.com/docs/en/plugins-reference#complete-schema
MANIFEST_STRING_COMPONENTS = ("skills", "hooks", "mcpServers", "outputStyles", "lspServers")
MANIFEST_LIST_COMPONENTS = ("commands", "agents")


def validate_manifest_components(
    path: Path, plugin_dir: Path, manifest: dict[str, Any]
) -> None:
    """Enforce Claude Code's component field types and referenced paths.

    A wrong-typed component field (for example ``"agents": "./agents/"`` where
    the schema requires an array) loads cleanly as JSON but is rejected by the
    host at install time, so it must fail validation here instead.
    """
    for field in MANIFEST_STRING_COMPONENTS:
        if field not in manifest:
            continue
        value = manifest[field]
        if not isinstance(value, str) or not value.strip():
            fail(path, f"{field} must be a non-empty string path")
            continue
        if not (plugin_dir / value).exists():
            fail(path, f"{field} path {value!r} does not exist")

    for field in MANIFEST_LIST_COMPONENTS:
        if field not in manifest:
            continue
        value = manifest[field]
        if not isinstance(value, list) or not value:
            fail(
                path,
                f"{field} must be a non-empty array of file paths, not "
                f"{type(value).__name__}",
            )
            continue
        for item in value:
            if not isinstance(item, str) or not item.strip():
                fail(path, f"{field} entries must be non-empty string paths")
                continue
            if not (plugin_dir / item).is_file():
                fail(path, f"{field} path {item!r} is not a file")


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
        }
        codex_manifest = plugin_dir / ".codex-plugin" / "plugin.json"
        if "codex" in plugin_platforms(shared.get(name, {})):
            manifests["codex"] = codex_manifest
        elif codex_manifest.exists() or codex_manifest.is_symlink():
            fail(
                codex_manifest,
                "plugin does not target codex, so its generated .codex-plugin "
                "adapter must be absent",
            )

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
            validate_manifest_components(manifests[platform], plugin_dir, manifest)

        skill_file = plugin_dir / "skills" / name / "SKILL.md"
        if not skill_file.is_file():
            fail(skill_file, "canonical skill is missing")


def parse_frontmatter(path: Path) -> dict[str, str]:
    """Parse a SKILL.md frontmatter block of single-line key: value fields.

    The frontmatter is what every supported host loads to decide whether a
    skill triggers, so it is validated strictly: it must open the file, be
    closed, and contain only blank lines and single-line scalar fields.
    Anything more exotic risks parsing differently across hosts.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        fail(path, "must begin with a '---' frontmatter block")
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        if not line.strip():
            continue
        match = FRONTMATTER_FIELD.match(line)
        if not match:
            fail(
                path,
                "frontmatter must contain only single-line 'key: value' "
                f"fields; cannot parse: {line!r}",
            )
            continue
        key, value = match.groups()
        value = value.strip()
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            value = value[1:-1].replace('\\"', '"')
        if key in fields:
            fail(path, f"duplicate frontmatter field {key!r}")
        fields[key] = value
    fail(path, "frontmatter block is never closed with '---'")
    return fields


def validate_skill_frontmatter() -> None:
    """Validate the trigger surface each host loads for every skill.

    Hosts select skills from the frontmatter name and description alone and
    flatten every installed skill into one namespace, so a malformed name, a
    missing description, or a name collision breaks routing without producing
    any load error a user would see.
    """
    seen: dict[str, Path] = {}
    for path in sorted((ROOT / "plugins").glob("*/skills/*/SKILL.md")):
        fields = parse_frontmatter(path)
        name = fields.get("name", "")
        if not name:
            fail(path, "frontmatter must declare a name")
        elif name != path.parent.name:
            fail(
                path,
                f"frontmatter name {name!r} must match the skill directory "
                f"{path.parent.name!r}",
            )
        elif not PLUGIN_NAME.fullmatch(name):
            fail(path, "frontmatter name must use lowercase kebab-case")
        elif name in seen:
            fail(
                path,
                f"skill name {name!r} is already used by "
                f"{seen[name].relative_to(ROOT)}; hosts flatten installed "
                "skills into one namespace",
            )
        else:
            seen[name] = path

        description = fields.get("description", "")
        if not description.strip():
            fail(path, "frontmatter must declare a non-empty description")
        elif len(description) > SKILL_DESCRIPTION_LIMIT:
            fail(
                path,
                f"description is {len(description)} characters, above the "
                f"{SKILL_DESCRIPTION_LIMIT}-character skill description limit",
            )


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


def validate_scenarios(
    shared: dict[str, dict[str, Any]],
) -> dict[str, dict[str, set[str]]]:
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
        declared_platforms = plugin_platforms(shared.get(plugin_dir.name, {}))
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
            undeclared_platforms = sorted(
                (set(platforms) & PLATFORMS) - declared_platforms
            )
            if undeclared_platforms:
                fail(
                    path,
                    f"platforms {undeclared_platforms} are not declared by "
                    f"{plugin_dir.name}; expected values from "
                    f"{sorted(declared_platforms)}",
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


def validate_test_directories() -> None:
    """Reject test trees for plugins that no longer exist.

    A deleted or renamed plugin would otherwise leave its acceptance record,
    scenarios, and review checklist behind forever, silently advertising
    coverage for something the marketplace no longer ships.
    """
    tests_root = ROOT / "tests" / "plugins"
    if not tests_root.is_dir():
        return
    plugin_names = {
        path.name
        for path in (ROOT / "plugins").iterdir()
        if path.is_dir() and not path.name.startswith(".")
    }
    for path in sorted(tests_root.iterdir()):
        if not path.is_dir() or path.name.startswith("."):
            continue
        if path.name not in plugin_names:
            fail(path, "test directory has no matching plugin under plugins/")


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


def validate_maturity_claims(
    shared: dict[str, dict[str, Any]],
    maturity_by_plugin: dict[str, str],
) -> None:
    """Keep each plugin's advertised maturity and version aligned."""
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
        published_version = shared.get(name, {}).get("version")
        for level, version in claims:
            if level.lower() != maturity:
                fail(
                    path,
                    f"advertises maturity {level!r} but the acceptance record "
                    f"declares {maturity!r}",
                )
            if isinstance(published_version, str) and version != published_version:
                fail(
                    path,
                    f"advertises version {version} but the published version "
                    f"is {published_version}",
                )


def validate_json_files() -> None:
    for path in ROOT.rglob("*.json"):
        if is_ignored(path):
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
    """Enforce the pinning rule documented in github-actions-standards.

    Any remote action may use a full commit SHA. An action published by GitHub
    itself may instead use an exact release tag, which this repository accepts
    because CI holds no secrets, write permissions, or deployment authority.
    """
    workflows = ROOT / ".github" / "workflows"
    for path in sorted(workflows.glob("*.yml")) + sorted(workflows.glob("*.yaml")):
        content = path.read_text(encoding="utf-8")
        for action, reference in ACTION_REFERENCE.findall(content):
            if FULL_SHA.fullmatch(reference):
                continue
            if action.startswith(("./", "docker://")):
                continue
            github_authored = action.startswith(GITHUB_AUTHORED_OWNERS)
            if github_authored and EXACT_RELEASE_TAG.fullmatch(reference):
                continue
            if github_authored:
                fail(
                    path,
                    f"{action} must use a full 40-character commit SHA or an "
                    f"exact release tag such as v1.2.3, not {reference!r}",
                )
            else:
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
            or is_ignored(path)
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
        if is_ignored(directory_path):
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
        if is_ignored(path):
            continue
        content = path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK.findall(content):
            tokens = raw_target.split(maxsplit=1)
            if not tokens:
                fail(path, "markdown link target is blank")
                continue
            target = tokens[0].strip("<>")
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
    validate_skill_frontmatter()
    scenario_index = validate_scenarios(shared)
    validate_test_directories()
    maturity_by_plugin = validate_acceptance(shared, scenario_index)
    validate_maturity_claims(shared, maturity_by_plugin)
    validate_catalog_tables(shared, maturity_by_plugin)
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
