# Watcher scoring policy

The watcher should not treat all changes equally.
It applies an event-specific threshold layer on top of the base publication score.

## Event classes and thresholds
- `docs_change` → autopublish `82+`, draft_only `58+`
- `repo_metadata_change` → autopublish `78+`, draft_only `55+`
- `commit_change` → autopublish `76+`, draft_only `54+`
- `release_change` → autopublish `72+`, draft_only `52+`
- `harness_change` → autopublish `84+`, draft_only `60+`
- `live_surface_activation` → autopublish `68+`, draft_only `52+`

## Interpretation
- docs and harness changes need a higher bar because many are informative but not worth feed noise
- releases and live-surface activations deserve a lower bar because they are more likely to matter operationally
- if the watcher decision is not `autopublish`, the update can still be kept as repo docs and/or draft material

## Goal
Maximize useful signal in Technocore while still documenting everything important in the repo.
