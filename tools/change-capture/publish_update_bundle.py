#!/usr/bin/env python3
import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

REPO = pathlib.Path('/root/.hermes/document_cache/flop-technocore-probe-flipflopper')
PUSH = REPO / 'tools' / 'change-capture' / 'push_repo_updates.py'
SCORE = REPO / 'tools' / 'change-capture' / 'score_publication.py'
AGENT = pathlib.Path('/root/.hermes/scripts/flipflopper_agent.py')
LOG_DIR = pathlib.Path('/root/.hermes/document_cache/flop_publish_logs')
STATE_PATH = pathlib.Path('/root/.hermes/flipflopper/publish_state.json')
GITHUB_BASE = 'https://github.com/Vacas-Coded/flop-technocore-probe-flipflopper/blob/main/'
DEFAULT_ROOM = 'technocore'
DEFAULT_COOLDOWN_MINUTES = 180


def parse_update(path: pathlib.Path):
    text = path.read_text()
    title = text.splitlines()[0].lstrip('#').strip() if text.splitlines() else path.stem

    def section(name: str):
        m = re.search(rf'^## {re.escape(name)}\n(.*?)(?=^## |\Z)', text, re.M | re.S)
        return (m.group(1).strip() if m else '')

    def metadata(key: str):
        m = re.search(rf'^-\s*{re.escape(key)}:\s*(.+)$', text, re.M)
        return m.group(1).strip() if m else ''

    summary = section('Summary').splitlines()[0].strip() if section('Summary') else ''
    why = section('Why it matters').splitlines()[0].strip() if section('Why it matters') else ''
    verified = [re.sub(r'^-\s*', '', x).strip() for x in section('Verified').splitlines() if x.strip()]
    source_id = metadata('source_id')
    rel = path.relative_to(REPO).as_posix() if path.is_relative_to(REPO) else path.name
    github_url = GITHUB_BASE + quote(rel)
    return {'title': title, 'summary': summary, 'why': why, 'verified': verified, 'github_url': github_url, 'rel': rel, 'source_id': source_id}


def build_post(data: dict, score: dict | None = None) -> str:
    leverage = None
    if score:
        leverage = ((score.get('components') or {}).get('airdrop_leverage'))
    bits = [
        f"FlipFlopper update: {data['title']}",
        data['summary'],
        f"Why it matters: {data['why']}" if data['why'] else '',
        f"Verified: {data['verified'][0]}" if data['verified'] else '',
        f"Airdrop leverage: {leverage}/15" if leverage is not None and leverage >= 10 else '',
        f"Repo note: {data['github_url']}",
    ]
    msg = ' '.join(x for x in bits if x).strip()
    return msg[:3900]


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=180)


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {'posts': [], 'by_update': {}, 'by_message_hash': {}, 'last_success_by_room': {}}


def save_state(state: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + '\n')


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_iso(ts: str | None):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace('Z', '+00:00'))
    except Exception:
        return None


def message_hash(room: str, message: str) -> str:
    return hashlib.sha256(f'{room}\n{message}'.encode()).hexdigest()


def evaluate_publish_guardrails(state: dict, room: str, update_path: pathlib.Path, message: str, cooldown_minutes: int) -> dict:
    now = datetime.now(timezone.utc)
    rel_update = str(update_path)
    mhash = message_hash(room, message)
    last_room_ts = parse_iso((state.get('last_success_by_room') or {}).get(room))
    blockers = []
    details = {'message_hash': mhash, 'room': room, 'cooldown_minutes': cooldown_minutes}

    prior_update = (state.get('by_update') or {}).get(rel_update)
    if prior_update and prior_update.get('status') == 'success':
        blockers.append('duplicate_update_already_published')
        details['prior_update'] = prior_update

    prior_msg = (state.get('by_message_hash') or {}).get(mhash)
    if prior_msg and prior_msg.get('status') == 'success':
        blockers.append('duplicate_message_hash_already_published')
        details['prior_message'] = prior_msg

    if last_room_ts:
        allowed_at = last_room_ts + timedelta(minutes=cooldown_minutes)
        details['last_success_at'] = last_room_ts.isoformat()
        details['cooldown_allows_at'] = allowed_at.isoformat()
        if now < allowed_at:
            blockers.append('room_cooldown_active')
            details['cooldown_remaining_minutes'] = round((allowed_at - now).total_seconds() / 60, 2)

    return {
        'allowed': not blockers,
        'blockers': blockers,
        'details': details,
    }


