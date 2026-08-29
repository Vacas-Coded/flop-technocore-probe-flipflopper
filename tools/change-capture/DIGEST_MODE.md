# Digest mode

Lower-signal watcher detections should not all become standalone Technocore posts.

## Eligibility
A watcher item becomes a digest candidate when:
- it has a scored repo update
- its watcher decision is `draft_only` or `kb_only`
- it is not a `live_surface_activation`

## Queue
Candidates are persisted in watcher state and deduplicated by `update_path`.

## Digest trigger
A digest is created when:
- at least `2` candidates exist, and
- either combined score is `>= 120`, or the oldest candidate is at least `12h` old

## Limits
- newest `4` candidates are grouped into a single digest
- candidates older than `48h` are dropped

## Goal
Convert scattered low-signal changes into one higher-signal operator summary that is more worthy of public feed space.
