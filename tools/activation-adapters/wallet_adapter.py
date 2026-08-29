#!/usr/bin/env python3
import argparse
import importlib.util
import json
import pathlib
import re
import sys
from datetime import datetime, timezone

FIRST_CONTACT = pathlib.Path('/root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/first-contact-runner/flop_first_contact.py')
OUTPUT_DIR = pathlib.Path('/root/.hermes/document_cache/flop_activation_adapters/wallet')


def load_first_contact():
    spec = importlib.util.spec_from_file_location('flip_first_contact', FIRST_CONTACT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'cannot load first-contact module from {FIRST_CONTACT}')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def derive(ins):
    excerpt = ins.get('excerpt') or ''
    low = excerpt.lower()
    wallets = [w for w in ['metamask', 'phantom', 'walletconnect', 'rabby', 'coinbase wallet'] if w in low]
    chains = [c for c in ['ethereum', 'base', 'solana', 'arbitrum', 'optimism', 'polygon'] if c in low]
    sign_msgs = [m.group(0) for m in re.finditer(r'(sign message|connect wallet|wallet)', low)][:10]
    return {
        'wallet_brands': wallets,
        'chain_hints': chains,
        'signing_signals': sign_msgs,
        'ready_for_manual_connect_review': ins.get('status') == 200 and ins.get('capability') in ('wallet_gated', 'action_capable', 'view_only'),
    }


def recommend(derived, ins):
    steps = [
        'capture the wallet gate and exact wording',
        'identify supported chains and wallet brands from the page before connecting anything',
        'confirm whether signing is informational auth or transaction-capable',
    ]
    if ins.get('capability') == 'unavailable':
        steps.append('no wallet route is live yet; keep watcher active')
    else:
        steps.append('do not connect or sign automatically; manual review first')
    return steps


def write(report):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    jp = OUTPUT_DIR / f'{stem}_wallet_adapter.json'
    mp = OUTPUT_DIR / f'{stem}_wallet_adapter.md'
    jp.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    lines = [
        '# FlipFlopper Wallet Adapter Report', '',
        f"Generated: {report['generated_at']}", '',
        f"- url: {report['inspection']['url']}",
        f"- status: `{report['inspection']['status']}`",
        f"- capability: `{report['inspection']['capability']}`",
        f"- ready_for_manual_connect_review: `{report['derived']['ready_for_manual_connect_review']}`",
        '', '## Hints',
        f"- wallets: {', '.join(report['derived']['wallet_brands']) or 'none'}",
        f"- chains: {', '.join(report['derived']['chain_hints']) or 'none'}",
        '', '## Recommended steps'
    ]
    lines += [f'- {x}' for x in report['recommended_steps']]
    mp.write_text('\n'.join(lines) + '\n')
    return {'json': str(jp), 'markdown': str(mp)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('url')
    ap.add_argument('--write-report', action='store_true')
    ap.add_argument('--pretty', action='store_true')
    args = ap.parse_args()
    mod = load_first_contact()
    ins = mod.inspect(args.url)
    report = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'adapter': 'wallet',
        'mode': 'safe_read_only',
        'inspection': ins,
        'derived': derive(ins),
    }
    report['recommended_steps'] = recommend(report['derived'], ins)
    if args.write_report:
        report['artifacts'] = write(report)
    json.dump(report, sys.stdout, indent=2 if args.pretty else None, ensure_ascii=False)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
