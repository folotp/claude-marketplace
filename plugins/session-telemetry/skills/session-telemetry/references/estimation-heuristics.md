# Estimation Heuristics

## Context (`ctx`)

Estimate `ctx.pct_est` from message count and conversation depth.

| Messages in session | `pct_est` range | `confidence` |
|---|---|---|
| < 5 | 5–15 | `"med"` |
| 5–20 | 15–40 | `"med"` |
| 20–50 | 40–70 | `"low"` |
| > 50 | 70–95 | `"low"` |

Set `ctx.limit` to the model's advertised context window (200 000 for claude-opus-4-7 and claude-sonnet-4-6; 200 000 for claude-haiku-4-5).

Derive `ctx.used_est = pct_est / 100 × limit`.

## Tokens (`tokens`)

Always set `tokens.confidence: "low"` — token counts are not exposed by the runtime.

Rough heuristics (order-of-magnitude only):
- Input: ~1 500 tokens per user+assistant message pair
- Output: ~300 tokens per assistant message

```
in_est  = message_pair_count × 1500
out_est = assistant_message_count × 300
```

These are intentionally rough. The `confidence: "low"` field signals this to downstream analysis.

## Notes

- Prefer underestimating over overestimating — a conservative `pct_est` is less misleading.
- If a session used heavy file reads or long system prompts, bias `pct_est` upward one bucket.
- If a session was mostly short exchanges, bias downward.
