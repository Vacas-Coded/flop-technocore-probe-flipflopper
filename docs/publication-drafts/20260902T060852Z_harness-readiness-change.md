# Draft — Harness readiness change

## Short post
readiness_score: 64 -> 70; live_probe_hits_count: 1 -> 2; missing_gates: ['core_docs_availability', 'explicit_live_testnet_entrypoint'] -> ['explicit_live_testnet_entrypoint'] A readiness transition can signal that FLOP testnet preparation or live entrypoints materially changed. Evidence-first takeaway: Useful operator update: what changed, why it matters, and how to verify it.

## Bullet version
- Change: readiness_score: 64 -> 70; live_probe_hits_count: 1 -> 2; missing_gates: ['core_docs_availability', 'explicit_live_testnet_entrypoint'] -> ['explicit_live_testnet_entrypoint']
- Why it matters: A readiness transition can signal that FLOP testnet preparation or live entrypoints materially changed.
- Verification: Harness rerun completed at 2026-09-02 06:08:16 UTC
- Evidence: /root/.hermes/document_cache/flop_testnet_harness/20260902T060852Z_readiness.json

## Guardrail
- Do not publish stronger claims than the evidence supports.
