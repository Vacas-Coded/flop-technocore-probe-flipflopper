#!/usr/bin/env python3
import argparse
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

UA = 'FlipFlopper-TestnetHarness/1.0'
FLIPFLOPPER_CONFIG = pathlib.Path('/root/.hermes/flipflopper/config.json')
DEFAULT_OUTPUT_DIR = pathlib.Path('/root/.hermes/document_cache/flop_testnet_harness')

TARGETS = [
    {
        'id': 'flop_teaser',
        'url': 'https://flop.finance/teaser/',
        'kind': 'html',
        'keywords': ['testnet', 'mainnet', 'airdrop', 'agent', 'inference', 'validator', 'miner', 'wallet', 'faucet'],
    },
    {
        'id': 'flop_llms',
        'url': 'https://flop.finance/llms.txt',
        'kind': 'text',
        'keywords': ['testnet', 'airdrop', 'validator', 'miners', 'kol', 'yellow paper'],
    },
    {
        'id': 'apply_miner',
        'url': 'https://flop.finance/apply/miner',
        'kind': 'html',
        'keywords': ['apply', 'miner', 'gpu', 'network'],
    },
    {
        'id': 'apply_validator',
        'url': 'https://flop.finance/apply/validator',
        'kind': 'html',
        'keywords': ['apply', 'validator', 'network'],
    },
    {
        'id': 'apply_kol',
        'url': 'https://flop.finance/apply/kol',
        'kind': 'html',
        'keywords': ['apply', 'creator', 'kol'],
    },
    {
        'id': 'technocore_auth',
        'url': 'https://technocore.chat/auth.md',
        'kind': 'text',
        'keywords': ['did:key', 'say-signed', 'nonce', 'mailbox'],
    },
    {
        'id': 'technocore_patterns',
        'url': 'https://technocore.chat/patterns.md',
        'kind': 'text',
        'keywords': ['mailbox', 'did note', 'room-owners', 'e2e'],
    },
]

ENTRYPOINT_PROBES = [
    'https://flop.finance/faucet',
    'https://flop.finance/testnet',
    'https://flop.finance/app',
    'https://flop.finance/inference',
    'https://flop.finance/wallet',
    'https://flop.finance/agents',
    'https://technocore.chat/openapi.json',
    'https://technocore.chat/config',
]


def fetch(url: str, retries: int = 4, timeout: int = 20) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/plain, text/html, application/json'})
    last = (599, 'uninitialized')
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read().decode('utf-8', 'ignore')
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', 'ignore')
            last = (e.code, body)
            if e.code not in (429, 500, 502, 503, 504) or attempt == retries - 1:
                return last
        except Exception as e:
            last = (599, str(e))
            if attempt == retries - 1:
                return last
        time.sleep(1 + attempt)
    return last


def load_flipflopper() -> dict[str, Any]:
    if not FLIPFLOPPER_CONFIG.exists():
        return {'config_found': False}
    data = json.loads(FLIPFLOPPER_CONFIG.read_text())
    data['config_found'] = True
    return data


