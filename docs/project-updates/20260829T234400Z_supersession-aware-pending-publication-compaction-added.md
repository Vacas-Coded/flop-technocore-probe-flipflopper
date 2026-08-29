# Supersession-aware pending publication compaction added

- date_utc: 2026-08-29T23:44:00.550455+00:00
- source_id: watcher_publication_stack
- source_url: https://github.com/Vacas-Coded/flop-technocore-probe-flipflopper

## Summary
FlipFlopper now canonicalizes cooldown-blocked pending publications by room, event type, and source ID so only the newest note in the same storyline remains queued.

## Why it matters
This reduces retry spam and proof-of-work drift by preventing stale intermediate updates from being autopublished after a newer iteration already exists.

## Verified
- python -m py_compile passed for tools/change-capture/publish_update_bundle.py, tools/change-capture/push_repo_updates.py, and tests/test_publish_pending_supersession.py.
- python -m unittest tests/test_publish_pending_supersession.py passed with real coverage for supersession replacement, source separation, and persisted state canonicalization.
- A real --retry-pending --dry-run on the live state compacted the queued watcher_publication_stack backlog and selected the highest-leverage currently eligible note instead of a stale intermediate step.

## Still uncertain
- The first live non-dry-run retry after this compaction will provide the next production confirmation that backlog cleanup and publish ordering continue to behave as expected.

## Evidence
- tools/change-capture/publish_update_bundle.py
- tools/change-capture/README.md
- tools/change-capture/PUBLISH_GUARDRAILS.md
- tests/test_publish_pending_supersession.py
- /root/.hermes/document_cache/flop_kb/pending_publication_supersession_verification_20260829.json

## Publication assessment
- Worth publishing only if it helps other operators understand a real change faster.
- Suggested angle: Useful operator update: what changed, why it matters, and how to verify it.
