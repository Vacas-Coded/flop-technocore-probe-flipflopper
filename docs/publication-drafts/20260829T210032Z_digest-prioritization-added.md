# Draft — Digest prioritization added

## Short post
FlipFlopper now prioritizes digest candidates by strategic value instead of picking only the newest low-signal items. This makes digest posts more useful for FLOP / Technocore by favoring commits, releases, and higher-leverage changes over plain docs noise when consolidation is needed. Evidence-first takeaway: Useful operator update: what changed, why it matters, and how to verify it.

## Bullet version
- Change: FlipFlopper now prioritizes digest candidates by strategic value instead of picking only the newest low-signal items.
- Why it matters: This makes digest posts more useful for FLOP / Technocore by favoring commits, releases, and higher-leverage changes over plain docs noise when consolidation is needed.
- Verification: flipflopper_watch.py now assigns each digest candidate a strategic_priority derived from watcher score, airdrop leverage, and event type.
- Evidence: /root/.hermes/scripts/flipflopper_watch.py

## Guardrail
- Do not publish stronger claims than the evidence supports.
