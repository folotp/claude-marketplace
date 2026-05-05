# claude-marketplace

Personal Claude marketplace. Hosts plugins (skills, commands, agents, hooks, MCP bundles) for use across Claude Code, Cowork, and any future surface that supports the Claude plugin format.

## Install

```text
/plugin marketplace add folotp/claude-marketplace
/plugin install <plugin-name>@claude-marketplace
/reload-plugins
```

For a private repo, ensure `gh auth status` shows you're logged in to GitHub before running `/plugin marketplace add`.

## Plugins

| Plugin | Version | Description |
| --- | --- | --- |
| [`projectionlab`](plugins/projectionlab/) | 0.1.0 | Read-only access to ProjectionLab financial plans via the Chrome MCP. |

## Layout

```
.claude-plugin/
  marketplace.json          ← marketplace metadata + plugin registry
plugins/
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

1. Create `plugins/<name>/` with at minimum a `skills/<name>/SKILL.md`.
2. Add an entry to `.claude-plugin/marketplace.json` under `plugins[]` with `name`, `source: "./plugins/<name>"`, `description`, `version`.
3. Optionally add `plugins/<name>/.claude-plugin/plugin.json` with version + description for discoverability.
4. Bump the plugin's version on each meaningful change.
5. Commit and push. Re-installation in Claude Code: `/plugin marketplace update claude-marketplace` then `/plugin install <name>@claude-marketplace`.

## License

Private. Not for redistribution.
