#!/usr/bin/env python3
import argparse
import json
import pathlib
import re
import subprocess
import sys
from urllib.parse import quote

REPO = pathlib.Path('/root/.hermes/document_cache/flop-technocore-probe-flipflopper')
PUSH = REPO / 'tools' / 'change-capture' / 'push_repo_updates.py'
SCORE = REPO / 'tools' / 'change-capture' / 'score_publication.py'
AGENT = pathlib.Path('/root/.hermes/scripts/flipflopper_agent.py')
LOG_DIR = pathlib.Path('/root/.hermes/document_cache/flop_publish_logs')
GITHUB_BASE = 'https://github.com/Vacas-Coded/flop-technocore-probe-flipflopper/blob/main/'


def parse_update(path: pathlib.Path):
    text = path.read_text()
    title = text.splitlines()[0].lstrip('#').strip() if text.splitlines() else path.stem
    def section(name: str):
        m = re.search(rf'^## {re.escape(name)}\n(.*?)(?=^## |\Z)', text, re.M | re.S)
        return (m.group(1).strip() if m else '')
    summary = section('Summary').splitlines()[0].strip() if section('Summary') else ''
    why = section('Why it matters').splitlines()[0].strip() if section('Why it matters') else ''
    verified = [re.sub(r'^-\s*', '', x).strip() for x in section('Verified').splitlines() if x.strip()]
    rel = path.relative_to(REPO).as_posix() if path.is_relative_to(REPO) else path.name
    github_url = GITHUB_BASE + quote(rel)
    return {'title': title, 'summary': summary, 'why': why, 'verified': verified, 'github_url': github_url, 'rel': rel}


def build_post(data: dict) -> str:
    bits = [
        f"FlipFlopper update: {data['title']}",
        data['summary'],
        f"Why it matters: {data['why']}" if data['why'] else '',
        f"Verified: {data['verified'][0]}" if data['verified'] else '',
        f"Repo note: {data['github_url']}",
    ]
    msg = ' '.join(x for x in bits if x).strip()
    return msg[:3900]


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=180)


def main():
    ap = argparse.ArgumentParser(description='Push repo docs and publish a Technocore post for a verified update')
    ap.add_argument('update_path')
    ap.add_argument('--room', default='technocore')
    ap.add_argument('--skip-github-push', action='store_true')
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args()

    update_path = pathlib.Path(args.update_path)
    if not update_path.exists():
        print(f'missing update path: {update_path}', file=sys.stderr)
        raise SystemExit(2)

    data = parse_update(update_path)
    s = run(['python', str(SCORE), str(update_path)])
    if s.returncode != 0:
        print(s.stdout)
        print(s.stderr, file=sys.stderr)
        raise SystemExit(s.returncode)
    score = json.loads(s.stdout)
    post = build_post(data)
    results = {'update_path': str(update_path), 'room': args.room, 'score': score, 'github_pushed': None, 'technocore_posted': None, 'message': post}

    if score.get('recommendation') != 'autopublish' and not args.force:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        stem = update_path.stem
        log = LOG_DIR / f'{stem}_{args.room}.json'
        results['technocore_posted'] = {'skipped': True, 'reason': f"recommendation={score.get('recommendation')} score={score.get('total_score')}"}
        log.write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n')
        print(str(log))
        return

    if not args.skip_github_push:
        p = run(['python', str(PUSH)])
        results['github_pushed'] = {'returncode': p.returncode, 'stdout': p.stdout.strip(), 'stderr': p.stderr.strip()}
        if p.returncode != 0 and 'nothing_to_push' not in p.stdout:
            print(p.stdout)
            print(p.stderr, file=sys.stderr)
            raise SystemExit(p.returncode)

    t = run(['python', str(AGENT), 'checkin', '--room', args.room, '--message', post])
    results['technocore_posted'] = {'returncode': t.returncode, 'stdout': t.stdout.strip(), 'stderr': t.stderr.strip()}
    if t.returncode != 0:
        print(t.stdout)
        print(t.stderr, file=sys.stderr)
        raise SystemExit(t.returncode)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stem = update_path.stem
    log = LOG_DIR / f'{stem}_{args.room}.json'
    log.write_text(__import__('json').dumps(results, indent=2, ensure_ascii=False) + '\n')
    print(str(log))


if __name__ == '__main__':
    main()
