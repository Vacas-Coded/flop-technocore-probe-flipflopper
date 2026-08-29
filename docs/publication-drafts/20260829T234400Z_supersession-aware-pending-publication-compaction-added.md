# Draft — Supersession-aware pending publication compaction added

## Short post
FlipFlopper now canonicalizes cooldown-blocked pending publications by room, event type, and source ID so only the newest note in the same storyline remains queued. This reduces retry spam and proof-of-work drift by preventing stale intermediate updates from being autopublished after a newer iteration already exists. Evidence-first takeaway: Useful operator update: what changed, why it matters, and how to verify it.

## Bullet version
- Change: FlipFlopper now canonicalizes cooldown-blocked pending publications by room, event type, and source ID so only the newest note in the same storyline remains queued.
- Why it matters: This reduces retry spam and proof-of-work drift by preventing stale intermediate updates from being autopublished after a newer iteration already exists.
- Verification: python -m py_compile passed for tools/change-capture/publish_update_bundle.py, tools/change-capture/push_repo_updates.py, and tests/test_publish_pending_supersession.py.
- Evidence: tools/change-capture/publish_update_bundle.py

## Guardrail
- Do not publish stronger claims than the evidence supports.
