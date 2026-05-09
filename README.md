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
| [`organon`](https://github.com/folotp/organon-plugin) | 0.6.0 | [`folotp/organon-plugin`](https://github.com/folotp/organon-plugin) | Organon vault conventions for Claude — 7 description-triggered skills covering write discipline, frontmatter, markdown style, session discipline, Bases, JSON Canvas, and diagramming. |

## Plugin sources

Two patterns are supported:

- **In-repo** (e.g. `projectionlab`): the plugin tree lives under `plugins/<name>/` of this marketplace. The marketplace entry uses `"source": "./plugins/<name>"`. The version lives in `plugins/<name>/.claude-plugin/plugin.json` — bump it on each meaningful change so users get an Update notification (`/bump-plugin <name> <version>`).
- **External GitHub repo** (e.g. `organon` → `folotp/organon-plugin`): the plugin lives in its own **public** repo with `.claude-plugin/plugin.json` at root. Private source repos are rejected by the Desktop plugin-source fetcher (uses anonymous access). The marketplace entry uses the documented github source object: `{"source": "github", "repo": "owner/repo", "ref": "vX.Y.Z", "sha": "<40-char SHA>"}`. The version is read from `plugin.json` on the pinned ref — bump on each release with `/bump-external-plugin <name>` (auto-resolves the latest tag + sha).

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
5. **Bump on each release**: run `/bump-external-plugin <name>` — auto-resolves the latest tag + sha from the source repo and rewrites `source.ref` + `source.sha` together.
6. Re-installation: same `/plugin marketplace update folotp-marketplace` then `/plugin install <name>@folotp-marketplace`.

## License

Private. Not for redistribution.
