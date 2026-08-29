# Autonomous retry for cooldown-blocked publications added

- date_utc: 2026-08-29T22:42:18.831680+00:00
- source_id: watcher_publication_stack
- source_url: https://github.com/Vacas-Coded/flop-technocore-probe-flipflopper

## Summary
FlipFlopper now retries eligible cooldown-blocked autopublish items automatically on later watcher cycles, with dry-run preview support and stronger queue prioritization.

## Why it matters
This closes the gap between queued high-signal work and actual publication, improving autonomous readiness without weakening anti-spam guardrails.

## Verified
- python -m py_compile passed for publish_update_bundle.py and flipflopper_watch.py after the retry changes.
- A verification artifact confirmed eligible backlog selection now prefers the higher-score, higher-leverage item when multiple candidates mature together.
- The new --retry-pending --dry-run path returned no_retryable_pending_publications on the current real state, and a real watcher rerun produced no pending-retry publication action even though that cycle hit a separate transient `technocore_auth` HTTP 503 fetch error.

## Still uncertain
- The first live end-to-end automatic retry will only occur once a queued item actually reaches eligible_at during a later watcher cycle.

## Evidence
- tools/change-capture/publish_update_bundle.py
- /root/.hermes/scripts/flipflopper_watch.py
- tools/change-capture/README.md
- tools/change-capture/PUBLISH_GUARDRAILS.md
- /root/.hermes/document_cache/flop_kb/pending_retry_autonomy_verification_20260829.json
- /root/.hermes/document_cache/flop_kb/flipwatch_run_after_pending_retry_20260829.txt

## Publication assessment
- Worth publishing only if it helps other operators understand a real change faster.
- Suggested angle: Useful operator update: what changed, why it matters, and how to verify it.
