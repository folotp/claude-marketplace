---
description: Triage a failure issue opened by the auto-bump-external-plugins workflow — pull run logs, classify the failure, propose a fix
argument-hint: <issue-number>
---

Triage GitHub issue `#$1` opened by the `auto-bump-external-plugins` workflow when a bumped diff failed validation. Pull the issue body and the linked workflow run logs, classify the failure, and propose (or apply, with confirmation) a fix.

## When to use

Run after the auto-bump workflow opens a failure issue. The issue title looks like `Auto-bump validation failed on YYYY-MM-DDTHH:MMZ` and the body contains the diff that was rejected. The actual reason for rejection lives in the workflow run logs, not the issue body.

## Steps

1. **Fetch the issue** to confirm it exists and was opened by the bumper workflow:
   ```bash
   gh issue view $1 --json number,title,body,createdAt,author,state
   ```
   - If state is already `closed`, ask the user whether to re-triage anyway.
   - If the title doesn't match the auto-bump pattern, abort and report — this command targets bumper-opened issues only.

2. **Find the workflow run.** The bumper opens the issue from the same job that detected the failure. Match the run by recency to the issue's `createdAt`:
   ```bash
   gh run list --workflow=auto-bump-external-plugins.yml --limit=10 \
     --json databaseId,createdAt,conclusion,event
   ```
   Pick the most recent `failure`-or-`success` run created within ~2 min before the issue's `createdAt`. (The job is `success` overall when the issue-open step succeeded; the validation outcome is captured in the step log.)

3. **Pull the validator output** from the run:
   ```bash
   gh run view <run-id> --log | grep -E "validate-marketplace|FAIL|^  -" -A 1
   ```
   You're looking for the lines emitted by `scripts/validate-marketplace.py` — they're the ground truth for what tripped.

4. **Classify the failure.** Match validator output to one of these categories:

   | Validator output pattern | Cause | Suggested fix |
   |---|---|---|
   | `forbidden 'source.commit' field` | bumper or manual edit added a non-schema field | strip the `commit` field from the marketplace entry |
   | `forbidden top-level 'version' field` | duplicate version on the marketplace entry | remove the top-level `version` (lives in `plugin.json` only) |
   | `source.sha is not a 40-char hex string` | sha resolution returned a tag/branch name | re-run `gh api /repos/<repo>/commits/<ref> --jq .sha` and patch |
   | `missing source.repo` | manifest corruption | restore from `git show HEAD~1:.claude-plugin/marketplace.json` |
   | `failed to resolve plugin.json at <ref>` | source repo deleted the tag, or `plugin.json` missing on that ref | check the source repo's release page; either restore the tag or pin to a different one |
   | `README version cell '...' != plugin.json '...'` | README row is stale; bumper missed the rewrite | apply the README row update by hand and re-run the workflow |
   | `no README plugins-table row found` | new external entry added without a README row | add the row to the plugins table |

   If the output doesn't match any of the above, surface it verbatim and ask the user how to proceed.

5. **Propose the fix as a diff.** Apply the fix locally, run `python3 scripts/validate-marketplace.py` (online — full check) to confirm the diff fixes the failure, and show `git diff`. **Do not commit yet.**

6. **Ask the user to confirm.** Two paths after confirmation:
   - **Apply**: stage, commit with `fix(marketplace): triage bumper failure (#$1)`, push to `main`. Cron will re-converge on the next tick.
   - **Open draft PR**: create a branch `triage/issue-$1`, commit, push, open `gh pr create --draft` referencing `#$1` in the body.

7. **Close the issue** (only if the fix was applied to `main`): `gh issue close $1 --reason completed --comment "Fixed by <commit-sha>."`. If the fix is in a draft PR, leave the issue open and link the PR via comment.

## What not to do

- Do not push directly to `main` without showing the diff and asking for confirmation.
- Do not delete the issue — close it (with reason) so the audit trail survives.
- Do not edit the bumper or validator scripts as a "fix" — those are the contract. If they produce wrong output, that's a separate bug fix, not a triage action.
