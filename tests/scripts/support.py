"""Shared fixtures for the repository script test suite.

`build_repo` writes a minimal repository tree that `scripts/validate.py`
accepts and `scripts/sync.py --check` reports as synchronized. Each test
mutates one aspect of that tree and asserts on the specific failure the
mutation causes, so a validator check that silently stops firing breaks a
test instead of shipping.

The path context managers exist because each script derives its paths from
a module-level ``ROOT`` at import time; pointing a script at a fixture tree
requires patching the derived globals together and restoring them afterward.
"""

from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

PLUGIN_VERSION = "1.0.0"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, value: Any) -> None:
    """Serialize exactly like scripts/sync.py renders generated artifacts."""
    write_text(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def mutate_json(path: Path, mutate: Callable[[Any], Any]) -> None:
    """Load a JSON file, apply a mutation, and write the result back."""
    value = read_json(path)
    write_json(path, mutate(value) or value)


def plugin_description(name: str) -> str:
    return f"Fixture plugin {name}."


def scenario(plugin: str, kind: str) -> dict[str, Any]:
    return {
        "id": f"{plugin}-{kind}-case",
        "type": kind,
        "platforms": ["claude-code"],
        "prompt": f"Exercise the {kind} path of {plugin}.",
        "setup": ["A repository prepared for the scenario."],
        "expected": ["The documented behavior is observed."],
        "must_not": ["No credential material appears in output."],
    }


def catalog_table(names: list[str], prefix: str) -> str:
    rows = "\n".join(
        f"| [{name}]({prefix}{name}/) | {PLUGIN_VERSION} | Experimental |"
        for name in sorted(names)
    )
    return (
        "| Plugin | Version | Maturity |\n"
        "| --- | --- | --- |\n"
        f"{rows}\n"
    )


def build_repo(root: Path, plugins: tuple[str, ...] = ("alpha",)) -> None:
    """Write a minimal repository tree that passes validation and sync."""
    names = sorted(plugins)

    write_json(
        root / ".claude-plugin" / "marketplace.json",
        {
            "name": "tashtit",
            "owner": {"name": "Fixture Maintainers"},
            "metadata": {
                "description": "Fixture marketplace for script tests.",
                "version": "0.1.0",
            },
            "plugins": [
                {
                    "name": name,
                    "source": f"./plugins/{name}",
                    "description": plugin_description(name),
                    "version": PLUGIN_VERSION,
                    "license": "Apache-2.0",
                    "category": "testing",
                }
                for name in names
            ],
        },
    )

    # The exact content scripts/sync.py is expected to generate; writing it
    # here makes `sync --check` on the clean fixture assert the generator.
    write_json(
        root / ".agents" / "plugins" / "marketplace.json",
        {
            "name": "tashtit",
            "interface": {"displayName": "Tashtit"},
            "plugins": [
                {
                    "name": name,
                    "source": {"source": "local", "path": f"./plugins/{name}"},
                    "policy": {
                        "installation": "AVAILABLE",
                        "authentication": "ON_INSTALL",
                    },
                    "category": "testing",
                }
                for name in names
            ],
        },
    )

    for name in names:
        plugin_dir = root / "plugins" / name
        manifest = {
            "name": name,
            "version": PLUGIN_VERSION,
            "description": plugin_description(name),
            "license": "Apache-2.0",
            "skills": "./skills",
        }
        write_json(plugin_dir / ".claude-plugin" / "plugin.json", manifest)
        write_json(plugin_dir / ".codex-plugin" / "plugin.json", manifest)
        write_text(
            plugin_dir / "skills" / name / "SKILL.md",
            "---\n"
            f"name: {name}\n"
            f"description: Fixture skill for {name}.\n"
            "---\n"
            "\n"
            "Use this fixture skill to exercise the validator.\n",
        )

        tests_dir = root / "tests" / "plugins" / name
        write_text(
            tests_dir / "REVIEW.md",
            f"# Review checklist for {name}\n\nReviewed for fixture use.\n",
        )
        write_json(
            tests_dir / "acceptance.json",
            {"plugin": name, "maturity": "experimental", "results": []},
        )
        for kind in ("positive", "failure", "unsafe"):
            write_json(
                tests_dir / "scenarios" / f"{kind}-case.json",
                scenario(name, kind),
            )

    write_text(
        root / "README.md",
        "# Fixture marketplace\n\n" + catalog_table(names, "plugins/"),
    )
    write_text(
        root / "plugins" / "README.md",
        "# Fixture plugins\n\n" + catalog_table(names, ""),
    )


@contextmanager
def validate_paths(root: Path):
    """Point scripts/validate.py at a fixture tree and reset its error state."""
    import validate

    saved = (validate.ROOT, validate.MARKETPLACES)
    validate.ROOT = root
    validate.MARKETPLACES = {
        "shared": root / ".claude-plugin" / "marketplace.json",
        "codex": root / ".agents" / "plugins" / "marketplace.json",
    }
    validate.errors.clear()
    try:
        yield validate
    finally:
        validate.ROOT, validate.MARKETPLACES = saved
        validate.errors.clear()


@contextmanager
def sync_paths(root: Path):
    """Point scripts/sync.py at a fixture tree."""
    import sync

    saved = (
        sync.ROOT,
        sync.SHARED_MARKETPLACE_PATH,
        sync.CODEX_MARKETPLACE_PATH,
        sync.PLUGINS_ROOT,
    )
    sync.ROOT = root
    sync.SHARED_MARKETPLACE_PATH = root / ".claude-plugin" / "marketplace.json"
    sync.CODEX_MARKETPLACE_PATH = root / ".agents" / "plugins" / "marketplace.json"
    sync.PLUGINS_ROOT = root / "plugins"
    try:
        yield sync
    finally:
        (
            sync.ROOT,
            sync.SHARED_MARKETPLACE_PATH,
            sync.CODEX_MARKETPLACE_PATH,
            sync.PLUGINS_ROOT,
        ) = saved


@contextmanager
def scan_paths(root: Path):
    """Point scripts/scan_secrets.py at a fixture tree and reset findings."""
    import scan_secrets

    saved = scan_secrets.ROOT
    scan_secrets.ROOT = root
    scan_secrets.findings.clear()
    try:
        yield scan_secrets
    finally:
        scan_secrets.ROOT = saved
        scan_secrets.findings.clear()
