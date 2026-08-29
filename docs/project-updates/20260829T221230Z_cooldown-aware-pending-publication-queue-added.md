# Cooldown-aware pending publication queue added

- date_utc: 2026-08-29T22:12:30.951160+00:00
- source_id: watcher_publication_stack
- source_url: https://github.com/Vacas-Coded/flop-technocore-probe-flipflopper

## Summary
FlipFlopper now queues autopublish-worthy updates that are blocked only by cooldown, preserving them for later retry instead of leaving them as one-off skipped attempts.

## Why it matters
This improves operational usefulness and anti-spam robustness by keeping high-signal work visible without bypassing guardrails, while also exposing the next eligible retry time.

## Verified
- publish_update_bundle.py now persists cooldown-blocked autopublish items under pending_publications with eligible_at metadata.
- A saved verification artifact shows selection stays null before eligible_at and succeeds after it.
- The retry entrypoint returned no_retryable_pending_publications when no queued item was yet eligible.

## Still uncertain
- Pending retry ordering may still need tuning if multiple rooms or event classes build backlog at once.

## Evidence
- tools/change-capture/publish_update_bundle.py
- tools/change-capture/README.md
- tools/change-capture/PUBLISH_GUARDRAILS.md
- /root/.hermes/document_cache/flop_kb/pending_publication_queue_verification_20260829.json

## Publication assessment
- Worth publishing only if it helps other operators understand a real change faster.
- Suggested angle: Useful operator update: what changed, why it matters, and how to verify it.
