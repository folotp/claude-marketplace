#!/usr/bin/env bash
set -euo pipefail

input=$(cat)

file_path=$(printf '%s' "$input" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))")
cwd=$(printf '%s' "$input" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('cwd',''))")

case "$file_path" in
  */plugin.json|*/marketplace.json) ;;
  *) exit 0 ;;
esac

repo_root="${CLAUDE_PROJECT_DIR:-${cwd:-$(pwd)}}"
mkt="$repo_root/.claude-plugin/marketplace.json"
[ -f "$mkt" ] || exit 0

python3 - "$repo_root" <<'PYEOF'
import json, sys, os
root = sys.argv[1]
mkt_path = os.path.join(root, '.claude-plugin', 'marketplace.json')
try:
    with open(mkt_path) as f:
        mkt = json.load(f)
except Exception as e:
    sys.stderr.write(f"Could not read marketplace.json: {e}\n")
    sys.exit(0)

issues = []
seen = set()
for entry in mkt.get('plugins', []):
    name = entry.get('name', '?')
    seen.add(name)
    src = entry.get('source', '')
    mkt_ver = entry.get('version')
    if not isinstance(src, str) or not src.startswith('./'):
        continue
    plugin_dir = os.path.join(root, src[2:])
    pj_path = os.path.join(plugin_dir, '.claude-plugin', 'plugin.json')
    if not os.path.isfile(pj_path):
        issues.append(f"{name}: plugin.json missing at {os.path.relpath(pj_path, root)}")
        continue
    try:
        with open(pj_path) as pf:
            pj = json.load(pf)
    except Exception as e:
        issues.append(f"{name}: could not parse plugin.json ({e})")
        continue
    pj_ver = pj.get('version')
    if mkt_ver and pj_ver and mkt_ver != pj_ver:
        issues.append(f"{name}: version mismatch -- marketplace.json={mkt_ver}, plugin.json={pj_ver}")

plugins_dir = os.path.join(root, 'plugins')
if os.path.isdir(plugins_dir):
    for d in sorted(os.listdir(plugins_dir)):
        full = os.path.join(plugins_dir, d)
        if os.path.isdir(full) and d not in seen:
            issues.append(f"{d}: directory exists at plugins/{d}/ but not registered in marketplace.json")

if issues:
    sys.stderr.write("Marketplace consistency heads-up (sync these before commit):\n")
    for i in issues:
        sys.stderr.write(f"  - {i}\n")
    sys.exit(2)
PYEOF
