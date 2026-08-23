<context>
Repo: folotp-marketplace. Manifest + tooling only — no app runtime, no language toolchain.
Plugin sources: in-repo (plugins/<name>/) or external GitHub (pinned ref+sha). Version SOT: plugin.json.
</context>

<workflow>
Validation: run python3 scripts/validate-marketplace.py (online, full) before any marketplace.json or README.md commit. Edit hook validate-json.sh (PostToolUse) does offline subset automatically.
Auto-bump: auto-bump-external-plugins.yml handles routine path. /bump-external-plugin for manual/dry-run. External repos must be public (anonymous fetch).
Agents (read-only): marketplace-consistency-checker · new-plugin-quality-reviewer. Use instead of ad-hoc checks.
/triage-bumper-failure <#> for workflow-opened failure issues.
</workflow>

<constraints>
Never set version in both plugin.json and marketplace entry — plugin.json wins silently.
Never re-introduce legacy commit field on github sources.
No commit without approval.
No JSON reformat on targeted edits; tags arrays = compact single-line.
</constraints>
