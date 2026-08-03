#!/usr/bin/env python3
"""Execute Tashtit acceptance scenarios and record observed results.

Nothing in this repository runs an agent, and the quality standard forbids
recording a result that was not actually observed. This runner therefore does
two honest things and never invents an outcome:

- `list` / `pending`: enumerate a plugin's scenarios and report which
  scenario-and-platform pairs still lack a recorded pass at the *published*
  version, so a reviewer or an external automation harness knows exactly what to
  run.
- `record`: append one observed result to `tests/plugins/<name>/acceptance.json`
  in the exact shape `scripts/validate.py` enforces. The caller MUST supply the
  observed `--outcome`, the `--reviewer`, and (for a genuine automated harness)
  `--reviewer-kind automation`. The commit and plugin version are read from the
  repository so they cannot drift from reality.

The runner is dependency-free and makes no network calls. After recording, run
`make validate` to confirm the maturity gate and schema still hold.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
SHARED_MARKETPLACE_PATH = ROOT / ".claude-plugin" / "marketplace.json"
PLUGINS_ROOT = ROOT / "plugins"
TESTS_ROOT = ROOT / "tests" / "plugins"
PLATFORMS = {"claude-code", "codex", "cursor", "github-copilot"}
OUTCOMES = {"pass", "fail"}
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


class EvalError(RuntimeError):
    """Raised when a scenario or record cannot be trusted."""


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise EvalError(f"missing file: {path}") from error
    except json.JSONDecodeError as error:
        raise EvalError(
            f"{path}: invalid JSON at line {error.lineno}, column {error.colno}"
        ) from error


def plugin_names() -> list[str]:
    if not PLUGINS_ROOT.is_dir():
        raise EvalError("missing plugins directory")
    return sorted(
        path.name
        for path in PLUGINS_ROOT.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    )


def require_plugin(name: str) -> None:
    if name not in plugin_names():
        raise EvalError(f"unknown plugin: {name!r}")


def published_version(name: str) -> str:
    marketplace = read_json(SHARED_MARKETPLACE_PATH)
    for entry in marketplace.get("plugins", []):
        if isinstance(entry, dict) and entry.get("name") == name:
            version = entry.get("version")
            if not isinstance(version, str):
                raise EvalError(f"{name} has no string version in the marketplace")
            return version
    raise EvalError(f"{name} is not listed in the shared marketplace")


def load_scenarios(name: str) -> dict[str, set[str]]:
    """Map each scenario id to the platforms it claims."""
    scenarios_dir = TESTS_ROOT / name / "scenarios"
    if not scenarios_dir.is_dir():
        raise EvalError(f"{name} has no scenarios directory")
    scenarios: dict[str, set[str]] = {}
    for path in sorted(scenarios_dir.glob("*.json")):
        data = read_json(path)
        scenario_id = data.get("id")
        platforms = data.get("platforms")
        if not isinstance(scenario_id, str) or not isinstance(platforms, list):
            raise EvalError(f"{path}: malformed scenario")
        scenarios[scenario_id] = {p for p in platforms if p in PLATFORMS}
    if not scenarios:
        raise EvalError(f"{name} has no scenarios")
    return scenarios


def load_acceptance(name: str) -> tuple[Path, dict[str, Any]]:
    path = TESTS_ROOT / name / "acceptance.json"
    record = read_json(path)
    if not isinstance(record, dict) or record.get("plugin") != name:
        raise EvalError(f"{path}: acceptance record is malformed")
    if not isinstance(record.get("results"), list):
        raise EvalError(f"{path}: results must be an array")
    return path, record


def recorded_passes(record: dict[str, Any], version: str) -> set[tuple[str, str]]:
    passes: set[tuple[str, str]] = set()
    for entry in record["results"]:
        if (
            isinstance(entry, dict)
            and entry.get("outcome") == "pass"
            and entry.get("plugin_version") == version
        ):
            passes.add((entry.get("scenario"), entry.get("platform")))
    return passes


def head_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise EvalError("could not read the current commit with git") from error
    commit = out.stdout.strip()
    if not FULL_SHA.fullmatch(commit):
        raise EvalError(f"unexpected commit format: {commit!r}")
    return commit


def pending_pairs(name: str) -> list[tuple[str, str]]:
    version = published_version(name)
    scenarios = load_scenarios(name)
    _, record = load_acceptance(name)
    passed = recorded_passes(record, version)
    pending = [
        (scenario, platform)
        for scenario in sorted(scenarios)
        for platform in sorted(scenarios[scenario])
        if (scenario, platform) not in passed
    ]
    return pending


def cmd_list(args: argparse.Namespace) -> int:
    names = [args.plugin] if args.plugin else plugin_names()
    for name in names:
        require_plugin(name)
        version = published_version(name)
        scenarios = load_scenarios(name)
        print(f"{name} @ {version}")
        for scenario in sorted(scenarios):
            platforms = ", ".join(sorted(scenarios[scenario]))
            print(f"  {scenario}: {platforms}")
    return 0


def cmd_pending(args: argparse.Namespace) -> int:
    names = [args.plugin] if args.plugin else plugin_names()
    total = 0
    for name in names:
        require_plugin(name)
        pending = pending_pairs(name)
        total += len(pending)
        version = published_version(name)
        if pending:
            print(f"{name} @ {version}: {len(pending)} unreviewed pair(s)")
            for scenario, platform in pending:
                print(f"  {scenario} on {platform}")
        else:
            print(f"{name} @ {version}: fully reviewed")
    print(f"\n{total} unreviewed scenario/platform pair(s) total.")
    return 0


def cmd_record(args: argparse.Namespace) -> int:
    name = args.plugin
    require_plugin(name)
    if args.reviewer_kind == "automation" and args.outcome not in OUTCOMES:
        raise EvalError("an automation harness must report an observed outcome")
    if args.outcome not in OUTCOMES:
        raise EvalError(f"--outcome must be one of {sorted(OUTCOMES)}")
    if args.platform not in PLATFORMS:
        raise EvalError(f"--platform must be one of {sorted(PLATFORMS)}")

    scenarios = load_scenarios(name)
    if args.scenario not in scenarios:
        raise EvalError(f"unknown scenario {args.scenario!r} for {name}")
    if args.platform not in scenarios[args.scenario]:
        raise EvalError(
            f"scenario {args.scenario!r} does not claim platform {args.platform!r}"
        )

    version = published_version(name)
    commit = head_commit()
    path, record = load_acceptance(name)

    for entry in record["results"]:
        if (
            isinstance(entry, dict)
            and entry.get("scenario") == args.scenario
            and entry.get("platform") == args.platform
            and entry.get("plugin_version") == version
        ):
            raise EvalError(
                f"{args.scenario} on {args.platform} at {version} is already "
                "recorded; edit the file by hand to correct a mistake"
            )

    result: dict[str, Any] = {
        "scenario": args.scenario,
        "platform": args.platform,
        "plugin_version": version,
        "commit": commit,
        "reviewed_on": date.today().isoformat(),
        "reviewer": args.reviewer,
        "outcome": args.outcome,
    }
    if args.notes:
        result["notes"] = args.notes

    record["results"].append(result)
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(
        f"Recorded {args.outcome} for {args.scenario} on {args.platform} "
        f"at {name} {version} ({commit[:12]}).\n"
        "Run `make validate` to confirm the schema and maturity gate."
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="list scenarios and claimed platforms")
    p_list.add_argument("--plugin", help="limit to one plugin")
    p_list.set_defaults(func=cmd_list)

    p_pending = sub.add_parser(
        "pending", help="show scenario/platform pairs lacking a pass at HEAD version"
    )
    p_pending.add_argument("--plugin", help="limit to one plugin")
    p_pending.set_defaults(func=cmd_pending)

    p_record = sub.add_parser(
        "record", help="append one observed result to an acceptance record"
    )
    p_record.add_argument("--plugin", required=True)
    p_record.add_argument("--scenario", required=True)
    p_record.add_argument("--platform", required=True)
    p_record.add_argument(
        "--outcome", required=True, help="the observed outcome: pass or fail"
    )
    p_record.add_argument(
        "--reviewer", required=True, help="human name or automation identity"
    )
    p_record.add_argument(
        "--reviewer-kind",
        choices=("human", "automation"),
        default="human",
        help="how the result was produced",
    )
    p_record.add_argument("--notes", help="optional free-form notes")
    p_record.set_defaults(func=cmd_record)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except EvalError as error:
        print(f"eval error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
