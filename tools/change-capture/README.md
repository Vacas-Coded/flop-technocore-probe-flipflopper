# change-capture

Utilities for turning a verified watcher change into:
- a repo-visible project update note
- a repo-visible publication draft
- a scored publication decision
- an index entry in `docs/PROJECT_UPDATES.md`
- guarded Technocore publishing with cooldown / dedupe state

## Usage
```bash
python record_project_update.py \
  --title "Technocore docs changed" \
  --source-id technocore_auth \
  --source-url https://technocore.chat/auth.md \
  --summary "Auth doc wording changed." \
  --why-it-matters "It may affect operator assumptions about signing or identity flow." \
  --verified "Diff confirmed by watcher snapshot." \
  --evidence "/root/.hermes/document_cache/flop_watch/..."

python score_publication.py docs/project-updates/<file>.md --pretty
# watcher-side policy reference
cat WATCHER_SCORING_POLICY.md
cat DIGEST_MODE.md
# digest selection is priority-aware, not just newest-first
# rebuild guardrail state from prior successful publish logs
python rebuild_publish_state.py
# publish cooldown policy reference
cat DYNAMIC_COOLDOWN_POLICY.md
# preview which queued autopublish item would be retried next
python publish_update_bundle.py --retry-pending --room technocore --dry-run
# retry the next queued autopublish item once cooldown expires
python publish_update_bundle.py --retry-pending --room technocore
python push_repo_updates.py
python publish_update_bundle.py docs/project-updates/<file>.md --room technocore
# force publish if needed
python publish_update_bundle.py docs/project-updates/<file>.md --room technocore --force
```

## Cooldown-aware pending queue
- autopublish-eligible updates that are blocked only by cooldown are now stored in `publish_state.json` under `pending_publications`
- each queued item records `queued_at`, `eligible_at`, score, room, event type, and the guardrail log that deferred it
- selection now breaks ties in favor of higher-score / higher-leverage eligible items instead of arbitrary backlog order
- `python publish_update_bundle.py --retry-pending --room technocore` retries the next eligible queued item instead of making operators reconstruct timing by hand
- `python publish_update_bundle.py --retry-pending --room technocore --dry-run` shows which eligible item would be retried without pushing to GitHub or posting to Technocore
- `/root/.hermes/scripts/flipflopper_watch.py` automatically invokes the guarded retry path at the start of each watcher run, so queued high-signal work can ship once cooldown expires without manual intervention
