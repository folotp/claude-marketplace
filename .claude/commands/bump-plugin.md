---
description: Bump an in-repo plugin version in plugin.json and the README plugins table
argument-hint: <plugin-name> <new-version>
---

Bump the in-repo `$1` plugin to version `$2`.

## When to use

For in-repo plugin entries (entries whose `source` is a `./plugins/...` string). Not for external github-source plugins (those use `/bump-external-plugin`).

## Single source of truth

Per the [plugin marketplace docs](https://code.claude.com/docs/en/plugin-marketplaces#version-resolution-and-release-channels), version lives in `plugin.json` only — never duplicated in `marketplace.json`. This command edits `plugin.json` (canonical) and the README plugins table (docs). It does NOT touch `marketplace.json`.

## Steps

1. **Validate args.** If `$1` or `$2` is missing, list the in-repo plugins under `plugins/` and ask. `$2` must look like semver (`MAJOR.MINOR.PATCH`, optionally `-pre`).

2. **Resolve target.** Confirm `plugins/$1/.claude-plugin/plugin.json` exists. If not, abort and show the list of valid plugin names from `plugins/`.

3. **Read current version** from `plugins/$1/.claude-plugin/plugin.json`. Compare to `$2`. If `$2` is not strictly greater, warn the user and ask whether to proceed (downgrade or no-op may be intentional but should be acknowledged).

4. **Update two places, in order:**
   - `plugins/$1/.claude-plugin/plugin.json` — set `version` to `$2`.
   - `README.md` — find the row in the plugins table whose link target is `plugins/$1/` (or contains `$1`) and update the version cell to `$2`.

5. **If `marketplace.json` has a top-level `version` on the `$1` entry**, remove it (the doc warns against duplicating; `plugin.json` always wins silently). Surface this in the diff so the user knows what's removed.

6. **Validate JSON.** Run `python3 -m json.tool plugins/$1/.claude-plugin/plugin.json > /dev/null` and the same on `.claude-plugin/marketplace.json`. The PostToolUse hooks should also catch issues automatically.

7. **Show `git diff`** and stop. Do not stage, do not commit. PA reviews and commits manually.

## Notes

- Do not modify `description`, `category`, or `tags` — this command is version-only.
- After PA commits and pushes, the user side is `/plugin marketplace update folotp-marketplace` then click Update on the plugin row in Desktop (or `/plugin install <name>@folotp-marketplace` to force-reinstall).
