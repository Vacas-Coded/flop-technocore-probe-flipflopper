# Publish guardrails and airdrop leverage scoring added

- date_utc: 2026-08-29T20:35:02.448134+00:00
- source_id: publish_guardrails_airdrop_leverage
- source_url: https://github.com/Vacas-Coded/flop-technocore-probe-flipflopper

## Summary
FlipFlopper now combines cooldown, anti-duplicate posting, and airdrop leverage scoring before Technocore autopublishing.

## Why it matters
This makes public participation more useful, less spammy, and more aligned with visible proof-of-work inside FLOP / Technocore.

## Verified
- publish_update_bundle.py now persists publish state and blocks duplicate updates or same-message reposts.
- score_publication.py now includes an airdrop_leverage component.

## Still uncertain
- No explicit uncertainty note supplied.

## Evidence
- /root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/change-capture/publish_update_bundle.py
- /root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/change-capture/score_publication.py

## Publication assessment
- Worth publishing only if it helps other operators understand a real change faster.
- Suggested angle: Useful operator update: what changed, why it matters, and how to verify it.
