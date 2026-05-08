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
| [`organon`](https://github.com/folotp/organon-plugin) | 0.4.1 | [`folotp/organon-plugin`](https://github.com/folotp/organon-plugin) | Organon vault conventions for Claude — 7 description-triggered skills covering write discipline, frontmatter, markdown style, session discipline, Bases, JSON Canvas, and diagramming. |

## Plugin sources

Two patterns are supported:

- **In-repo** (e.g. `projectionlab`): the plugin tree lives under `plugins/<name>/` of this marketplace. The marketplace entry uses `"source": "./plugins/<name>"` and a pinned `version`. Bump version on each release.
- **External GitHub repo** (e.g. `organon` → `folotp/organon-plugin`): the plugin lives in its own repo with `.claude-plugin/plugin.json` at root. The marketplace entry uses the canonical object form `{"source": "github", "repo": "owner/repo", "ref": "vX.Y.Z", "commit": "<sha>", "sha": "<sha>"}` plus a top-level `"version": "X.Y.Z"`. The source repo must be **public** (Anthropic's Desktop plugin-source fetcher uses anonymous access — private repos are rejected with "Repository not found"). Floating (`{source, repo}` only, no `version`) loads but disables the Desktop UI's version label and Update button — pin to a release tag for proper update notifications. Bump on each release with `/bump-external-plugin <name>` (auto-resolves the latest tag + sha).

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

1. Create `plugins/<name>/` with at minimum a `skills/<name>/SKILL.md`.
2. Add an entry to `.claude-plugin/marketplace.json` under `plugins[]` with `name`, `source: "./plugins/<name>"`, `description`, `version`.
3. Optionally add `plugins/<name>/.claude-plugin/plugin.json` with version + description for discoverability.
4. Bump the plugin's version on each meaningful change.
5. Commit and push. Re-installation in Claude Code: `/plugin marketplace update folotp-marketplace` then `/plugin install <name>@folotp-marketplace`.

### Option B — External GitHub source (own repo, independent lifecycle)

1. The plugin lives in its own **public** repo (e.g. `folotp/<name>-plugin`) with `.claude-plugin/plugin.json` at root and the standard layout below it. Private source repos are rejected by the Desktop plugin-source fetcher.
2. Tag a release in the source repo (e.g. `v0.1.0`) before adding the marketplace entry.
3. Add an entry to `.claude-plugin/marketplace.json` under `plugins[]` with `name`, `description`, `version: "X.Y.Z"`, and `source` as the canonical object form: `{"source": "github", "repo": "owner/repo", "ref": "vX.Y.Z", "commit": "<sha>", "sha": "<sha>"}`. Both `commit` and `sha` are needed (loader requirement, despite the public schema only listing `sha`).
4. Commit and push the marketplace update. The plugin repo evolves independently between releases — only push to the marketplace when a new release is cut.
5. **Bump on each release**: run `/bump-external-plugin <name>` to auto-resolve the latest tag + sha from the source repo and rewrite all four fields together.
6. Re-installation: same `/plugin marketplace update folotp-marketplace` then `/plugin install <name>@folotp-marketplace`.

## License

Private. Not for redistribution.
