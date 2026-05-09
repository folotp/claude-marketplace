# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`folotp-marketplace` (registered name in `.claude-plugin/marketplace.json`) is a personal Claude Code plugin marketplace. It is a **manifest + tooling repo, not an application** — there is no app runtime, no language toolchain. The "code" is Python stdlib scripts, bash hooks, GitHub Actions workflows, and Markdown specs (slash commands, agent system prompts).

## Two plugin source patterns

Every entry in `.claude-plugin/marketplace.json` `plugins[]` is one of:

- **In-repo** (`source: "./plugins/<name>"`): the plugin tree lives under `plugins/<name>/`. `plugin.json` is its `version` source of truth. Bumped via `/bump-plugin`.
- **External GitHub** (`source: {source: "github", repo, ref, sha}`): the plugin lives in its own public repo. `ref` and `sha` together pin it to a specific release. Bumped automatically by `.github/workflows/auto-bump-external-plugins.yml` (see "Auto-bump pipeline" below); `/bump-external-plugin` remains for manual / dry-run preview.

External-source repos must be **public** — the Desktop plugin-source fetcher uses anonymous access and rejects private ones.

## Single source of truth for version

Per the [official docs](https://code.claude.com/docs/en/plugin-marketplaces#version-resolution-and-release-channels), Claude resolves a plugin's version from `plugin.json` first, then a top-level `version` on the marketplace entry, then the source SHA. **Never set `version` in both `plugin.json` and the marketplace entry.** `plugin.json` always wins silently, so a stale duplicate masks a real bump. This rule is enforced by `scripts/validate-marketplace.py` and the consistency-checker agent — don't add a top-level `version` to entries, and never re-introduce the legacy `commit` field on github sources (not in the schema; was removed in `c7dcab7`).

## Auto-bump pipeline

The flow when an external plugin (e.g. `organon`) cuts a new release:

1. **Source repo** publishes a release. A workflow there (`notify-marketplace.yml`) fires `repository_dispatch[external-plugin-release]` at this repo via the composite action `.github/actions/notify-marketplace/action.yml`. The dispatcher logic lives **once**, in this repo's composite action — source repos contain only a 6-line caller workflow and a `MARKETPLACE_DISPATCH_TOKEN` secret.
2. **`.github/workflows/auto-bump-external-plugins.yml`** wakes on the dispatch (or every 30 min via cron as a safety net). It runs `scripts/bump-external-plugins.py`, which scans every external entry, resolves each repo's latest tag + commit SHA + `plugin.json` version, and rewrites `source.ref`, `source.sha`, and the matching README plugins-table row.
3. **`scripts/validate-marketplace.py`** gates the commit. On success the workflow commits to `main` as `marketplace-bot`; on failure it opens a GitHub issue with the rejected diff (use `/triage-bumper-failure <#>` to investigate).

The bumper is **idempotent and formatting-preserving**: it does a targeted text-level edit of `ref` and `sha` (not a JSON re-serialize), so the only diff on a real bump is the two changed lines plus the README cell. If you ever need to change this, preserve that property — `json.dumps(indent=2)` would expand every compact tags array and produce noisy diffs.

## Edit-time validation

`.claude/hooks/validate-json.sh` is a PostToolUse hook (Edit | Write | MultiEdit, configured in `.claude/settings.json`). It does two things:

1. JSON syntax check on any `.json` file the tool just touched.
2. **Schema check** via `python3 scripts/validate-marketplace.py --offline` whenever the touched path is `.claude-plugin/marketplace.json` or `README.md`. Catches forbidden-field drift, sha shape, and missing README rows in the same loop the mistake was made — before commit. Exit 2 blocks the edit; the validator's stderr surfaces the rule that tripped.

The `--offline` flag skips the GitHub-API `plugin.json` version cross-check (kept fast for the local loop). CI runs the validator without `--offline` to catch the cross-check too.

## Available automations

- **Slash commands** (`.claude/commands/*.md`):
  - `/bump-plugin <name> <version>` — bump in-repo plugin's `plugin.json` + README row.
  - `/bump-external-plugin <name>` — manual / dry-run external bump (the auto-bump workflow handles the routine path).
  - `/new-plugin-skeleton` — scaffold a new in-repo plugin (manifest + SKILL.md stub + marketplace registration + README row).
  - `/triage-bumper-failure <issue-#>` — classify a workflow-opened failure issue against validator output and propose a fix.

- **Agents** (`.claude/agents/*.md`, both **read-only**):
  - `marketplace-consistency-checker` — audits the marketplace's structural integrity (manifest ↔ disk ↔ README).
  - `new-plugin-quality-reviewer` — audits a single in-repo plugin's internal quality (description-trigger effectiveness, frontmatter, components).

Use these instead of re-inventing the same checks ad hoc. Both agents are read-only on purpose — they do not edit files.

## Conventions to follow

- **Don't commit** changes unless explicitly asked. The bumper and validators surface diffs; the user reviews and commits.
- **Don't reformat `marketplace.json`** when only changing one entry — keep tags arrays compact (single-line). Use targeted edits (`Edit` tool, or text-level regex in scripts), not JSON re-serialize.
- **Run `python3 scripts/validate-marketplace.py`** (online, full check) before committing any change to `marketplace.json` or `README.md`'s plugins table. The hook does the offline subset; the full check catches version-cell drift against the source repo's `plugin.json`.
- **Check `git log --oneline` first.** This repo's history is short and the commit messages are precise — the schema-shape, single-source-of-truth, and bumper-formatting decisions all have commits explaining the why.
