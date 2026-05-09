#!/usr/bin/env python3
"""Minimal CI-safe subset of the marketplace-consistency-checker agent.

Validates the bumper's diff before the workflow commits:
  - marketplace.json parses as JSON
  - every external entry has ref (non-empty) and sha (40-char hex)
  - no external entry carries forbidden fields (`commit`, top-level `version`)
  - the README plugins-table row exists for each external entry
  - [online only] the README version cell matches the version declared by
    plugin.json at the pinned ref

Exits non-zero on any failure. Stdlib only. Shells out to `gh` for the
plugin.json read at the pinned ref (online mode).

Pass --offline to skip the GitHub API call. Used by the PostToolUse hook
to keep the local edit loop fast; CI uses the default (online) mode.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
README = REPO_ROOT / "README.md"

SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def gh(*args: str) -> str:
    result = subprocess.run(
        ["gh", *args], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def plugin_version_at(repo: str, ref: str) -> str:
    raw = gh("api", f"/repos/{repo}/contents/.claude-plugin/plugin.json?ref={ref}",
             "--jq", ".content")
    decoded = base64.b64decode(raw).decode("utf-8")
    return json.loads(decoded)["version"]


def readme_version_for(plugin_name: str) -> str | None:
    text = README.read_text(encoding="utf-8")
    match = re.search(
        r"^\|\s*\[`" + re.escape(plugin_name) + r"`\][^|]*\|\s*([^|]+?)\s*\|",
        text,
        flags=re.MULTILINE,
    )
    return match.group(1).strip() if match else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--offline", action="store_true",
        help="skip GitHub API checks (no version cross-reference)"
    )
    args = parser.parse_args()
    errors: list[str] = []

    try:
        data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"FAIL: marketplace.json does not parse: {e}")
        return 1

    for entry in data.get("plugins", []):
        name = entry.get("name", "<unnamed>")
        src = entry.get("source")
        if not isinstance(src, dict) or src.get("source") != "github":
            continue

        if "version" in entry:
            errors.append(f"{name}: forbidden top-level 'version' field")
        if "commit" in src:
            errors.append(f"{name}: forbidden 'source.commit' field")

        ref = src.get("ref")
        sha = src.get("sha")
        if not ref:
            errors.append(f"{name}: missing or empty source.ref")
        if not sha or not SHA_PATTERN.match(sha):
            errors.append(f"{name}: source.sha is not a 40-char hex string")

        if not ref or not sha:
            continue

        repo = src.get("repo")
        if not repo:
            errors.append(f"{name}: missing source.repo")
            continue

        readme_version = readme_version_for(name)
        if readme_version is None:
            errors.append(f"{name}: no README plugins-table row found")

        if args.offline:
            continue

        try:
            expected_version = plugin_version_at(repo, ref)
        except Exception as e:
            errors.append(f"{name}: failed to resolve plugin.json at {ref}: {e}")
            continue

        if readme_version is not None and readme_version != expected_version:
            errors.append(
                f"{name}: README version cell '{readme_version}' "
                f"!= plugin.json '{expected_version}' at {ref}"
            )

    if errors:
        print("validate-marketplace: FAIL" + (" (offline)" if args.offline else ""))
        for err in errors:
            print(f"  - {err}")
        return 1

    print("validate-marketplace: OK" + (" (offline)" if args.offline else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
