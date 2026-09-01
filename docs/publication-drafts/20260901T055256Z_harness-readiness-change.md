# Draft — Harness readiness change

## Short post
readiness_score: 70 -> 64; missing_gates: ['explicit_live_testnet_entrypoint'] -> ['core_docs_availability', 'explicit_live_testnet_entrypoint'] A readiness transition can signal that FLOP testnet preparation or live entrypoints materially changed. Evidence-first takeaway: Useful operator update: what changed, why it matters, and how to verify it.

## Bullet version
- Change: readiness_score: 70 -> 64; missing_gates: ['explicit_live_testnet_entrypoint'] -> ['core_docs_availability', 'explicit_live_testnet_entrypoint']
- Why it matters: A readiness transition can signal that FLOP testnet preparation or live entrypoints materially changed.
- Verification: Harness rerun completed at 2026-09-01 05:52:29 UTC
- Evidence: /root/.hermes/document_cache/flop_testnet_harness/20260901T055256Z_readiness.json

## Guardrail
- Do not publish stronger claims than the evidence supports.
