#!/usr/bin/env python3
import argparse
import importlib.util
import json
import pathlib
import sys
from datetime import datetime, timezone

FIRST_CONTACT = pathlib.Path('/root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/first-contact-runner/flop_first_contact.py')
WALLET_ADAPTER = pathlib.Path('/root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/activation-adapters/wallet_adapter.py')
OUT = pathlib.Path('/root/.hermes/document_cache/flop_armed_runners/wallet')


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'cannot load module {name} from {path}')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write_report(report: dict) -> dict[str, str]:
    OUT.mkdir(parents=True, exist_ok=True)
    stem = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    jp = OUT / f'{stem}_wallet_runner.json'
    mp = OUT / f'{stem}_wallet_runner.md'
    jp.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    lines = [
        '# FlipFlopper Wallet Connect Runner Report', '',
        f"Generated: {report['generated_at']}", '',
        f"- url: {report['url']}",
        f"- mode: `{report['mode']}`",
        f"- allowed_to_attempt_side_effect: `{report['allowed_to_attempt_side_effect']}`",
        f"- gate_passed: `{report['gate_passed']}`",
        f"- status: `{report['inspection']['status']}`",
        f"- capability: `{report['inspection']['capability']}`",
        '', '## Blockers'
    ]
    lines += [f"- {x}" for x in report['blockers']] or ['- none']
    lines += ['', '## Next steps'] + [f"- {x}" for x in report['next_steps']]
    mp.write_text('\n'.join(lines) + '\n')
    return {'json': str(jp), 'markdown': str(mp)}


def main():
    ap = argparse.ArgumentParser(description='Armed-but-safe wallet connect runner')
    ap.add_argument('url')
    ap.add_argument('--armed', action='store_true')
    ap.add_argument('--acknowledge-side-effects', action='store_true')
    ap.add_argument('--pretty', action='store_true')
    args = ap.parse_args()

    first = load_module('flip_first_contact', FIRST_CONTACT)
    adapter = load_module('flip_wallet_adapter', WALLET_ADAPTER)
    inspection = first.inspect(args.url)
    derived = adapter.derive(inspection)
    blockers = []
    if inspection.get('status') != 200:
        blockers.append('route_not_http_200')
    if inspection.get('capability') == 'unavailable':
        blockers.append('surface_unavailable')
    if not derived.get('ready_for_manual_connect_review'):
        blockers.append('not_ready_for_manual_connect_review')
    if not args.armed:
        blockers.append('runner_not_armed')
    if not args.acknowledge_side_effects:
        blockers.append('side_effects_not_acknowledged')

    gate_passed = not blockers
    report = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'runner': 'wallet_connect',
        'url': args.url,
        'mode': 'armed_gate' if args.armed else 'safe_blocked',
        'allowed_to_attempt_side_effect': gate_passed,
        'gate_passed': gate_passed,
        'inspection': inspection,
        'derived': derived,
        'blockers': blockers,
        'next_steps': adapter.recommend(derived, inspection) + ['manual approval still required before any real wallet connect or sign flow'],
    }
    report['artifacts'] = write_report(report)
    json.dump(report, sys.stdout, indent=2 if args.pretty else None, ensure_ascii=False)
    sys.stdout.write('\n')
    raise SystemExit(0 if gate_passed else 2)


if __name__ == '__main__':
    main()
