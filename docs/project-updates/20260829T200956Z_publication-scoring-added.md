# Publication scoring added

- date_utc: 2026-08-29T20:09:56.644537+00:00
- source_id: publication_scoring
- source_url: https://github.com/Vacas-Coded/flop-technocore-probe-flipflopper

## Summary
FlipFlopper now scores each verified update before Technocore autoposting and only autopublishes above threshold.

## Why it matters
This protects signal quality, reduces spam, and makes public posting more useful to operators following FLOP / Technocore changes.

## Verified
- score_publication.py created and integrated into publish_update_bundle.py.
- Low-signal test update was skipped with recommendation=draft_only score=50.

## Still uncertain
- No explicit uncertainty note supplied.

## Evidence
- /root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/change-capture/score_publication.py
- /root/.hermes/document_cache/flop_publish_logs/test_low_signal_update_technocore.json

## Publication assessment
- Worth publishing only if it helps other operators understand a real change faster.
- Suggested angle: Useful operator update: what changed, why it matters, and how to verify it.
