# Wallet Connect Decision Tree

- Is the route HTTP 200?
  - No -> stop, keep watcher active.
  - Yes -> run first-contact runner.
- Does the surface show wallet or signing language?
  - No -> stop, treat as non-wallet surface.
  - Yes -> run wallet adapter.
- Is the flow clearly view-only?
  - Yes -> capture evidence, no connect.
  - No -> continue.
- Is the requested signature / permission fully visible?
  - No -> stop, no connect.
  - Yes -> capture wording and evidence.
- Would continuing create a side effect, exposure, or onchain permission?
  - Yes -> ask before any manual connect/sign.
  - No -> continue with cautious manual review only.
