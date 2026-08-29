# Draft — Autonomous retry for cooldown-blocked publications added

## Short post
FlipFlopper now retries eligible cooldown-blocked autopublish items automatically on later watcher cycles, with dry-run preview support and stronger queue prioritization. This closes the gap between queued high-signal work and actual publication, improving autonomous readiness without weakening anti-spam guardrails. Evidence-first takeaway: Useful operator update: what changed, why it matters, and how to verify it.

## Bullet version
- Change: FlipFlopper now retries eligible cooldown-blocked autopublish items automatically on later watcher cycles, with dry-run preview support and stronger queue prioritization.
- Why it matters: This closes the gap between queued high-signal work and actual publication, improving autonomous readiness without weakening anti-spam guardrails.
- Verification: python -m py_compile passed for publish_update_bundle.py and flipflopper_watch.py after the retry changes.
- Evidence: tools/change-capture/publish_update_bundle.py

## Guardrail
- Do not publish stronger claims than the evidence supports.
