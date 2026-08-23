# Session Telemetry Schema

Version `v: 2`. One JSON object per line, terminated by `\n`.

## Field Reference

| Field | Type | Rules |
|---|---|---|
| `v` | int | Schema version. Bump on any schema change. Current: `2`. |
| `ts` | string | ISO 8601 with timezone offset (e.g. `2026-05-26T14:30:00-04:00`). |
| `session_id` | string | Runtime UUID if available; else ULID. If synthetic, add `"session_id_source": "synthetic"`. |
| `surface` | string | `"cowork"` \| `"code"` \| `"chat"`. |
| `model` | string | Exact model string (e.g. `"claude-opus-4-7"`). |
| `ctx.limit` | int | Context window size in tokens (e.g. `200000`). |
| `ctx.used_est` | int | Estimated tokens used so far. |
| `ctx.pct_est` | int | `used_est / limit × 100`, integer. |
| `ctx.confidence` | string | `"high"` \| `"med"` \| `"low"`. See `references/estimation-heuristics.md`. |
| `tokens.in_est` | int | Estimated input tokens for session. |
| `tokens.out_est` | int | Estimated output tokens for session. |
| `tokens.confidence` | string | Always `"low"` — token counts are not exposed by runtime. |
| `tools.loaded` | string[] | Immediately-callable tools (schema present in system prompt). |
| `tools.used` | string[] | Tools actually invoked at least once. |
| `tools.unused` | string[] | `(loaded ∪ deferred_loaded) \ used`. |
| `tools.deferred_loaded` | string[] | Deferred tools fetched via ToolSearch during session. |
| `tools.deferred_total` | int | Count of deferred tools advertised but never fetched. |
| `mcp.servers` | string[] | MCP server names derived from `mcp__<server>__<tool>` namespaces. |
| `mcp.versions` | object | `{server: version_string}`. Use `"unknown"` when not determinable. |
| `skills.available_count` | int | Count of entries in `<available_skills>` block; `0` if absent. |
| `skills.invoked` | string[] | Skill names actually invoked via the Skill tool. |
| `plugins` | string[] | Plugin names derived from `<plugin>:<skill>` skill identifiers. Deduplicated. |
| `plugin_versions` | object | `{plugin_name: version_string}`. Keys match `plugins[]`. `"unknown"` when not determinable from cache path. Added in v:2. |
| `errors` | object[] | `{tool: string, msg: string, when: "early"\|"mid"\|"late"}`. Empty array if no errors. |
| `task` | string | One phrase ≤ 60 chars — the session's main job. |
| `tags` | string[] | Lowercase. From `--tag` args + topic tags. |

## Canonical Example

```json
{"v":2,"ts":"2026-05-26T14:30:00-04:00","session_id":"c6f4c18a-495c-46cc-b800-f91b6eded3bb","surface":"cowork","model":"claude-opus-4-7","ctx":{"limit":200000,"used_est":45000,"pct_est":22,"confidence":"med"},"tokens":{"in_est":38000,"out_est":7000,"confidence":"low"},"tools":{"loaded":["Read","Edit","Bash","Grep","Glob"],"used":["Read","Bash"],"unused":["Edit","Grep","Glob"],"deferred_loaded":["TaskCreate","WebSearch"],"deferred_total":120},"mcp":{"servers":["cowork","workspace","organon","github"],"versions":{"organon":"unknown","github":"unknown"}},"skills":{"available_count":47,"invoked":["caveman","engineering:system-design"]},"plugins":["organon","engineering","mattpocock-skills","anthropic-skills"],"plugin_versions":{"organon":"1.1.0","engineering":"unknown","mattpocock-skills":"unknown","anthropic-skills":"unknown"},"errors":[{"tool":"Read","msg":"ENOENT","when":"mid"}],"task":"design telemetry sys","tags":["design","telemetry","meta"]}
```

## Smoke Test

```bash
jq -c . "99 - Méta/AI/Telemetry/sessions.ndjson" | wc -l
```

Each line must parse cleanly. Output = number of records.

## Invariants

- No newlines inside string values — escape as `\n`.
- Field order stable (human grep relies on it).
- `task` ≤ 60 chars.
- `tags` entries lowercase, no spaces.
