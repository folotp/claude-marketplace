---
description: Bump an external GitHub-source plugin to its source repo's latest release (resolves tag + sha, updates all four pinning fields)
argument-hint: <plugin-name>
---

Bump the `$1` plugin's pinning to the latest release in its source GitHub repo.

## When to use

For external github-source entries in `.claude-plugin/marketplace.json` (entries whose `source` is an object with `{source: "github", repo: ...}`). Not for in-repo plugins (those use `/bump-plugin`).

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

5. **Compute the new version string.** Strip a leading `v` from `tagName` (e.g. `v0.4.1` -> `0.4.1`). If `tagName` doesn't start with `v` or `V`, use it as-is.

6. **Compare to current state.** Read current `version` and `source.ref` in the entry. If both already match the latest tag, report "already at latest (vX.Y.Z)" and stop — no diff to make.

7. **Rewrite the entry**, updating four fields together:
   - `source.ref` -> `<tagName>` (e.g. `v0.4.1`)
   - `source.commit` -> `<sha>`
   - `source.sha` -> `<sha>`
   - top-level `version` -> the version string from step 5

   Keep all other fields (`description`, `category`, `tags`, etc.) untouched.

8. **Update README plugins table.** Find the row where the link target contains `$1` (or matches the plugin name in the first cell). Set the version cell to the new version string.

9. **Validate JSON.** Run `python3 -m json.tool .claude-plugin/marketplace.json > /dev/null`. The PostToolUse hooks will also fire on the edit.

10. **Show `git diff`** and stop. Do not stage, do not commit. PA reviews and commits manually.

## Notes

- Both `commit` and `sha` get the same value — Anthropic's loader empirically requires `commit` (the schema lists only `sha`, but the official `claude-plugins-official` marketplace ships both, and bare-`sha` shapes have failed with "Failed to update marketplace" historically).
- The source repo must be public — the Desktop plugin-source fetcher uses anonymous access and rejects private repos with "Repository not found".
- After commit + push, install side: `/plugin marketplace update folotp-marketplace` then the Desktop UI should show an Update button on the plugin row (because marketplace `version` advanced past the installed `version`).