def normalize_text(text: str) -> str:
    text = re.sub(r'(?is)<script.*?</script>', ' ', text)
    text = re.sub(r'(?is)<style.*?</style>', ' ', text)
    text = re.sub(r'(?is)<!--.*?-->', ' ', text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def analyze_target(target: dict[str, Any]) -> dict[str, Any]:
    status, body = fetch(target['url'])
    cleaned = normalize_text(body)
    body_l = cleaned.lower()
    hits = [kw for kw in target['keywords'] if kw.lower() in body_l]
    signals = {
        'mentions_testnet': 'testnet' in body_l,
        'mentions_faucet': 'faucet' in body_l,
        'mentions_wallet': 'wallet' in body_l,
        'mentions_inference': 'inference' in body_l,
        'mentions_agent': 'agent' in body_l or 'agents' in body_l,
        'mentions_validator': 'validator' in body_l,
    }
    return {
        'id': target['id'],
        'url': target['url'],
        'status': status,
        'keyword_hits': hits,
        'signals': signals,
        'excerpt': cleaned[:700],
    }


def probe_entrypoints() -> list[dict[str, Any]]:
    out = []
    for url in ENTRYPOINT_PROBES:
        status, body = fetch(url, retries=2, timeout=15)
        cleaned = normalize_text(body)
        out.append({
            'url': url,
            'status': status,
            'looks_live': status == 200 and len(cleaned) > 0,
            'excerpt': cleaned[:220],
        })
    return out


def derive_readiness(config: dict[str, Any], checks: list[dict[str, Any]], entrypoint_probes: list[dict[str, Any]]) -> dict[str, Any]:
    ok = {c['id']: c for c in checks}
    identity_ready = bool(config.get('config_found') and config.get('did') and config.get('mailbox') and config.get('room'))
    docs_ready = all(ok.get(k, {}).get('status') == 200 for k in ['flop_teaser', 'flop_llms', 'technocore_auth', 'technocore_patterns'])
    applications_visible = all(ok.get(k, {}).get('status') == 200 for k in ['apply_miner', 'apply_validator', 'apply_kol'])
    testnet_mentions = sum(1 for c in checks if c['signals'].get('mentions_testnet'))
    inference_mentions = sum(1 for c in checks if c['signals'].get('mentions_inference'))
    live_probe_hits = [p for p in entrypoint_probes if p['looks_live']]
    explicit_live_surface = any(p['url'].startswith('https://flop.finance/') for p in live_probe_hits)

    missing = []
    if not identity_ready:
        missing.append('flipflopper_identity_config')
    if not docs_ready:
        missing.append('core_docs_availability')
    if testnet_mentions == 0:
        missing.append('official_testnet_wording')
    if not explicit_live_surface:
        missing.append('explicit_live_testnet_entrypoint')
    if inference_mentions == 0:
        missing.append('explicit_inference_entrypoint')

    readiness_score = 0
    readiness_score += 30 if identity_ready else 0
    readiness_score += 20 if docs_ready else 0
    readiness_score += 10 if applications_visible else 0
    readiness_score += min(15, testnet_mentions * 3)
    readiness_score += min(10, inference_mentions * 3)
    readiness_score += 15 if explicit_live_surface else 0

    if not explicit_live_surface:
        readiness_score = min(readiness_score, 70)

    activation_candidates = []
    for c in checks:
        strong = c['id'] in ('flop_teaser', 'flop_llms') and c['signals']['mentions_testnet']
        if c['status'] == 200 and strong:
            activation_candidates.append({'id': c['id'], 'url': c['url'], 'signals': c['signals']})
    for p in live_probe_hits:
        activation_candidates.append({'id': 'entrypoint_probe', 'url': p['url'], 'signals': {'live_probe': True}})

    phase = 'pre-testnet-observability-ready'
    if explicit_live_surface:
        phase = 'activation-surface-detected'

    return {
        'phase': phase,
        'identity_ready': identity_ready,
        'docs_ready': docs_ready,
        'applications_visible': applications_visible,
        'explicit_live_surface': explicit_live_surface,
        'live_probe_hits_count': len(live_probe_hits),
        'readiness_score': readiness_score,
        'testnet_mentions_count': testnet_mentions,
        'inference_mentions_count': inference_mentions,
        'missing_gates': missing,
        'activation_candidates': activation_candidates,
        'recommended_next_actions': [
            'keep DID, mailbox and owned room stable',
            'watch for faucet / wallet / inference entrypoints',
            'capture evidence immediately when a live testnet surface appears',
            'avoid claiming eligibility rules not stated by official sources',
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = []
    lines.append('# FlipFlopper Testnet Readiness Report')
    lines.append('')
    lines.append(f"Generated: {report['generated_at']}")
    lines.append('')
    r = report['readiness']
    lines.append('## Summary')
    lines.append(f"- phase: **{r['phase']}**")
    lines.append(f"- readiness_score: **{r['readiness_score']}/100**")
    lines.append(f"- identity_ready: **{r['identity_ready']}**")
    lines.append(f"- docs_ready: **{r['docs_ready']}**")
    lines.append(f"- applications_visible: **{r['applications_visible']}**")
    lines.append(f"- explicit_live_surface: **{r['explicit_live_surface']}**")
    lines.append(f"- live_probe_hits_count: **{r['live_probe_hits_count']}**")
    lines.append(f"- testnet_mentions_count: **{r['testnet_mentions_count']}**")
    lines.append(f"- inference_mentions_count: **{r['inference_mentions_count']}**")
    lines.append('')
    lines.append('## Missing gates')
    if r['missing_gates']:
        for item in r['missing_gates']:
            lines.append(f'- {item}')
    else:
        lines.append('- none')
    lines.append('')
    lines.append('## Activation candidates')
    if r['activation_candidates']:
        for item in r['activation_candidates']:
            lines.append(f"- `{item['id']}` → {item['url']}")
    else:
        lines.append('- none yet')
    lines.append('')
    lines.append('## Entrypoint probes')
    for p in report['entrypoint_probes']:
        lines.append(f"- `{p['status']}` {p['url']} | live={p['looks_live']}")
    lines.append('')
    lines.append('## Surface checks')
    for c in report['checks']:
        lines.append(f"### {c['id']}")
        lines.append(f"- status: `{c['status']}`")
        lines.append(f"- url: {c['url']}")
        lines.append(f"- keyword_hits: {', '.join(c['keyword_hits']) if c['keyword_hits'] else 'none'}")
        lines.append(f"- excerpt: {c['excerpt'][:280]}")
        lines.append('')
    lines.append('## Recommended next actions')
    for item in r['recommended_next_actions']:
        lines.append(f'- {item}')
    lines.append('')
    return '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser(description='FlipFlopper testnet readiness harness')
    ap.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    ap.add_argument('--pretty', action='store_true')
    ap.add_argument('--write-report', action='store_true')
    args = ap.parse_args()

    checks = [analyze_target(t) for t in TARGETS]
    entrypoint_probes = probe_entrypoints()
    cfg = load_flipflopper()
    report = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'flipflopper': {
            'config_found': cfg.get('config_found', False),
            'alias': cfg.get('alias'),
            'did': cfg.get('did'),
            'room': cfg.get('room'),
            'mailbox': cfg.get('mailbox'),
        },
        'checks': checks,
        'entrypoint_probes': entrypoint_probes,
        'readiness': derive_readiness(cfg, checks, entrypoint_probes),
    }

    if args.write_report:
        outdir = pathlib.Path(args.output_dir)
        outdir.mkdir(parents=True, exist_ok=True)
        stem = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        json_path = outdir / f'{stem}_readiness.json'
        md_path = outdir / f'{stem}_readiness.md'
        json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
        md_path.write_text(render_markdown(report))
        report['artifacts'] = {'json': str(json_path), 'markdown': str(md_path)}

    json.dump(report, sys.stdout, indent=2 if args.pretty else None, ensure_ascii=False)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
