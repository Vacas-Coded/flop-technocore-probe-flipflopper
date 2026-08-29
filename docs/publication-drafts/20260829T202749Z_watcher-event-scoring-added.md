# Draft — Watcher event scoring added

## Short post
FlipFlopper watcher now applies event-specific publish thresholds on top of the base publication score before autoposting. This lets the agent treat docs changes, releases, harness transitions and live-surface activations differently, which should improve signal quality while staying aggressive on genuinely important FLOP events. Evidence-first takeaway: Useful operator update: what changed, why it matters, and how to verify it.

## Bullet version
- Change: FlipFlopper watcher now applies event-specific publish thresholds on top of the base publication score before autoposting.
- Why it matters: This lets the agent treat docs changes, releases, harness transitions and live-surface activations differently, which should improve signal quality while staying aggressive on genuinely important FLOP events.
- Verification: flipflopper_watch.py now classifies event types and applies watcher-side thresholds.
- Evidence: /root/.hermes/scripts/flipflopper_watch.py

## Guardrail
- Do not publish stronger claims than the evidence supports.
