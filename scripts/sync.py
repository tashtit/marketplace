#!/usr/bin/env python3
"""Generate Tashtit's Codex adapters from their canonical sources.

Codex requires two files that cannot live at the shared Claude/Copilot paths:

- `.agents/plugins/marketplace.json`, whose catalog schema differs;
- `.codex-plugin/plugin.json` per plugin, whose content matches the shared
  manifest but whose location is fixed by the host.

Both are generated here and drift-checked by `make validate`. Repository
symlinks are deliberately not used: Git materializes them as plain text files
when `core.symlinks=false`, which is the default whenever a checkout cannot
create symlinks, and a host would then read the link target instead of JSON.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
SHARED_MARKETPLACE_PATH = ROOT / ".claude-plugin" / "marketplace.json"
CODEX_MARKETPLACE_PATH = ROOT / ".agents" / "plugins" / "marketplace.json"
PLUGINS_ROOT = ROOT / "plugins"
SHARED_MANIFEST_DIR = ".claude-plugin"
CODEX_MANIFEST_DIR = ".codex-plugin"
DISPLAY_NAME = "Tashtit"
PLUGIN_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PLATFORMS = {"claude-code", "codex", "cursor", "github-copilot"}
# Platforms a plugin targets by default when it declares no `platforms` list.
# Cursor is optional research, so it is opt-in rather than a default target.
CORE_TARGETS = {"claude-code", "codex", "github-copilot"}
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
REQUIRED_MANIFEST_FIELDS = ("name", "version", "description", "skills")


class SyncError(ValueError):
    """Raised when a canonical source cannot be trusted for generation."""


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def require_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SyncError(f"{field} must be an object")
    return value


def require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SyncError(f"{field} must be a non-empty string")
    return value


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise SyncError(f"missing canonical source: {relative(path)}") from error
    except json.JSONDecodeError as error:
        raise SyncError(
            f"{relative(path)}: invalid JSON at line {error.lineno}, "
            f"column {error.colno}"
        ) from error


def load_shared_marketplace() -> dict[str, Any]:
    marketplace = require_object(read_json(SHARED_MARKETPLACE_PATH), "marketplace")
    if require_text(marketplace.get("name"), "name") != "tashtit":
        raise SyncError("name must be 'tashtit'")
    owner = require_object(marketplace.get("owner"), "owner")
    require_text(owner.get("name"), "owner.name")
    metadata = require_object(marketplace.get("metadata"), "metadata")
    require_text(metadata.get("description"), "metadata.description")
    if not SEMVER.fullmatch(
        require_text(metadata.get("version"), "metadata.version")
    ):
        raise SyncError("metadata.version must use Semantic Versioning")

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        raise SyncError("plugins must be an array")

    names: list[str] = []
    for index, raw_plugin in enumerate(plugins):
        plugin = require_object(raw_plugin, f"plugins[{index}]")
        prefix = f"plugins[{index}]"
        name = require_text(plugin.get("name"), f"{prefix}.name")
        if not PLUGIN_NAME.fullmatch(name):
            raise SyncError(f"{prefix}.name must use lowercase kebab-case")
        names.append(name)
        if plugin.get("source") != f"./plugins/{name}":
            raise SyncError(f"{prefix}.source must be './plugins/{name}'")
        require_text(plugin.get("description"), f"{prefix}.description")
        if not SEMVER.fullmatch(
            require_text(plugin.get("version"), f"{prefix}.version")
        ):
            raise SyncError(f"{prefix}.version must use Semantic Versioning")
        if plugin.get("license") != "Apache-2.0":
            raise SyncError(f"{prefix}.license must be 'Apache-2.0'")
        require_text(plugin.get("category"), f"{prefix}.category")
        platforms = plugin.get("platforms")
        if platforms is not None:
            if (
                not isinstance(platforms, list)
                or not platforms
                or any(not isinstance(item, str) for item in platforms)
            ):
                raise SyncError(
                    f"{prefix}.platforms must be a non-empty array of strings"
                )
            unknown = sorted(set(platforms) - PLATFORMS)
            if unknown:
                raise SyncError(f"{prefix}.platforms has unknown platforms {unknown}")

    if names != sorted(names):
        raise SyncError("plugins must be sorted by name")
    if len(names) != len(set(names)):
        raise SyncError("plugin names must be unique")
    return marketplace


def targets_codex(entry: dict[str, Any]) -> bool:
    """Whether a plugin gets a generated Codex adapter.

    A plugin targets every core platform unless it declares a narrower
    `platforms` list. Codex is the only platform with a separately generated
    adapter, so omitting it from `platforms` suppresses that adapter while the
    shared Claude/Copilot manifest is unaffected.
    """
    platforms = entry.get("platforms")
    if platforms is None:
        return "codex" in CORE_TARGETS
    return "codex" in platforms


def build_codex_marketplace(marketplace: dict[str, Any]) -> dict[str, Any]:
    """Translate the shared entries to Codex's incompatible catalog schema."""
    plugins = []
    for plugin in marketplace["plugins"]:
        if not targets_codex(plugin):
            continue
        plugins.append(
            {
                "name": plugin["name"],
                "source": {
                    "source": "local",
                    "path": f"./plugins/{plugin['name']}",
                },
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": plugin["category"],
            }
        )
    return {
        "name": marketplace["name"],
        "interface": {"displayName": DISPLAY_NAME},
        "plugins": plugins,
    }


