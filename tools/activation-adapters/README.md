# flipflopper-activation-adapters

Surface-specific safe adapters for the day FLOP opens a real testnet route.

## Included adapters
- `faucet_adapter.py`
- `wallet_adapter.py`
- `app_inference_adapter.py`
- `dispatch_adapter.py`

## Purpose
These adapters sit **after** the first-contact runner.
They do not submit transactions, connect wallets, or send POSTs.
They only:
- classify the surface more specifically
- derive operator-relevant hints
- emit a tighter next-step brief
- write timestamped evidence artifacts

## Examples
```bash
python dispatch_adapter.py faucet https://flop.finance/faucet --write-report --pretty
python dispatch_adapter.py wallet https://flop.finance/wallet --write-report --pretty
python dispatch_adapter.py app https://flop.finance/app --write-report --pretty
```

## Output dirs
- faucet: `/root/.hermes/document_cache/flop_activation_adapters/faucet/`
- wallet: `/root/.hermes/document_cache/flop_activation_adapters/wallet/`
- app/inference: `/root/.hermes/document_cache/flop_activation_adapters/app_inference/`
