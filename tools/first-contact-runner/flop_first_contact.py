#!/usr/bin/env python3
import argparse
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any

UA = 'FlipFlopper-FirstContact/1.0'
DEFAULT_OUTPUT_DIR = pathlib.Path('/root/.hermes/document_cache/flop_first_contact')
KNOWN_TYPES = ['faucet', 'app', 'wallet', 'inference', 'form', 'unknown']


class FormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms: list[dict[str, Any]] = []
        self._current: dict[str, Any] | None = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'form':
            self._current = {
                'action': attrs.get('action'),
                'method': (attrs.get('method') or 'GET').upper(),
                'inputs': [],
            }
            self.forms.append(self._current)
        elif tag in ('input', 'textarea', 'select') and self._current is not None:
            self._current['inputs'].append({
                'tag': tag,
                'name': attrs.get('name'),
                'type': attrs.get('type'),
                'required': 'required' in attrs,
                'placeholder': attrs.get('placeholder'),
            })


def fetch(url: str, retries: int = 3, timeout: int = 20) -> tuple[int, str, dict[str, str]]:
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html, text/plain, application/json'})
    last = (599, 'uninitialized', {})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read().decode('utf-8', 'ignore'), dict(r.headers.items())
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', 'ignore')
            last = (e.code, body, dict(e.headers.items()))
            if e.code not in (429, 500, 502, 503, 504) or attempt == retries - 1:
                return last
        except Exception as e:
            last = (599, str(e), {})
            if attempt == retries - 1:
                return last
        time.sleep(1 + attempt)
    return last


def clean(text: str) -> str:
    text = re.sub(r'(?is)<script.*?</script>', ' ', text)
    text = re.sub(r'(?is)<style.*?</style>', ' ', text)
    text = re.sub(r'(?is)<!--.*?-->', ' ', text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def detect_surface_type(url: str, cleaned: str, forms: list[dict[str, Any]]) -> str:
    url_l = url.lower()
    body_l = cleaned.lower()
    if 'faucet' in url_l or ' faucet ' in f' {body_l} ':
        return 'faucet'
    if 'wallet' in url_l or 'connect wallet' in body_l or 'wallet' in body_l:
        return 'wallet'
    if 'inference' in url_l or 'inference' in body_l or 'model' in body_l:
        return 'inference'
    if url_l.endswith('/app') or '/app/' in url_l or 'launch app' in body_l or 'dashboard' in body_l:
        return 'app'
    if forms:
        return 'form'
    return 'unknown'


def classify_capability(status: int, cleaned: str, forms: list[dict[str, Any]], headers: dict[str, str]) -> str:
    if status != 200:
        return 'unavailable'
    if forms:
        return 'form_only'
    if 'application/json' in (headers.get('Content-Type', '') or ''):
        return 'api_like'
    body_l = cleaned.lower()
    if 'connect wallet' in body_l or 'sign message' in body_l:
        return 'wallet_gated'
    if any(x in body_l for x in ['submit', 'claim', 'run inference', 'send request']):
        return 'action_capable'
    return 'view_only'


def recommend_next_steps(surface_type: str, capability: str) -> list[str]:
    common = [
        'save raw response and cleaned excerpt as evidence',
        'confirm the route remains stable with one immediate rerun',
        'do not infer eligibility rules beyond explicit source text',
    ]
    specific = {
        'faucet': [
            'extract claim requirements, cooldowns and wallet prerequisites',
            'check whether claiming is manual, signed or API-based',
        ],
        'wallet': [
            'identify supported chain(s), wallet(s) and signing flow',
            'confirm whether automation is appropriate or manual review is safer',
        ],
        'inference': [
            'capture auth requirements, request schema and quota semantics',
            'probe only safe read-only docs endpoints before any write/action attempt',
        ],
        'app': [
            'map visible navigation, gates and whether any action path is exposed',
            'capture forms, buttons and wallet prompts before interacting',
        ],
        'form': [
            'extract all fields and determine if this is activation or just interest collection',
            'prepare required identity data but do not submit automatically',
        ],
        'unknown': ['inspect manually before any action'],
    }
    cap = {
        'form_only': ['treat as non-activated until semantics are clear'],
        'wallet_gated': ['capture wallet gate evidence before attempting any connect flow'],
        'api_like': ['look for docs/schema before sending any non-GET request'],
        'action_capable': ['use dry-run evidence first, then ask before side effects'],
        'view_only': ['capture evidence; no safe action implied yet'],
        'unavailable': ['route is not live; keep watcher active'],
    }
    return common + specific.get(surface_type, []) + cap.get(capability, [])


def inspect(url: str) -> dict[str, Any]:
    status, body, headers = fetch(url)
    cleaned = clean(body)
    parser = FormParser()
    try:
        parser.feed(body)
    except Exception:
        pass
    surface_type = detect_surface_type(url, cleaned, parser.forms)
    capability = classify_capability(status, cleaned, parser.forms, headers)
    return {
        'url': url,
        'status': status,
        'surface_type': surface_type,
        'capability': capability,
        'content_type': headers.get('Content-Type'),
        'forms': parser.forms,
        'link_hints': sorted(set(re.findall(r'https?://[^\s"\'<>]+', body)))[:25],
        'excerpt': cleaned[:1200],
        'recommended_next_steps': recommend_next_steps(surface_type, capability),
    }


def write_artifacts(report: dict[str, Any], output_dir: pathlib.Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    json_path = output_dir / f'{stem}_first_contact.json'
    md_path = output_dir / f'{stem}_first_contact.md'
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')

    lines = [
        '# FlipFlopper First Contact Report', '',
        f"Generated: {report['generated_at']}", '',
        f"- url: {report['inspection']['url']}",
        f"- status: `{report['inspection']['status']}`",
        f"- surface_type: `{report['inspection']['surface_type']}`",
        f"- capability: `{report['inspection']['capability']}`",
        f"- content_type: `{report['inspection']['content_type']}`",
        '', '## Excerpt', report['inspection']['excerpt'], '',
        '## Forms',
    ]
    forms = report['inspection']['forms']
    if forms:
        for i, form in enumerate(forms, 1):
            lines.append(f"### Form {i}")
            lines.append(f"- action: `{form.get('action')}`")
            lines.append(f"- method: `{form.get('method')}`")
            for field in form.get('inputs', []):
                lines.append(f"  - {field.get('tag')} name=`{field.get('name')}` type=`{field.get('type')}` required=`{field.get('required')}`")
    else:
        lines.append('- none detected')
    lines += ['', '## Recommended next steps']
    for step in report['inspection']['recommended_next_steps']:
        lines.append(f'- {step}')
    md_path.write_text('\n'.join(lines) + '\n')
    return {'json': str(json_path), 'markdown': str(md_path)}


def main():
    ap = argparse.ArgumentParser(description='FlipFlopper first-contact runner')
    ap.add_argument('url')
    ap.add_argument('--expected-type', choices=KNOWN_TYPES, default='unknown')
    ap.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    ap.add_argument('--write-report', action='store_true')
    ap.add_argument('--pretty', action='store_true')
    args = ap.parse_args()

    report = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'mode': 'safe_read_only',
        'expected_type': args.expected_type,
        'inspection': inspect(args.url),
    }
    report['type_match'] = args.expected_type == 'unknown' or report['inspection']['surface_type'] == args.expected_type

    if args.write_report:
        report['artifacts'] = write_artifacts(report, pathlib.Path(args.output_dir))

    json.dump(report, sys.stdout, indent=2 if args.pretty else None, ensure_ascii=False)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
