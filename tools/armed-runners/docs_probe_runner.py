#!/usr/bin/env python3
import argparse
import importlib.util
import json
import pathlib
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

FIRST_CONTACT = pathlib.Path('/root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/first-contact-runner/flop_first_contact.py')
APP_ADAPTER = pathlib.Path('/root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/activation-adapters/app_inference_adapter.py')
OUT = pathlib.Path('/root/.hermes/document_cache/flop_armed_runners/docs_probe')
UA = 'FlipFlopper-ArmedDocsProbe/1.0'


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'cannot load module {name} from {path}')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fetch_get(url: str) -> tuple[int, str, dict[str, str]]:
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json, text/plain, text/html'})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode('utf-8', 'ignore'), dict(r.headers.items())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'ignore'), dict(e.headers.items())


def write_report(report: dict) -> dict[str, str]:
    OUT.mkdir(parents=True, exist_ok=True)
    stem = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    jp = OUT / f'{stem}_docs_probe_runner.json'
    mp = OUT / f'{stem}_docs_probe_runner.md'
    jp.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    lines = [
        '# FlipFlopper Docs Probe Runner Report', '',
        f"Generated: {report['generated_at']}", '',
        f"- url: {report['url']}",
        f"- mode: `{report['mode']}`",
        f"- gate_passed: `{report['gate_passed']}`",
        f"- execution_performed: `{report['execution_performed']}`",
        f"- status: `{report['inspection']['status']}`",
        f"- capability: `{report['inspection']['capability']}`",
        '', '## Blockers'
    ]
    lines += [f"- {x}" for x in report['blockers']] or ['- none']
    if report.get('probe_result'):
        lines += ['', '## GET probe', f"- status: `{report['probe_result']['status']}`", f"- content_type: `{report['probe_result']['content_type']}`"]
    lines += ['', '## Next steps'] + [f"- {x}" for x in report['next_steps']]
    mp.write_text('\n'.join(lines) + '\n')
    return {'json': str(jp), 'markdown': str(mp)}


def main():
    ap = argparse.ArgumentParser(description='Armed-but-safe docs probe runner')
    ap.add_argument('url')
    ap.add_argument('--armed', action='store_true')
    ap.add_argument('--allow-get-probe', action='store_true')
    ap.add_argument('--pretty', action='store_true')
    args = ap.parse_args()

    first = load_module('flip_first_contact', FIRST_CONTACT)
    adapter = load_module('flip_app_adapter', APP_ADAPTER)
    inspection = first.inspect(args.url)
    derived = adapter.derive(inspection)
    blockers = []
    if inspection.get('status') != 200:
        blockers.append('route_not_http_200')
    if not derived.get('ready_for_safe_docs_probe'):
        blockers.append('not_ready_for_safe_docs_probe')
    if not args.armed:
        blockers.append('runner_not_armed')
    if not args.allow_get_probe:
        blockers.append('get_probe_not_allowed')

    probe_result = None
    execution_performed = False
    gate_passed = not blockers
    if gate_passed:
        status, body, headers = fetch_get(args.url)
        probe_result = {
            'status': status,
            'content_type': headers.get('Content-Type'),
            'length': len(body),
            'excerpt': body[:800],
        }
        execution_performed = True

    report = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'runner': 'docs_probe',
        'url': args.url,
        'mode': 'armed_get_only' if args.armed else 'safe_blocked',
        'gate_passed': gate_passed,
        'execution_performed': execution_performed,
        'inspection': inspection,
        'derived': derived,
        'blockers': blockers,
        'probe_result': probe_result,
        'next_steps': adapter.recommend(derived, inspection) + ['restrict follow-up to GET-only unless explicitly re-approved'],
    }
    report['artifacts'] = write_report(report)
    json.dump(report, sys.stdout, indent=2 if args.pretty else None, ensure_ascii=False)
    sys.stdout.write('\n')
    raise SystemExit(0 if gate_passed else 2)


if __name__ == '__main__':
    main()
