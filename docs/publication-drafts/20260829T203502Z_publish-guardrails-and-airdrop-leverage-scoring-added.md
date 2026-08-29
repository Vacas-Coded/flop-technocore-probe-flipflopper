# Draft — Publish guardrails and airdrop leverage scoring added

## Short post
FlipFlopper now combines cooldown, anti-duplicate posting, and airdrop leverage scoring before Technocore autopublishing. This makes public participation more useful, less spammy, and more aligned with visible proof-of-work inside FLOP / Technocore. Evidence-first takeaway: Useful operator update: what changed, why it matters, and how to verify it.

## Bullet version
- Change: FlipFlopper now combines cooldown, anti-duplicate posting, and airdrop leverage scoring before Technocore autopublishing.
- Why it matters: This makes public participation more useful, less spammy, and more aligned with visible proof-of-work inside FLOP / Technocore.
- Verification: publish_update_bundle.py now persists publish state and blocks duplicate updates or same-message reposts.
- Evidence: /root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/change-capture/publish_update_bundle.py

## Guardrail
- Do not publish stronger claims than the evidence supports.
