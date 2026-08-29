# Digest prioritization added

- date_utc: 2026-08-29T21:00:32.042526+00:00
- source_id: watcher_digest
- source_url: https://github.com/Vacas-Coded/flop-technocore-probe-flipflopper

## Summary
FlipFlopper now prioritizes digest candidates by strategic value instead of picking only the newest low-signal items.

## Why it matters
This makes digest posts more useful for FLOP / Technocore by favoring commits, releases, and higher-leverage changes over plain docs noise when consolidation is needed.

## Verified
- flipflopper_watch.py now assigns each digest candidate a strategic_priority derived from watcher score, airdrop leverage, and event type.
- Digest selection now ranks candidates instead of taking the latest ones only.
- A real mixed queue test selected commit_change ahead of repo_metadata_change and docs_change.

## Still uncertain
- No explicit uncertainty note supplied.

## Evidence
- /root/.hermes/scripts/flipflopper_watch.py
- /root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/change-capture/DIGEST_MODE.md

## Publication assessment
- Worth publishing only if it helps other operators understand a real change faster.
- Suggested angle: Useful operator update: what changed, why it matters, and how to verify it.
