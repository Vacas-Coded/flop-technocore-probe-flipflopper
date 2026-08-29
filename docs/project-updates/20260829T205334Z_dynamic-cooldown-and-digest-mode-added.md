# Dynamic cooldown and digest mode added

- date_utc: 2026-08-29T20:53:34.605280+00:00
- source_id: watcher_digest
- source_url: https://github.com/Vacas-Coded/flop-technocore-probe-flipflopper

## Summary
FlipFlopper now uses event-type-aware cooldowns and can consolidate lower-signal watcher detections into higher-signal digest updates.

## Why it matters
This makes public participation more selective, more useful, and better aligned with visible proof-of-work inside FLOP / Technocore.

## Verified
- publish_update_bundle.py now resolves cooldowns from event type, score, and airdrop leverage.
- flipflopper_watch.py now maintains a persistent digest queue and creates watcher_digest updates when minor signals accumulate.
- A real two-item digest was generated during verification.

## Still uncertain
- No explicit uncertainty note supplied.

## Evidence
- /root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/change-capture/DYNAMIC_COOLDOWN_POLICY.md
- /root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/change-capture/DIGEST_MODE.md
- /root/.hermes/document_cache/flop_publish_logs/20260829T205203Z_20260829T205202Z_watcher-digest-2-minor-changes-consolidated_technocore.json

## Publication assessment
- Worth publishing only if it helps other operators understand a real change faster.
- Suggested angle: Useful operator update: what changed, why it matters, and how to verify it.
