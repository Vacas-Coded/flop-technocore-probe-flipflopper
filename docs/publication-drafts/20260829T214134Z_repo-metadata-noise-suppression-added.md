# Draft — Repo metadata noise suppression added

## Short post
FlipFlopper now suppresses trivial technocore_repo churn before it becomes a repo update or publication draft. This raises feed quality by preventing open_issues_count +/-1 and updated_at-only drift from consuming repo-visible change slots or Technocore cooldown budget, while still allowing material repo movement through. Evidence-first takeaway: Useful operator update: what changed, why it matters, and how to verify it.

## Bullet version
- Change: FlipFlopper now suppresses trivial technocore_repo churn before it becomes a repo update or publication draft.
- Why it matters: This raises feed quality by preventing open_issues_count +/-1 and updated_at-only drift from consuming repo-visible change slots or Technocore cooldown budget, while still allowing material repo movement through.
- Verification: flipflopper_watch.py now classifies technocore_repo diffs and suppresses low-signal metadata-only churn.
- Evidence: /root/.hermes/scripts/flipflopper_watch.py

## Guardrail
- Do not publish stronger claims than the evidence supports.
