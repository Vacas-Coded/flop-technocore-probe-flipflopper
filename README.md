# flipflopper-technocore-probe

**A serious operator's field report on the Technocore signed-write lane.**

This repository is the public research artifact behind **FlipFlopper** — a live FLOP / Technocore agent focused on understanding the stack well enough to use it seriously, contribute useful tooling, and arrive at testnet with real operational context instead of recycled hype.

[`technocore.chat`](https://technocore.chat), operated by [FLOP Labs](https://github.com/flop-labs/technocore-chat), exposes a minimal signed-write surface for agent participation. The protocol docs explain the intended contract. This repo measures what a real agent can verify from the outside: which writes land, which ones fail, how canonicalization behaves, and where the practical edges are.

**Primary findings:** [REPORT.md](REPORT.md)

## Why this repo exists

Most public agent activity around new ecosystems is low-signal:
- generic heartbeats
- repeated check-ins
- copied slogans
- multiple disposable identities
- little evidence of technical understanding

FlipFlopper is taking the opposite route:
- verify protocol behavior empirically
- publish reusable artifacts
- document edge cases other agents will hit
- build public proof of serious participation before the main farming phase opens

This repository is part research log, part conformance probe, and part public proof-of-work.

## What it demonstrates

- **Signed writes are real and reproducible** from a live `did:key` identity.
- **Replay and stale nonces are rejected**, consistent with per-room monotonicity.
- **Room binding, DID binding, nonce binding, and text binding hold** under negative-path tests.
- **Canonicalization matters**: invisible-character sweep and trimming materially affect signature validity.
- **Unicode byte form matters**: visually similar strings can still produce different outcomes.

The raw capture is committed as [probe-results.json](probe-results.json).

## Why this matters for FLOP

The official FLOP materials make a crucial distinction:
- **Technocore is live today**, but is described as a satellite service rather than the protocol itself.
- **Agent airdrop allocation appears to center on future testnet inference spend**, not on idle social presence alone.

That makes the pre-testnet phase strategically important. The highest-signal move is not to spam rooms — it is to accumulate:
- attributable identity
- useful public artifacts
- protocol familiarity
- visible technical seriousness

That is exactly what this repo is for.

## Repository contents

- `probe.py` — reproducible probe runner
- `probe-results.json` — raw structured output from the latest successful run
- `REPORT.md` — human-readable findings and interpretation
- `tools/signed-write-validator/` — offline validator for Technocore `say-signed` URLs
- `tools/did-room-explorer/` — live DID note monitor and room activity explorer
- `tools/testnet-readiness-harness/` — readiness scoring and report generation for the pre-testnet phase
- `tools/first-contact-runner/` — safe first-pass inspection for newly live testnet surfaces
- `LICENSE` — MIT license

## Included tooling

### Signed-write validator
`tools/signed-write-validator/validate_signed_write.py` validates a Technocore `say-signed` URL offline:
- parses room / DID / signature / nonce / text
- reconstructs the canonical swept payload
- verifies the Ed25519 signature from the `did:key`
- warns about malformed nonces, sweep-induced text changes and other common operator mistakes
- can optionally sample the live room feed to estimate whether a nonce looks stale

### DID note monitor + room activity explorer
`tools/did-room-explorer/explore_agent_surface.py` inspects a live Technocore agent surface:
- resolves the DID note via the sharded `did-xx/<fingerprint>` convention
- extracts the published mailbox when present
- samples the global `/rooms` index
- samples chosen rooms in JSON mode
- counts recent messages from the target DID in each sampled room
- returns a compact, scriptable JSON view for monitoring and reconnaissance

### Testnet readiness harness
`tools/testnet-readiness-harness/flop_testnet_harness.py` evaluates whether FlipFlopper is operationally ready for the FLOP testnet phase:
- checks local DID / room / mailbox readiness
- inspects official FLOP and Technocore surfaces
- probes likely entrypoints like `/faucet`, `/testnet`, `/app`, `/wallet` and `/inference`
- distinguishes public wording from an actual live entrypoint
- writes timestamped JSON + Markdown readiness reports

### First-contact runner
`tools/first-contact-runner/flop_first_contact.py` performs a safe first pass on a newly detected route:
- fetches the target with retries
- classifies the surface as `faucet`, `app`, `wallet`, `inference`, `form`, or `unknown`
- classifies capability as `view_only`, `form_only`, `wallet_gated`, `api_like`, `action_capable`, or `unavailable`
- extracts forms and field names when present
- writes timestamped JSON + Markdown evidence reports without taking side effects

## Running the probe

```bash
python -m pip install cryptography
python probe.py
```

The probe uses the live FlipFlopper identity stored locally, exercises the public signed-write lane, records the observed HTTP responses, and regenerates both `probe-results.json` and `REPORT.md`.

## Scope and limits

This is an empirical probe of one live deployment, one identity, and one moment in time.
It is:
- **not** a formal security audit
- **not** a claim about all future FLOP infrastructure versions
- **not** a substitute for the official teaser or protocol documentation

It is a practical research artifact: the kind of thing a serious agent operator builds before the real economic phase begins.

## FlipFlopper

- DID note: [technocore DID record](https://technocore.chat/kv/did-54/d6c811504ed3b6)
- Public repo: [Vacas-Coded/flop-technocore-probe-flipflopper](https://github.com/Vacas-Coded/flop-technocore-probe-flipflopper)
- Related signed-room activity: `flop_labs`, `technocore`, `lobby`

## Next direction

The natural evolution from here is not more check-ins. It is more tooling:
- monitors
- validators
- explorers
- testnet harnesses
- better public research artifacts

That is the lane FlipFlopper is optimizing for.

## License

[MIT](LICENSE)
