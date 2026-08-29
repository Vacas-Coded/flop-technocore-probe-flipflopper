# flipflopper-armed-runners

Armed-but-safe runners for the moment a FLOP testnet surface becomes real.

## Included
- `claim_runner.py`
- `wallet_connect_runner.py`
- `docs_probe_runner.py`
- `dispatch_armed_runner.py`

## Safety model
- blocked by default
- require `--armed`
- side-effect-capable lanes also require `--acknowledge-side-effects`
- docs lane requires `--allow-get-probe`
- still preserve evidence even when blocked

## Important
These runners do **not** auto-claim, auto-connect wallets, or send non-GET requests.
They only decide whether the preconditions for a manual next step appear satisfied.

## Examples
```bash
python dispatch_armed_runner.py claim https://flop.finance/faucet --pretty
python dispatch_armed_runner.py wallet https://flop.finance/wallet --pretty
python dispatch_armed_runner.py docs https://technocore.chat/openapi.json --armed --allow-get-probe --pretty
```
