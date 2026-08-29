#!/usr/bin/env python3
import argparse
import pathlib
from datetime import datetime, timezone

BASE = pathlib.Path('/root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/day0-operations')
OUT = pathlib.Path('/root/.hermes/document_cache/flop_day0_packets')
MAP = {
    'faucet': [
        BASE / 'templates/evidence-capture-template.md',
        BASE / 'templates/manual-claim-checklist.md',
        BASE / 'decision-trees/claim-decision-tree.md',
    ],
    'wallet': [
        BASE / 'templates/evidence-capture-template.md',
        BASE / 'templates/manual-wallet-connect-checklist.md',
        BASE / 'decision-trees/wallet-connect-decision-tree.md',
    ],
    'docs': [
        BASE / 'templates/evidence-capture-template.md',
        BASE / 'templates/get-only-docs-probe-checklist.md',
        BASE / 'decision-trees/get-only-docs-decision-tree.md',
    ],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['faucet', 'wallet', 'docs'])
    ap.add_argument('url')
    args = ap.parse_args()
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    target = OUT / f'{ts}_{args.mode}'
    target.mkdir(parents=True, exist_ok=True)
    header = target / '00_context.md'
    header.write_text(f'# Day-0 Packet\n\n- generated_at: {datetime.now(timezone.utc).isoformat()}\n- mode: {args.mode}\n- url: {args.url}\n')
    for src in MAP[args.mode]:
        (target / src.name).write_text(src.read_text())
    print(str(target))


if __name__ == '__main__':
    main()
