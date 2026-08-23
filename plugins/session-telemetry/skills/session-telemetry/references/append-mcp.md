# Append via MCP (Both Surfaces)

Both Cowork and Claude Code use `mcp__plugin_organon_organon__append_to_vault_file`.

```
LOG_FILE = "99 - Méta/AI/Telemetry/sessions.ndjson"

# Directory auto-created by append_to_vault_file on first write — explicit create is optional
# but safe to call idempotently if you want to guarantee the directory exists first:
mcp__plugin_organon_organon__create_vault_directory("99 - Méta/AI/Telemetry")

mcp__plugin_organon_organon__append_to_vault_file(
  path    = LOG_FILE,
  content = COMPACT_JSON + "\n"
)
```

**Rules:**
- No prior read. Never call `get_vault_file` before appending.
- Single call. Do not split the record across multiple appends.
- `content` must be the compact JSON string followed by exactly one `\n`.
- If the MCP call returns an error, surface it verbatim to the user. Do not retry silently.

**Verified:** `.ndjson` extension accepted by the Organon MCP server, bytes preserved verbatim (no markdown coercion). Tested 2026-05-26.
