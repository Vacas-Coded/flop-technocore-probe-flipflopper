# change-capture

Utilities for turning a verified watcher change into:
- a repo-visible project update note
- a repo-visible publication draft
- an index entry in `docs/PROJECT_UPDATES.md`

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

python push_repo_updates.py
python publish_update_bundle.py docs/project-updates/<file>.md --room technocore
```
