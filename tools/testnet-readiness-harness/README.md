# flipflopper-testnet-readiness-harness

Readiness harness for the FLOP testnet phase.

## What it does
This tool does **not** pretend the testnet is live when it is not.
Instead, it answers a more useful question:

**If a real FLOP testnet surface appeared today, how ready is this agent stack to act immediately and capture evidence?**

It checks:
- FlipFlopper local identity config
- official FLOP surfaces
- Technocore docs relevant to agent participation
- visible application / onboarding surfaces
- testnet / inference / faucet / wallet wording on public pages

It then produces:
- a machine-readable JSON report
- an operator-friendly Markdown report
- a readiness score
- missing gates
- activation candidates to watch closely

## Why this exists
Most agents will only react after the testnet is obvious.
This harness is for being operational **before** the economic phase starts.

## Usage
```bash
python flop_testnet_harness.py --pretty
```

Write timestamped artifacts:
```bash
python flop_testnet_harness.py --write-report --pretty
```

Default output directory:
```text
/root/.hermes/document_cache/flop_testnet_harness/
```

## Output fields
- `flipflopper` — local DID / room / mailbox readiness
- `checks` — per-surface availability and keyword/signal extraction
- `readiness` — score, missing gates, activation candidates and recommended actions

## Scope
This harness is a **pre-testnet operations tool**.
It is not a protocol client, not a wallet, and not a claim that the FLOP testnet is already live.
