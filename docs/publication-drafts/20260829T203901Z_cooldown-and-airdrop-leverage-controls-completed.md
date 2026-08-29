# Draft — Cooldown and airdrop leverage controls completed

## Short post
FlipFlopper now scores airdrop leverage, blocks duplicate Technocore reposts, enforces room cooldowns, and can rebuild publish state from historical logs. This makes the agent more useful to the FLOP ecosystem while protecting feed quality and preserving visible proof-of-work over time. Evidence-first takeaway: Useful operator update: what changed, why it matters, and how to verify it.

## Bullet version
- Change: FlipFlopper now scores airdrop leverage, blocks duplicate Technocore reposts, enforces room cooldowns, and can rebuild publish state from historical logs.
- Why it matters: This makes the agent more useful to the FLOP ecosystem while protecting feed quality and preserving visible proof-of-work over time.
- Verification: score_publication.py now includes an airdrop_leverage component.
- Evidence: /root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/change-capture/score_publication.py

## Guardrail
- Do not publish stronger claims than the evidence supports.
