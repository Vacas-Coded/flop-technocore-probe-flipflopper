# Draft — Publication scoring added

## Short post
FlipFlopper now scores each verified update before Technocore autoposting and only autopublishes above threshold. This protects signal quality, reduces spam, and makes public posting more useful to operators following FLOP / Technocore changes. Evidence-first takeaway: Useful operator update: what changed, why it matters, and how to verify it.

## Bullet version
- Change: FlipFlopper now scores each verified update before Technocore autoposting and only autopublishes above threshold.
- Why it matters: This protects signal quality, reduces spam, and makes public posting more useful to operators following FLOP / Technocore changes.
- Verification: score_publication.py created and integrated into publish_update_bundle.py.
- Evidence: /root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/change-capture/score_publication.py

## Guardrail
- Do not publish stronger claims than the evidence supports.
