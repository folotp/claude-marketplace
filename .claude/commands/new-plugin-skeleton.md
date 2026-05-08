---
description: Scaffold a new plugin entry in this marketplace (manifest + SKILL.md stub + marketplace registration + README row)
argument-hint: <plugin-name>
---

Scaffold a new plugin called `$1` in this marketplace.

## Steps

1. **Validate.** If `$1` is missing or contains characters outside `[a-z0-9-]`, abort with a clear message. If `plugins/$1/` already exists, abort — point PA to `/bump-plugin` if this was meant as a version update.

2. **Gather metadata.** Use `AskUserQuestion` to collect (in one prompt where possible):
   - **description** — one-sentence description used in both manifests and README
   - **version** — default `0.1.0`
   - **category** — short string (e.g. `personal-finance`, `dev-tools`)
   - **tags** — comma-separated list
   - **primary component** — `skills`, `commands`, `agents`, or `hooks` (default `skills`)

3. **Create the plugin manifest** at `plugins/$1/.claude-plugin/plugin.json`:
   ```json
   {
     "name": "$1",
     "version": "<version>",
     "description": "<description>",
     "author": {
       "name": "Pierre-André",
       "email": "pierreandre@folot.net"
     }
   }
   ```

4. **Create the primary component stub** based on the answer in step 2:
   - `skills` -> `plugins/$1/skills/$1/SKILL.md` with `name`, `description` frontmatter and a body placeholder.
   - `commands` -> `plugins/$1/commands/$1.md` with frontmatter `description`, `argument-hint`.
   - `agents` -> `plugins/$1/agents/$1.md` with `name`, `description`, `tools` frontmatter.
   - `hooks` -> `plugins/$1/hooks/hooks.json` with an empty hooks scaffold.

5. **Register in marketplace.** Add an entry to `.claude-plugin/marketplace.json` `plugins[]`:
   ```json
   {
     "name": "$1",
     "source": "./plugins/$1",
     "description": "<description>",
     "version": "<version>",
     "category": "<category>",
     "tags": ["<tag1>", "<tag2>"]
   }
   ```

6. **Add a row to `README.md`** plugins table, matching the existing row format.

7. **Validate.** Run `python3 -m json.tool` on both `marketplace.json` and the new `plugin.json`. The PostToolUse hooks will also fire on each edit.

8. **Final report.** Show `git status` (untracked files in `plugins/$1/`), and remind PA to:
   - Fill in the SKILL.md / command / agent body before committing.
   - Bump the description if it grows past one sentence.
   - Commit when ready — this command does not commit.