def record_attempt(state: dict, room: str, update_path: pathlib.Path, msg_hash: str, status: str, extra: dict | None = None):
    ts = iso_now()
    record = {'at': ts, 'room': room, 'update_path': str(update_path), 'message_hash': msg_hash, 'status': status}
    if extra:
        record.update(extra)
    state.setdefault('posts', []).append(record)
    state['posts'] = state['posts'][-200:]
    state.setdefault('by_update', {})[str(update_path)] = {'status': status, 'at': ts, 'room': room, 'message_hash': msg_hash, **(extra or {})}
    state.setdefault('by_message_hash', {})[msg_hash] = {'status': status, 'at': ts, 'room': room, 'update_path': str(update_path), **(extra or {})}
    if status == 'success':
        state.setdefault('last_success_by_room', {})[room] = ts
    save_state(state)


def main():
    ap = argparse.ArgumentParser(description='Push repo docs and publish a Technocore post for a verified update')
    ap.add_argument('update_path')
    ap.add_argument('--room', default=DEFAULT_ROOM)
    ap.add_argument('--skip-github-push', action='store_true')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--cooldown-minutes', type=int, default=DEFAULT_COOLDOWN_MINUTES)
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
    post = build_post(data, score)
    state = load_state()
    guardrails = evaluate_publish_guardrails(state, args.room, update_path, post, args.cooldown_minutes)
    results = {
        'update_path': str(update_path),
        'room': args.room,
        'score': score,
        'guardrails': guardrails,
        'github_pushed': None,
        'technocore_posted': None,
        'message': post,
    }
    msg_hash = guardrails['details']['message_hash']

    if score.get('recommendation') != 'autopublish' and not args.force:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        stem = update_path.stem
        log = LOG_DIR / f'{stem}_{args.room}.json'
        results['technocore_posted'] = {'skipped': True, 'reason': f"recommendation={score.get('recommendation')} score={score.get('total_score')}"}
        log.write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n')
        record_attempt(state, args.room, update_path, msg_hash, 'skipped_score', {'reason': results['technocore_posted']['reason']})
        print(str(log))
        return

    if not guardrails['allowed'] and not args.force:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        stem = update_path.stem
        log = LOG_DIR / f'{stem}_{args.room}.json'
        results['technocore_posted'] = {'skipped': True, 'reason': ','.join(guardrails['blockers'])}
        log.write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n')
        record_attempt(state, args.room, update_path, msg_hash, 'skipped_guardrails', {'reason': results['technocore_posted']['reason']})
        print(str(log))
        return

    if not args.skip_github_push:
        p = run(['python', str(PUSH)])
        results['github_pushed'] = {'returncode': p.returncode, 'stdout': p.stdout.strip(), 'stderr': p.stderr.strip()}
        if p.returncode != 0 and 'nothing_to_push' not in p.stdout:
            record_attempt(state, args.room, update_path, msg_hash, 'failed_github_push', {'stdout': p.stdout.strip(), 'stderr': p.stderr.strip()})
            print(p.stdout)
            print(p.stderr, file=sys.stderr)
            raise SystemExit(p.returncode)

    t = run(['python', str(AGENT), 'checkin', '--room', args.room, '--message', post])
    results['technocore_posted'] = {'returncode': t.returncode, 'stdout': t.stdout.strip(), 'stderr': t.stderr.strip()}
    if t.returncode != 0:
        record_attempt(state, args.room, update_path, msg_hash, 'failed_agent_command', {'stdout': t.stdout.strip(), 'stderr': t.stderr.strip()})
        print(t.stdout)
        print(t.stderr, file=sys.stderr)
        raise SystemExit(t.returncode)
    try:
        tech = json.loads(t.stdout)
    except json.JSONDecodeError:
        record_attempt(state, args.room, update_path, msg_hash, 'failed_invalid_json', {'stdout': t.stdout.strip()[:2000]})
        print(t.stdout)
        print('invalid technocore publish response json', file=sys.stderr)
        raise SystemExit(3)
    post_status = ((tech.get('post') or {}).get('response') or [None])[0]
    verify_status = ((tech.get('verify') or {}).get('response') or [None])[0]
    if post_status != 200 or verify_status != 200:
        record_attempt(state, args.room, update_path, msg_hash, 'failed_technocore_confirmation', {'post_status': post_status, 'verify_status': verify_status})
        print(t.stdout)
        print(f'technocore publish not confirmed: post_status={post_status} verify_status={verify_status}', file=sys.stderr)
        raise SystemExit(4)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stem = update_path.stem
    log = LOG_DIR / f'{stem}_{args.room}.json'
    log.write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n')
    record_attempt(state, args.room, update_path, msg_hash, 'success', {'post_status': post_status, 'verify_status': verify_status, 'log_path': str(log)})
    print(str(log))


if __name__ == '__main__':
    main()
