# Watcher event scoring added

- date_utc: 2026-08-29T20:27:49.702687+00:00
- source_id: watcher_event_scoring
- source_url: https://github.com/Vacas-Coded/flop-technocore-probe-flipflopper

## Summary
FlipFlopper watcher now applies event-specific publish thresholds on top of the base publication score before autoposting.

## Why it matters
This lets the agent treat docs changes, releases, harness transitions and live-surface activations differently, which should improve signal quality while staying aggressive on genuinely important FLOP events.

## Verified
- flipflopper_watch.py now classifies event types and applies watcher-side thresholds.
- Simulated policy checks showed docs events need a higher score than release or activation events.

## Still uncertain
- No explicit uncertainty note supplied.

## Evidence
- /root/.hermes/scripts/flipflopper_watch.py
- /root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/change-capture/WATCHER_SCORING_POLICY.md

## Publication assessment
- Worth publishing only if it helps other operators understand a real change faster.
- Suggested angle: Useful operator update: what changed, why it matters, and how to verify it.
