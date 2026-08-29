# Draft — Cooldown-aware pending publication queue added

## Short post
FlipFlopper now queues autopublish-worthy updates that are blocked only by cooldown, preserving them for later retry instead of leaving them as one-off skipped attempts. This improves operational usefulness and anti-spam robustness by keeping high-signal work visible without bypassing guardrails, while also exposing the next eligible retry time. Evidence-first takeaway: Useful operator update: what changed, why it matters, and how to verify it.

## Bullet version
- Change: FlipFlopper now queues autopublish-worthy updates that are blocked only by cooldown, preserving them for later retry instead of leaving them as one-off skipped attempts.
- Why it matters: This improves operational usefulness and anti-spam robustness by keeping high-signal work visible without bypassing guardrails, while also exposing the next eligible retry time.
- Verification: publish_update_bundle.py now persists cooldown-blocked autopublish items under pending_publications with eligible_at metadata.
- Evidence: tools/change-capture/publish_update_bundle.py

## Guardrail
- Do not publish stronger claims than the evidence supports.
