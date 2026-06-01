---
name: session-telemetry
description: Append a structured snapshot of the current Claude session (context, tokens, tools, MCP, skills, errors) as a single NDJSON line to the Organon vault telemetry log. Use when the user runs /session-stats, /telemetry, or asks to "log this session", "capture session stats", "record telemetry", "snapshot this session". Do NOT trigger on generic "stats", "metrics", or "analytics" requests unrelated to Claude sessions.
---

# session-telemetry

Log target: `99 - Méta/AI/Telemetry/sessions.ndjson`
Both surfaces (Cowork + Code) use `mcp__mcp-tools-istefox__append_to_vault_file`. No filesystem path needed.

## Surface Field

Detect from system context:
- `"cowork"` — Skill tool advertised in system prompt
- `"code"` — default (Claude Code CLI / IDE)
- `"chat"` — claude.ai web context

## Introspection Checklist

Work through these steps mentally before composing JSON. Build the record silently — no intermediate output.

1. **tools.used** — scan entire transcript: every distinct tool function name in a tool_use block.
2. **tools.loaded** — scan system prompt tool-definitions block: every immediately-callable tool (schema present, not deferred).
3. **tools.deferred_total** — count tools listed in `<system-reminder>` deferred-tool notices.
4. **tools.deferred_loaded** — scan ToolSearch results in transcript: tool names whose schemas were fetched.
5. **tools.unused** — `(loaded ∪ deferred_loaded) \ used`.
6. **mcp.servers** — extract server names from `mcp__<server>__<tool>` namespaces seen in transcript.
7. **skills.available_count** — count entries in `<available_skills>` block; `0` if absent.
8. **skills.invoked** — skill names from Skill tool invocations in transcript.
9. **plugins** — derive from skill identifiers: `<plugin>:<skill>` → `<plugin>`. Deduplicate.
10. **errors** — scan tool results for `is_error: true` or `"Error:"` strings; record `{tool, msg, when}` where `when` ∈ `{early, mid, late}` (thirds of transcript).
11. **ctx** — load `references/estimation-heuristics.md` → assign `pct_est` and `confidence`.
12. **tokens** — estimate `in_est` / `out_est` from message count × heuristic; always `confidence: "low"`.
13. **session_id** — use runtime UUID if exposed; else generate a ULID and add `"session_id_source": "synthetic"`.
14. **task** — one phrase ≤ 60 chars summarizing the session's main job.
15. **tags** — lowercase; from `--tag` args plus any obvious topic tags.
16. **plugin_versions** — for each name in `plugins[]`, run `find ~/.claude/plugins/cache -maxdepth 3 -name "plugin.json" -path "*/${name}/*" 2>/dev/null`. List the version subdirectories found; pick the highest semver (e.g. `1.1.0` beats `1.0.1`); if no semver format, pick alphabetical-last. Read `version` from that `plugin.json`; if the field is absent, use the directory name itself (e.g. `655b7d9c5431` or `unknown`). If no cache entry found, use `"unknown"`. Build map `{name: version}`.

## JSON Composition

Compose per `SCHEMA.md`. Serialize **compact** (no pretty-print). Append exactly one `\n`. Never embed literal newlines in string values — escape as `\n`.

## Append Procedure

Load `references/append-mcp.md` for the exact MCP call sequence.

## Error Handling

- istefox MCP not available → fail: "Connect Organon vault first (mcp-tools-istefox)." No fallback.
- MCP call returns error → surface error verbatim; no silent retry.

## Confirmation

```
Logged to [[99 - Méta/AI/Telemetry/sessions.ndjson]] — <first-8-chars-of-session_id>.
```