def plugin_directories() -> list[Path]:
    if not PLUGINS_ROOT.is_dir():
        raise SyncError(f"missing plugins directory: {relative(PLUGINS_ROOT)}")
    return sorted(
        path
        for path in PLUGINS_ROOT.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    )


def load_shared_manifest(path: Path, plugin_name: str) -> str:
    """Return the canonical manifest text once Codex's requirements hold.

    Codex accepts the shared manifest schema, so the generated file is a byte
    copy. Validate here rather than emitting an adapter a host cannot load.
    """
    manifest = require_object(read_json(path), f"{relative(path)} manifest")
    if manifest.get("name") != plugin_name:
        raise SyncError(f"{relative(path)}: name must be {plugin_name!r}")
    for field in REQUIRED_MANIFEST_FIELDS:
        require_text(manifest.get(field), f"{relative(path)}.{field}")
    if not SEMVER.fullmatch(manifest["version"]):
        raise SyncError(f"{relative(path)}: version must use Semantic Versioning")
    if not manifest["skills"].startswith("./"):
        raise SyncError(f"{relative(path)}: skills path must start with './'")
    return path.read_text(encoding="utf-8")


def render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def collect_artifacts() -> tuple[list[tuple[Path, str]], list[Path]]:
    """Pair every generated path with the content its canonical source implies.

    Also returns the generated adapters that must no longer exist, so that a
    plugin dropping codex from its platforms is remediated by `make sync`
    instead of leaving an adapter that only `make validate` complains about.
    """
    marketplace = load_shared_marketplace()
    codex_targets = {
        plugin["name"]
        for plugin in marketplace["plugins"]
        if targets_codex(plugin)
    }
    artifacts = [
        (CODEX_MARKETPLACE_PATH, render(build_codex_marketplace(marketplace)))
    ]
    obsolete: list[Path] = []
    for plugin_dir in plugin_directories():
        adapter = plugin_dir / CODEX_MANIFEST_DIR / "plugin.json"
        if plugin_dir.name not in codex_targets:
            if adapter.is_file() or adapter.is_symlink():
                obsolete.append(adapter)
            continue
        shared_manifest = plugin_dir / SHARED_MANIFEST_DIR / "plugin.json"
        artifacts.append(
            (adapter, load_shared_manifest(shared_manifest, plugin_dir.name))
        )
    return artifacts, obsolete


def sync_artifact(path: Path, expected: str, check: bool) -> bool:
    """Write or verify one generated file, replacing any symlink in place."""
    linked = path.is_symlink()
    actual = path.read_text(encoding="utf-8") if path.is_file() else ""
    if not linked and actual == expected:
        return True

    if check:
        if linked:
            print(
                f"{relative(path)}: must be a generated regular file, not a "
                "symlink; symlinks become plain text when core.symlinks=false",
                file=sys.stderr,
            )
            return False
        sys.stderr.writelines(
            difflib.unified_diff(
                actual.splitlines(keepends=True),
                expected.splitlines(keepends=True),
                fromfile=relative(path),
                tofile=f"{relative(path)} (generated)",
            )
        )
        return False

    if linked:
        path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(expected, encoding="utf-8")
    print(f"updated {relative(path)}")
    return True


def remove_obsolete(path: Path, check: bool) -> bool:
    """Remove one adapter whose plugin no longer targets codex."""
    if check:
        print(
            f"{relative(path)}: plugin no longer targets codex, so its "
            "generated adapter must be removed",
            file=sys.stderr,
        )
        return False
    path.unlink()
    try:
        path.parent.rmdir()
    except OSError:
        # The directory holds files this script does not generate; validation
        # will report them if they are a problem.
        pass
    print(f"removed {relative(path)}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if a generated Codex adapter is out of date",
    )
    args = parser.parse_args()

    try:
        artifacts, obsolete = collect_artifacts()
    except SyncError as error:
        print(f"canonical source validation failed: {error}", file=sys.stderr)
        return 1

    stale = [
        path
        for path, expected in artifacts
        if not sync_artifact(path, expected, args.check)
    ]
    stale.extend(
        path for path in obsolete if not remove_obsolete(path, args.check)
    )
    if stale:
        print(
            "Generated Codex adapters are stale; run `make sync` and include "
            "the result",
            file=sys.stderr,
        )
        return 1
    if args.check:
        print(f"Generated Codex adapters are synchronized ({len(artifacts)} files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
