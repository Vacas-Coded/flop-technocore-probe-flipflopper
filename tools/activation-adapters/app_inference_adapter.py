#!/usr/bin/env python3
import argparse
import importlib.util
import json
import pathlib
import re
import sys
from datetime import datetime, timezone

FIRST_CONTACT = pathlib.Path('/root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/first-contact-runner/flop_first_contact.py')
OUTPUT_DIR = pathlib.Path('/root/.hermes/document_cache/flop_activation_adapters/app_inference')


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
    auth = [x for x in ['api key', 'bearer', 'authorization', 'login', 'sign in', 'nonce', 'signature'] if x in low]
    quota = [x for x in ['quota', 'rate limit', 'credits', 'token', 'usage'] if x in low]
    schema = [m.group(0) for m in re.finditer(r'(json|openapi|schema|endpoint|model)', low)][:10]
    return {
        'auth_hints': auth,
        'quota_hints': quota,
        'schema_hints': schema,
        'api_like': ins.get('capability') == 'api_like',
        'ready_for_safe_docs_probe': ins.get('status') == 200,
    }


def recommend(derived, ins):
    steps = [
        'capture docs/schema/auth wording before any non-GET request',
        'identify whether the surface is app UI, inference API, or mixed gateway',
        'save any endpoint or model identifiers as evidence',
    ]
    if derived['api_like']:
        steps.append('safe next step would be GET-only docs probing, not POST execution')
    if ins.get('capability') == 'unavailable':
        steps.append('app/inference route is not live yet; keep watcher active')
    return steps


def write(report):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    jp = OUTPUT_DIR / f'{stem}_app_inference_adapter.json'
    mp = OUTPUT_DIR / f'{stem}_app_inference_adapter.md'
    jp.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    lines = [
        '# FlipFlopper App/Inference Adapter Report', '',
        f"Generated: {report['generated_at']}", '',
        f"- url: {report['inspection']['url']}",
        f"- status: `{report['inspection']['status']}`",
        f"- capability: `{report['inspection']['capability']}`",
        f"- api_like: `{report['derived']['api_like']}`",
        '', '## Hints',
        f"- auth: {', '.join(report['derived']['auth_hints']) or 'none'}",
        f"- quota: {', '.join(report['derived']['quota_hints']) or 'none'}",
        f"- schema: {', '.join(report['derived']['schema_hints']) or 'none'}",
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
        'adapter': 'app_inference',
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
