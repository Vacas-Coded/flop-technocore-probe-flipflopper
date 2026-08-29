# Claim Decision Tree

- Is the route HTTP 200?
  - No -> stop, keep watcher active.
  - Yes -> run first-contact runner.
- Does first-contact classify it as `faucet` or show explicit claim wording?
  - No -> stop, treat as non-claim surface.
  - Yes -> run faucet adapter.
- Is capability `unavailable`?
  - Yes -> stop.
  - No -> capture claim wording and cooldowns.
- Are requirements explicit and understandable?
  - No -> stop, no action.
  - Yes -> capture evidence template fully.
- Is a side effect required to continue?
  - No -> continue with read-only documentation.
  - Yes -> ask before any manual claim attempt.
