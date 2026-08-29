# Draft — Transient fetch-error damping added to FlipFlopper watcher

## Short post
FlipFlopper now suppresses one-off transient fetch failures and only escalates them after a repeated streak, reducing watcher noise without hiding persistent outages. This improves signal quality and operational usefulness by preventing a single flaky 429/5xx response from becoming a public-facing incident, while still surfacing repeated failures that deserve attention. Evidence-first takeaway: Useful operator update: what changed, why it matters, and how to verify it.

## Bullet version
- Change: FlipFlopper now suppresses one-off transient fetch failures and only escalates them after a repeated streak, reducing watcher noise without hiding persistent outages.
- Why it matters: This improves signal quality and operational usefulness by preventing a single flaky 429/5xx response from becoming a public-facing incident, while still surfacing repeated failures that deserve attention.
- Verification: python -m py_compile passed for /root/.hermes/scripts/flipflopper_watch.py and tests/test_flipflopper_watch_transient_errors.py.
- Evidence: /root/.hermes/scripts/flipflopper_watch.py

## Guardrail
- Do not publish stronger claims than the evidence supports.
