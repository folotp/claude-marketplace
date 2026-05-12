# claude-marketplace

Personal Claude marketplace. Hosts plugins (skills, commands, agents, hooks, MCP bundles) for use across Claude Code, Cowork, and any future surface that supports the Claude plugin format.

## Install

```text
/plugin marketplace add folotp/claude-marketplace
/plugin install <plugin-name>@folotp-marketplace
/reload-plugins
```

The marketplace `name` (`folotp-marketplace`) differs from the repo name (`claude-marketplace`) because Claude Code rejects marketplace names that impersonate official Anthropic marketplaces.

For a private repo, ensure `gh auth status` shows you're logged in to GitHub before running `/plugin marketplace add`.

## Plugins

| Plugin | Version | Source | Description |
| --- | --- | --- | --- |
| [`projectionlab`](plugins/projectionlab/) | 0.1.0 | in-repo | Read-only access to ProjectionLab financial plans via the Chrome MCP. |
| [`organon`](https://github.com/folotp/organon-plugin) | 1.0.0 | [`folotp/organon-plugin`](https://github.com/folotp/organon-plugin) | Organon vault conventions for Claude — 7 description-triggered skills covering write discipline, frontmatter, markdown style, session discipline, Bases, JSON Canvas, and diagramming. |

## Plugin sources

Two patterns are supported:

- **In-repo** (e.g. `projectionlab`): the plugin tree lives under `plugins/<name>/` of this marketplace. The marketplace entry uses `"source": "./plugins/<name>"`. The version lives in `plugins/<name>/.claude-plugin/plugin.json` — bump it on each meaningful change so users get an Update notification (`/bump-plugin <name> <version>`).
- **External GitHub repo** (e.g. `organon` → `folotp/organon-plugin`): the plugin lives in its own **public** repo with `.claude-plugin/plugin.json` at root. Private source repos are rejected by the Desktop plugin-source fetcher (uses anonymous access). The marketplace entry uses the documented github source object: `{"source": "github", "repo": "owner/repo", "ref": "vX.Y.Z", "sha": "<40-char SHA>"}`. The version is read from `plugin.json` on the pinned ref. Bumps are automatic — see [auto-bump](#auto-bump-of-external-plugins) below — `/bump-external-plugin <name>` remains for manual / dry-run use.

**Single source of truth for version.** Per the [official docs](https://code.claude.com/docs/en/plugin-marketplaces#version-resolution-and-release-channels), Claude Code resolves a plugin's version from the first of these set: `version` in `plugin.json` -> `version` in the marketplace entry -> the source's commit SHA. **Don't set `version` in both `plugin.json` and the marketplace entry** — `plugin.json` always wins silently, so a stale duplicate can mask a real bump. This marketplace keeps `version` in `plugin.json` only.

## Layout

```
.claude-plugin/
  marketplace.json          ← marketplace metadata + plugin registry
plugins/                    ← in-repo plugins only
  <plugin-name>/
    .claude-plugin/
      plugin.json           ← per-plugin manifest (optional but recommended)
    skills/<skill>/SKILL.md
    commands/<cmd>.md
    agents/<agent>.md
    hooks/hooks.json
README.md
```

Skills, commands, agents, and hooks are auto-discovered from their conventional folders inside each plugin — no explicit declaration in `plugin.json` required.

## Adding a new plugin

### Option A — In-repo (small plugins, tight coupling to marketplace lifecycle)

1. Create `plugins/<name>/` with at minimum a `skills/<name>/SKILL.md` (or commands/agents/hooks).
2. Create `plugins/<name>/.claude-plugin/plugin.json` with `name`, `version`, `description`, `author`. **The `version` here drives Update detection — bump it on every meaningful change.**
3. Add an entry to `.claude-plugin/marketplace.json` under `plugins[]` with `name`, `source: "./plugins/<name>"`, `description`, `category`, `tags`. Do **not** duplicate `version` here.
4. Use `/bump-plugin <name> <version>` to bump on each release (updates `plugin.json` and the README plugins table).
5. Commit and push. Re-installation: `/plugin marketplace update folotp-marketplace` then `/plugin install <name>@folotp-marketplace`.

### Option B — External GitHub source (own repo, independent lifecycle)

1. The plugin lives in its own **public** repo (e.g. `folotp/<name>-plugin`) with `.claude-plugin/plugin.json` at root and the standard layout below it. Private source repos are rejected by the Desktop plugin-source fetcher.
2. Tag a release in the source repo (e.g. `v0.1.0`) before adding the marketplace entry. The release commit's `plugin.json` must declare a `version` matching the tag.
3. Add an entry to `.claude-plugin/marketplace.json` under `plugins[]` with `name`, `description`, `category`, `tags`, and `source` as the documented github source object: `{"source": "github", "repo": "owner/repo", "ref": "vX.Y.Z", "sha": "<40-char SHA>"}`. Do **not** add `commit` (not in the schema) or a top-level `version` (let `plugin.json` own it).
4. Commit and push the marketplace update. The plugin repo evolves independently between releases — only push to the marketplace when a new release is cut.
5. **No manual bumping needed** — see [auto-bump](#auto-bump-of-external-plugins) below. The `/bump-external-plugin <name>` command stays available for ad-hoc dry-run preview.
6. Re-installation: same `/plugin marketplace update folotp-marketplace` then `/plugin install <name>@folotp-marketplace`.

## Auto-bump of external plugins

External github-source entries are re-pinned automatically by [`.github/workflows/auto-bump-external-plugins.yml`](.github/workflows/auto-bump-external-plugins.yml). The workflow runs `scripts/bump-external-plugins.py`, which scans every external entry, resolves each source repo's latest release tag + commit sha, rewrites `source.ref` and `source.sha` in `marketplace.json`, and updates the matching version cell in the plugins table above. `scripts/validate-marketplace.py` gates the commit; on failure the workflow opens an issue instead.

Triggers:
- **Cron**, every 30 min (safety net).
- **`repository_dispatch`** of type `external-plugin-release`, fired by each source repo on `release: published` (near-instant).
- **Manual**: `gh workflow run auto-bump-external-plugins.yml` for debug.

### Wiring up `repository_dispatch` in a source repo

To get instant updates instead of waiting up to 30 min for cron, do these two steps in the source repo (e.g. `folotp/<name>-plugin`):

**1. Create a PAT and store it as a repo secret.**

Generate a token at <https://github.com/settings/tokens>:
- Classic PAT: `repo` scope.
- Fine-grained PAT (preferred, tighter): scoped to `folotp/claude-marketplace`, repository permission `Contents: write` (this is what the `repository_dispatch` endpoint requires).

Then in the source repo: **Settings → Secrets and variables → Actions → New repository secret**. Name it `MARKETPLACE_DISPATCH_TOKEN`, paste the PAT.

> Use the **Actions** tab, not Codespaces / Dependabot / Agents — those tabs scope secrets to other contexts (Codespaces dev envs, Dependabot-triggered runs, the Copilot Coding Agent) and are not visible to a `release: published` workflow.

**2. Add this workflow file:**

```yaml
# .github/workflows/notify-marketplace.yml
name: Notify marketplace
on:
  release:
    types: [published]
jobs:
  dispatch:
    runs-on: ubuntu-latest
    steps:
      - uses: folotp/claude-marketplace/.github/actions/notify-marketplace@main
        with:
          token: ${{ secrets.MARKETPLACE_DISPATCH_TOKEN }}
```

The dispatcher logic lives once, in the [`notify-marketplace`](.github/actions/notify-marketplace/action.yml) composite action of this repo — change it here and every source repo picks up the new behavior on its next release. Pin to `@main` for auto-update, or to a tag/sha (e.g. `@v1`) for stability.

Without this workflow, the cron tick alone catches new releases within 30 min — this step is purely a latency optimization.

The `client_payload` is informational; the bumper rescans every external entry regardless of which repo dispatched.

## License

Private. Not for redistribution.
