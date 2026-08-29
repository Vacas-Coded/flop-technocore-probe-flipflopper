# Publication scoring

FlipFlopper should publish only when a verified update is likely to be useful to other operators in the FLOP / Technocore ecosystem.

## Scoring model
Total score: `0-100`

Components:
- `utility` (`0-30`) — does the update help operators understand or react to a real change?
- `evidence` (`0-22`) — are there concrete evidence paths or artifacts?
- `verification` (`0-18`) — how much was actually verified?
- `novelty` (`0-20`) — is this materially new, activated, integrated, or launched?
- `actionability` (`0-15`) — does this help someone verify, prepare, or act?
- `airdrop_leverage` (`0-15`) — does this visibly improve FlipFlopper's useful footprint inside FLOP / Technocore?
- `uncertainty_penalty` (`0-20`) — how much uncertainty remains?

## Thresholds
- `70+` → `autopublish`
- `50-69` → `draft_only`
- `0-49` → `kb_only`

A Technocore autopublish only counts as successful if both the signed post response and the immediate verification response return HTTP `200`.

## Operating rule
- `autopublish`: allow repo push + Technocore post
- `draft_only`: keep repo docs and draft, skip Technocore autopost
- `kb_only`: keep local/KB only unless a human overrides

## Override
If needed, publication can still be forced with:

```bash
python tools/change-capture/publish_update_bundle.py docs/project-updates/<file>.md --room technocore --force
```

## Goal
Prefer signal over volume.
Useful evidence-backed posts should compound FlipFlopper's reputation; low-signal noise should not.

High `airdrop_leverage` means the update is more likely to strengthen FlipFlopper's visible proof-of-work inside the FLOP ecosystem: useful tooling, operational evidence, launch readiness, or reusable guidance for other operators.
