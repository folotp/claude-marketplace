#!/usr/bin/env bash
# PostToolUse hook (Edit | Write | MultiEdit).
#   - Validates JSON syntax for any .json file the tool just touched.
#   - Additionally runs scripts/validate-marketplace.py --offline when the
#     edit is to .claude-plugin/marketplace.json or the project README.
#     Catches schema drift (forbidden fields, sha shape, missing README row)
#     in the same loop where the mistake was made, before commit.
set -euo pipefail

input=$(cat)
file_path=$(printf '%s' "$input" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))")

[ -n "$file_path" ] || exit 0
[ -f "$file_path" ] || exit 0

case "$file_path" in
  *.json)
    if ! python3 -m json.tool "$file_path" > /dev/null 2>/tmp/.claude-json-err; then
      echo "JSON syntax error in $file_path:" >&2
      cat /tmp/.claude-json-err >&2
      rm -f /tmp/.claude-json-err
      exit 2
    fi
    rm -f /tmp/.claude-json-err
    ;;
esac

case "$file_path" in
  */.claude-plugin/marketplace.json|*/README.md)
    project_dir="${CLAUDE_PROJECT_DIR:-$(git -C "$(dirname "$file_path")" rev-parse --show-toplevel 2>/dev/null || true)}"
    validator="$project_dir/scripts/validate-marketplace.py"
    [ -x "$validator" ] || exit 0
    if ! "$validator" --offline > /tmp/.claude-mkt-err 2>&1; then
      cat /tmp/.claude-mkt-err >&2
      rm -f /tmp/.claude-mkt-err
      exit 2
    fi
    rm -f /tmp/.claude-mkt-err
    ;;
esac

exit 0
