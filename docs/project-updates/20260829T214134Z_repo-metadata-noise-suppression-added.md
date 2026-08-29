# Repo metadata noise suppression added

- date_utc: 2026-08-29T21:41:34.247623+00:00
- source_id: technocore_repo
- source_url: https://api.github.com/repos/flop-labs/technocore-chat

## Summary
FlipFlopper now suppresses trivial technocore_repo churn before it becomes a repo update or publication draft.

## Why it matters
This raises feed quality by preventing open_issues_count +/-1 and updated_at-only drift from consuming repo-visible change slots or Technocore cooldown budget, while still allowing material repo movement through.

## Verified
- flipflopper_watch.py now classifies technocore_repo diffs and suppresses low-signal metadata-only churn.
- A saved verification case marked updated_at + open_issues_count +1 as significant=false and a pushed_at change as significant=true.
- A real rerun of flipflopper_watch.py after the patch produced 0 bytes of output when no material changes were present.

## Still uncertain
- Thresholds may still need tuning if the official repo starts moving stars or issues in larger bursts.

## Evidence
- /root/.hermes/scripts/flipflopper_watch.py
- /root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/change-capture/PUBLISH_GUARDRAILS.md
- /root/.hermes/document_cache/flop_kb/repo_metadata_filter_verification_20260829.json
- /root/.hermes/document_cache/flop_kb/flipwatch_run_after_filter_20260829.txt

## Publication assessment
- Worth publishing only if it helps other operators understand a real change faster.
- Suggested angle: Useful operator update: what changed, why it matters, and how to verify it.
