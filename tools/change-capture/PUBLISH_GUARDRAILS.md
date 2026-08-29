# Technocore publish guardrails

FlipFlopper should not repost the same thing or flood Technocore with near-duplicate updates.

## Guardrails
- hard duplicate block by `update_path` if that update was already published successfully
- hard duplicate block by `message_hash` if the same room already got the same message successfully
- room-level cooldown window before another successful autopost is allowed
- same-event cooldown memory is also tracked to avoid bursts of one event class
- source-aware suppression should stop trivial repo metadata churn (for example `updated_at` or `open_issues_count +/-1`) before it even becomes a repo update or draft
- `--force` can override these blocks when a human explicitly decides it is worth it

## Default cooldown
- `180` minutes per room

## State
Publish state is tracked in:
- `/root/.hermes/flipflopper/publish_state.json`

The state keeps:
- recent attempts
- last successful post per room
- last successful post per room and event type
- last successful status by update path
- last successful status by message hash
- last attempt by update path
- last attempt by message hash
- pending autopublish items blocked only by cooldown, with their next `eligible_at`

## Cooldown-aware deferral
- if an update is autopublish-worthy but blocked only by `room_cooldown_active` and/or `same_event_cooldown_active`, it is queued instead of being effectively forgotten
- the queue preserves the update path, room, event type, score, last guardrail log, and the next retry time derived from cooldown state
- when multiple queued items become eligible together, the retry path prefers the highest-score and highest-leverage candidate among the oldest eligible slot
- operators can retry the next eligible item with:

```bash
python publish_update_bundle.py --retry-pending --room technocore
```

- operators can preview the next retry candidate without side effects with:

```bash
python publish_update_bundle.py --retry-pending --room technocore --dry-run
```

- the FlipFlopper watcher also runs this guarded retry automatically on each cycle, so expired cooldowns can release queued work without human babysitting

## Goal
Prefer compounding evidence-backed signal over noisy repetition.
