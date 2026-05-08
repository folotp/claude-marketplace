#!/usr/bin/env bash
set -euo pipefail

input=$(cat)

file_path=$(printf '%s' "$input" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))")

case "$file_path" in
  *.json) ;;
  *) exit 0 ;;
esac

[ -f "$file_path" ] || exit 0

if ! python3 -m json.tool "$file_path" > /dev/null 2>/tmp/.claude-json-err; then
  echo "JSON syntax error in $file_path:" >&2
  cat /tmp/.claude-json-err >&2
  rm -f /tmp/.claude-json-err
  exit 2
fi

rm -f /tmp/.claude-json-err
exit 0
