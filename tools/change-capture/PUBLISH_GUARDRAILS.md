# Technocore publish guardrails

FlipFlopper should not repost the same thing or flood Technocore with near-duplicate updates.

## Guardrails
- hard duplicate block by `update_path` if that update was already published successfully
- hard duplicate block by `message_hash` if the same room already got the same message successfully
- room-level cooldown window before another successful autopost is allowed
- `--force` can override these blocks when a human explicitly decides it is worth it

## Default cooldown
- `180` minutes per room

## State
Publish state is tracked in:
- `/root/.hermes/flipflopper/publish_state.json`

The state keeps:
- recent attempts
- last successful post per room
- last status by update path
- last status by message hash

## Goal
Prefer compounding evidence-backed signal over noisy repetition.
