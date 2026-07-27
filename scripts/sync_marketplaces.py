#!/usr/bin/env python3
"""Generate the Codex marketplace from the shared standard marketplace."""

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
DISPLAY_NAME = "Tashtit"
PLUGIN_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


class MarketplaceError(ValueError):
    """Raised when the shared marketplace is invalid."""


def require_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise MarketplaceError(f"{field} must be an object")
    return value


def require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MarketplaceError(f"{field} must be a non-empty string")
    return value


def load_shared_marketplace() -> dict[str, Any]:
    try:
        marketplace = json.loads(
            SHARED_MARKETPLACE_PATH.read_text(encoding="utf-8")
        )
    except FileNotFoundError as error:
        raise MarketplaceError(
            f"missing shared marketplace: {SHARED_MARKETPLACE_PATH}"
        ) from error
    except json.JSONDecodeError as error:
        raise MarketplaceError(
            f"invalid marketplace JSON at line {error.lineno}, "
            f"column {error.colno}"
        ) from error

    marketplace = require_object(marketplace, "marketplace")
    if require_text(marketplace.get("name"), "name") != "tashtit":
        raise MarketplaceError("name must be 'tashtit'")
    owner = require_object(marketplace.get("owner"), "owner")
    require_text(owner.get("name"), "owner.name")
    metadata = require_object(marketplace.get("metadata"), "metadata")
    require_text(metadata.get("description"), "metadata.description")
    if not SEMVER.fullmatch(
        require_text(metadata.get("version"), "metadata.version")
    ):
        raise MarketplaceError("metadata.version must use Semantic Versioning")

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        raise MarketplaceError("plugins must be an array")

    names: list[str] = []
    for index, raw_plugin in enumerate(plugins):
        plugin = require_object(raw_plugin, f"plugins[{index}]")
        prefix = f"plugins[{index}]"
        name = require_text(plugin.get("name"), f"{prefix}.name")
        if not PLUGIN_NAME.fullmatch(name):
            raise MarketplaceError(f"{prefix}.name must use lowercase kebab-case")
        names.append(name)
        if plugin.get("source") != f"./plugins/{name}":
            raise MarketplaceError(
                f"{prefix}.source must be './plugins/{name}'"
            )
        require_text(plugin.get("description"), f"{prefix}.description")
        if not SEMVER.fullmatch(
            require_text(plugin.get("version"), f"{prefix}.version")
        ):
            raise MarketplaceError(f"{prefix}.version must use Semantic Versioning")
        if plugin.get("license") != "Apache-2.0":
            raise MarketplaceError(f"{prefix}.license must be 'Apache-2.0'")
        require_text(plugin.get("category"), f"{prefix}.category")

    if names != sorted(names):
        raise MarketplaceError("plugins must be sorted by name")
    if len(names) != len(set(names)):
        raise MarketplaceError("plugin names must be unique")
    return marketplace


def build_codex_marketplace(marketplace: dict[str, Any]) -> dict[str, Any]:
    """Translate the shared entries to Codex's incompatible schema."""
    plugins = []
    for plugin in marketplace["plugins"]:
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


def render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def sync_codex_marketplace(expected: str, check: bool) -> bool:
    actual = (
        CODEX_MARKETPLACE_PATH.read_text(encoding="utf-8")
        if CODEX_MARKETPLACE_PATH.exists()
        else ""
    )
    if actual == expected:
        return True

    if check:
        relative_path = CODEX_MARKETPLACE_PATH.relative_to(ROOT)
        diff = difflib.unified_diff(
            actual.splitlines(keepends=True),
            expected.splitlines(keepends=True),
            fromfile=str(relative_path),
            tofile=f"{relative_path} (generated)",
        )
        sys.stderr.writelines(diff)
        return False

    CODEX_MARKETPLACE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CODEX_MARKETPLACE_PATH.write_text(expected, encoding="utf-8")
    print(f"updated {CODEX_MARKETPLACE_PATH.relative_to(ROOT)}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the generated Codex marketplace is out of date",
    )
    args = parser.parse_args()

    try:
        marketplace = load_shared_marketplace()
    except MarketplaceError as error:
        print(f"shared marketplace validation failed: {error}", file=sys.stderr)
        return 1

    clean = sync_codex_marketplace(
        render(build_codex_marketplace(marketplace)),
        args.check,
    )
    if not clean:
        print(
            "Codex marketplace is stale; run `make sync` and include the result",
            file=sys.stderr,
        )
        return 1
    if args.check:
        print("Generated Codex marketplace is synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
