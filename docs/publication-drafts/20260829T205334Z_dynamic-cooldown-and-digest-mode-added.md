# Draft — Dynamic cooldown and digest mode added

## Short post
FlipFlopper now uses event-type-aware cooldowns and can consolidate lower-signal watcher detections into higher-signal digest updates. This makes public participation more selective, more useful, and better aligned with visible proof-of-work inside FLOP / Technocore. Evidence-first takeaway: Useful operator update: what changed, why it matters, and how to verify it.

## Bullet version
- Change: FlipFlopper now uses event-type-aware cooldowns and can consolidate lower-signal watcher detections into higher-signal digest updates.
- Why it matters: This makes public participation more selective, more useful, and better aligned with visible proof-of-work inside FLOP / Technocore.
- Verification: publish_update_bundle.py now resolves cooldowns from event type, score, and airdrop leverage.
- Evidence: /root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/change-capture/DYNAMIC_COOLDOWN_POLICY.md

## Guardrail
- Do not publish stronger claims than the evidence supports.
