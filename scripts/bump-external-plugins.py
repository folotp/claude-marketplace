#!/usr/bin/env python3
"""Resolve the latest release for every external GitHub-source entry in
.claude-plugin/marketplace.json, then rewrite the entry's ref+sha and the
matching README plugins-table row's version cell.

Idempotent: entries already pinned to the latest tag+sha are left alone and
the file is not rewritten (no formatting drift).

Stdlib only. Shells out to `gh` for the GitHub API calls.
"""

from __future__ import annotations

import base64
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
README = REPO_ROOT / "README.md"


def gh(*args: str) -> str:
    result = subprocess.run(
        ["gh", *args], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def latest_release(repo: str) -> str | None:
    try:
        out = gh("release", "view", "--repo", repo, "--json", "tagName")
    except RuntimeError as e:
        msg = str(e).lower()
        if "release not found" in msg or "no releases" in msg:
            return None
        raise
    return json.loads(out)["tagName"]


def commit_sha(repo: str, ref: str) -> str:
    return gh("api", f"/repos/{repo}/commits/{ref}", "--jq", ".sha")


def plugin_version_at(repo: str, ref: str) -> str:
    raw = gh(
        "api",
        f"/repos/{repo}/contents/.claude-plugin/plugin.json?ref={ref}",
        "--jq",
        ".content",
    )
    decoded = base64.b64decode(raw).decode("utf-8")
    return json.loads(decoded)["version"]


def replace_in_source_block(text: str, plugin_name: str, old_ref: str,
                            new_ref: str, old_sha: str, new_sha: str) -> str:
    """Replace ref and sha inside the source object of the named plugin only."""
    pattern = re.compile(
        r'("name":\s*"' + re.escape(plugin_name) + r'"[\s\S]*?"source":\s*\{)([\s\S]*?)(\n\s*\})'
    )

    def repl(m: re.Match) -> str:
        head, body, tail = m.group(1), m.group(2), m.group(3)
        new_body = body.replace(f'"{old_ref}"', f'"{new_ref}"', 1)
        new_body = new_body.replace(old_sha, new_sha, 1)
        return head + new_body + tail

    new_text, n = pattern.subn(repl, text, count=1)
    if n != 1:
        raise RuntimeError(f"Could not locate source block for '{plugin_name}'")
    return new_text


def update_readme_row(plugin_name: str, new_version: str) -> None:
    text = README.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^(\|\s*\[`" + re.escape(plugin_name) + r"`\][^|]*\|\s*)([^|]+?)(\s*\|)",
        flags=re.MULTILINE,
    )
    new_text, n = pattern.subn(rf"\g<1>{new_version}\g<3>", text)
    if n == 0:
        raise RuntimeError(
            f"Could not find README plugins-table row for '{plugin_name}'"
        )
    if new_text != text:
        README.write_text(new_text, encoding="utf-8")


def main() -> int:
    text = MARKETPLACE.read_text(encoding="utf-8")
    data = json.loads(text)
    bumped, unchanged, skipped, errored = [], [], [], []

    for entry in data.get("plugins", []):
        name = entry.get("name", "<unnamed>")
        src = entry.get("source")
        if not isinstance(src, dict) or src.get("source") != "github":
            continue

        repo = src.get("repo")
        if not repo:
            errored.append((name, "missing source.repo"))
            continue

        try:
            tag = latest_release(repo)
            if tag is None:
                skipped.append((name, "no releases yet"))
                continue
            sha = commit_sha(repo, tag)
            version = plugin_version_at(repo, tag)
        except Exception as e:
            errored.append((name, str(e)))
            continue

        old_ref = src.get("ref")
        old_sha = src.get("sha")

        if old_ref == tag and old_sha == sha:
            unchanged.append((name, tag))
            continue

        text = replace_in_source_block(text, name, old_ref or "", tag,
                                       old_sha or "", sha)
        update_readme_row(name, version)
        bumped.append((name, tag, version))

    # Only rewrite marketplace.json if a bump actually changed it.
    if bumped:
        MARKETPLACE.write_text(text, encoding="utf-8")

    def fmt(rows, label):
        if not rows:
            return f"  {label}: (none)"
        return f"  {label}:\n" + "\n".join(
            f"    - {' | '.join(map(str, row))}" for row in rows
        )

    print("bump-external-plugins summary:")
    print(fmt(bumped, "bumped"))
    print(fmt(unchanged, "unchanged"))
    print(fmt(skipped, "skipped"))
    print(fmt(errored, "errored"))

    return 1 if errored else 0


if __name__ == "__main__":
    sys.exit(main())
