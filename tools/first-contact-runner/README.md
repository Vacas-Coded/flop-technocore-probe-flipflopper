# flipflopper-first-contact-runner

Safe first-contact runner for newly detected FLOP surfaces.

## What it does
When the watcher or harness detects a likely live route, this runner performs a **read-only first pass**:
- fetches the URL with retries
- classifies the surface (`faucet`, `app`, `wallet`, `inference`, `form`, `unknown`)
- detects whether it looks `view_only`, `form_only`, `wallet_gated`, `api_like`, or `action_capable`
- extracts forms and field names when present
- writes JSON + Markdown evidence reports

## What it does not do
By design, this tool does **not**:
- submit forms
- connect wallets
- perform claims
- send POST requests
- assume eligibility mechanics

It is a safe reconnaissance step, not an auto-farmer.

## Usage
```bash
python flop_first_contact.py https://flop.finance/faucet --expected-type faucet --write-report --pretty
```

## Output
Reports are written under `/root/.hermes/document_cache/flop_first_contact/` by default.

## Why this matters
The right first move on a newly live route is not blind interaction. It is:
1. verify the route is real
2. classify the gate
3. capture evidence
4. decide the next action from facts
