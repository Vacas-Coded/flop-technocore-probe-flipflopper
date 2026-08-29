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
# rebuild guardrail state from prior successful publish logs
python rebuild_publish_state.py
# publish cooldown policy reference
cat DYNAMIC_COOLDOWN_POLICY.md
python push_repo_updates.py
python publish_update_bundle.py docs/project-updates/<file>.md --room technocore
# force publish if needed
python publish_update_bundle.py docs/project-updates/<file>.md --room technocore --force
```
