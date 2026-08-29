# flipflopper-day0-operations

Day-0 operational kit for FLOP testnet opening.

## Contents
- `templates/evidence-capture-template.md`
- `templates/manual-claim-checklist.md`
- `templates/manual-wallet-connect-checklist.md`
- `templates/get-only-docs-probe-checklist.md`
- `decision-trees/claim-decision-tree.md`
- `decision-trees/wallet-connect-decision-tree.md`
- `decision-trees/get-only-docs-decision-tree.md`
- `generate_day0_packet.py`

## Purpose
This kit converts detection into repeatable operator behavior:
- capture evidence consistently
- choose the right path by surface type
- avoid premature side effects
- preserve proof for later attribution

## Example
```bash
python generate_day0_packet.py faucet https://flop.finance/faucet
python generate_day0_packet.py wallet https://flop.finance/wallet
python generate_day0_packet.py docs https://flop.finance/app
```
