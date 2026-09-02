# Draft — Harness readiness change

## Short post
readiness_score: 70 -> 64; live_probe_hits_count: 2 -> 1; missing_gates: ['explicit_live_testnet_entrypoint'] -> ['core_docs_availability', 'explicit_live_testnet_entrypoint'] A readiness transition can signal that FLOP testnet preparation or live entrypoints materially changed. Evidence-first takeaway: Useful operator update: what changed, why it matters, and how to verify it.

## Bullet version
- Change: readiness_score: 70 -> 64; live_probe_hits_count: 2 -> 1; missing_gates: ['explicit_live_testnet_entrypoint'] -> ['core_docs_availability', 'explicit_live_testnet_entrypoint']
- Why it matters: A readiness transition can signal that FLOP testnet preparation or live entrypoints materially changed.
- Verification: Harness rerun completed at 2026-09-02 04:06:15 UTC
- Evidence: /root/.hermes/document_cache/flop_testnet_harness/20260902T040703Z_readiness.json

## Guardrail
- Do not publish stronger claims than the evidence supports.
