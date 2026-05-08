---
description: Bump a plugin version across plugin.json, marketplace.json, and the README table
argument-hint: <plugin-name> <new-version>
---

Bump the `$1` plugin to version `$2` in this marketplace.

## Steps

1. **Validate args.** If `$1` or `$2` is missing, list the plugins under `plugins/` and ask which one and what version. `$2` must look like semver (`MAJOR.MINOR.PATCH`, optionally `-pre`).

2. **Resolve target.** Confirm `plugins/$1/.claude-plugin/plugin.json` exists. If not, abort and show the list of valid plugin names from `plugins/`.

3. **Read current version** from `plugins/$1/.claude-plugin/plugin.json`. Compare to `$2`. If `$2` is not strictly greater, warn the user and ask whether to proceed (downgrade or no-op may be intentional but should be acknowledged).

4. **Update three places, in order:**
   - `plugins/$1/.claude-plugin/plugin.json` — set `version` to `$2`.
   - `.claude-plugin/marketplace.json` — find the entry where `name == "$1"` in `plugins[]`, set its `version` to `$2`.
   - `README.md` — find the row in the plugins table whose link target is `plugins/$1/` (or contains `$1`) and update the version cell.

5. **Validate JSON.** Run `python3 -m json.tool .claude-plugin/marketplace.json > /dev/null` and the same on `plugins/$1/.claude-plugin/plugin.json`. The PostToolUse hooks should also catch issues automatically.

6. **Show `git diff`** and stop. Do not stage, do not commit. PA reviews and commits manually.

## Notes

- Do not modify `description`, `category`, or `tags` — this command is version-only.
- If the README table row format is ambiguous (e.g., the version cell isn't a clean column), surface the diff before saving and ask PA to confirm the edit.
- After PA commits and pushes, the install side is `/plugin marketplace update folotp-marketplace`.
