---
description: Bump an external GitHub-source plugin to its source repo's latest release (resolves tag + sha, rewrites source.ref and source.sha)
argument-hint: <plugin-name>
---

Bump the `$1` plugin's pinning to the latest release in its source GitHub repo.

> **Note.** The `.github/workflows/auto-bump-external-plugins.yml` workflow already bumps every external entry on a 30-min cron and on `repository_dispatch` from each source repo. This manual command remains for ad-hoc dry-run preview (it stops at `git diff` instead of committing), targeting a single plugin, or emergency overrides when CI is unavailable.

## When to use

For external github-source entries in `.claude-plugin/marketplace.json` (entries whose `source` is an object with `{source: "github", repo: ...}`). Not for in-repo plugins (those use `/bump-plugin`).

## Single source of truth

Per the [plugin marketplace docs](https://code.claude.com/docs/en/plugin-marketplaces#version-resolution-and-release-channels), version lives in the source repo's `plugin.json` — never duplicated in `marketplace.json`. This command rewrites the marketplace entry's `source.ref` and `source.sha` to point at the latest release, then updates the README plugins table for human readers. The version itself is read from the source `plugin.json`; the marketplace entry has no `version` field.

## Steps

1. **Validate args.** If `$1` is missing, list the external-source plugins from `marketplace.json` (entries where `source` is an object) and ask which.

2. **Resolve target.** Read `.claude-plugin/marketplace.json`. Find the entry where `name == "$1"`. Verify its `source` is an object with `source == "github"` and a `repo` field. If not (e.g. in-repo `./plugins/...`), abort and point to `/bump-plugin`.

3. **Fetch latest release** from the source repo:
   ```bash
   gh release view --repo <repo> --json tagName,targetCommitish
   ```
   If no releases exist, abort with a clear message — pinning requires at least one tagged release.

4. **Resolve the commit sha** for the latest tag:
   ```bash
   gh api /repos/<repo>/commits/<tagName> --jq '.sha'
   ```

5. **Resolve the version** declared on that commit's `plugin.json`:
   ```bash
   gh api /repos/<repo>/contents/.claude-plugin/plugin.json?ref=<tagName> --jq '.content' | base64 -d | python3 -c 'import json,sys; print(json.load(sys.stdin)["version"])'
   ```
   This is the value the README plugins table will display. If it differs from `tagName` minus a leading `v`, surface the discrepancy and ask the user whether to proceed.

6. **Compare to current state.** Read current `source.ref` and `source.sha` in the entry. If both already match the latest tag, report "already at latest (`<tagName>`)" and stop — no diff to make.

7. **Rewrite the entry**, updating two fields:
   - `source.ref` -> `<tagName>` (e.g. `v0.4.1`)
   - `source.sha` -> `<sha>` (40-char commit SHA)

   Keep all other fields untouched. **Do not add `commit` or a top-level `version`** — `commit` is not in the documented schema, and version lives in `plugin.json` per the doc warning.

8. **If the entry has stale `commit` or top-level `version` fields** (left over from before the doc-aligned cleanup), remove them in the same diff.

9. **Update README plugins table.** Find the row whose link target contains `$1` (or matches the plugin name in the first cell). Set the version cell to the version from step 5.

10. **Validate JSON.** Run `python3 -m json.tool .claude-plugin/marketplace.json > /dev/null`. The PostToolUse hook will also fire on the edit.

11. **Show `git diff`** and stop. Do not stage, do not commit. PA reviews and commits manually.

## Notes

- The source repo must be public — Anthropic Desktop's plugin-source fetcher uses anonymous access and rejects private repos with "Repository not found".
- After commit + push, install side: `/plugin marketplace update folotp-marketplace` then click Update on the plugin row in Desktop. Update detection compares the user's installed `plugin.json` version against the version of the manifest at the new pinned ref.
