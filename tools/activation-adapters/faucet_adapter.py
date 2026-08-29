#!/usr/bin/env python3
import argparse
import importlib.util
import json
import pathlib
import sys
from datetime import datetime, timezone

FIRST_CONTACT = pathlib.Path('/root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/first-contact-runner/flop_first_contact.py')
OUTPUT_DIR = pathlib.Path('/root/.hermes/document_cache/flop_activation_adapters/faucet')


def load_first_contact():
    spec = importlib.util.spec_from_file_location('flip_first_contact', FIRST_CONTACT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'cannot load first-contact module from {FIRST_CONTACT}')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def derive(ins):
    excerpt = (ins.get('excerpt') or '').lower()
    forms = ins.get('forms') or []
    wallet_words = ['wallet', 'address', 'connect wallet', 'metamask', 'phantom']
    cooldown_words = ['cooldown', 'rate limit', 'once per', 'daily', 'hour']
    claim_words = ['claim', 'drip', 'mint', 'receive']
    return {
        'wallet_signals': [w for w in wallet_words if w in excerpt],
        'cooldown_signals': [w for w in cooldown_words if w in excerpt],
        'claim_signals': [w for w in claim_words if w in excerpt],
        'form_count': len(forms),
        'field_names': [f.get('name') for form in forms for f in form.get('inputs', []) if f.get('name')],
        'ready_for_manual_claim_attempt': ins.get('status') == 200 and ins.get('capability') in ('action_capable', 'wallet_gated', 'form_only'),
    }


def recommend(derived, ins):
    steps = [
        'capture faucet wording exactly as shown',
        'record wallet prerequisites and any supported chain hints',
        'rerun first-contact once to confirm stability',
    ]
    if derived['cooldown_signals']:
        steps.append('extract cooldown / rate-limit policy before any claim attempt')
    if derived['field_names']:
        steps.append('map form fields to required identity or wallet inputs; do not submit automatically')
    if ins.get('capability') == 'unavailable':
        steps.append('keep watcher active; faucet route still unavailable')
    else:
        steps.append('if manual claim becomes appropriate, ask before performing any side-effecting step')
    return steps


def write(report):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    jp = OUTPUT_DIR / f'{stem}_faucet_adapter.json'
    mp = OUTPUT_DIR / f'{stem}_faucet_adapter.md'
    jp.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    lines = [
        '# FlipFlopper Faucet Adapter Report', '',
        f"Generated: {report['generated_at']}", '',
        f"- url: {report['inspection']['url']}",
        f"- status: `{report['inspection']['status']}`",
        f"- capability: `{report['inspection']['capability']}`",
        f"- ready_for_manual_claim_attempt: `{report['derived']['ready_for_manual_claim_attempt']}`",
        '', '## Signals',
        f"- wallet: {', '.join(report['derived']['wallet_signals']) or 'none'}",
        f"- cooldown: {', '.join(report['derived']['cooldown_signals']) or 'none'}",
        f"- claim: {', '.join(report['derived']['claim_signals']) or 'none'}",
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
        'adapter': 'faucet',
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
