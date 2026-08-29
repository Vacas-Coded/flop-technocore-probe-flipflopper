#!/usr/bin/env python3
import argparse
import copy
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
EVENT_COOLDOWNS = {
    'docs_change': 240,
    'repo_metadata_change': 180,
    'commit_change': 150,
    'release_change': 120,
    'harness_change': 240,
    'live_surface_activation': 45,
    'digest_change': 90,
    'digest_activation': 60,
}
SOURCE_EVENT_TYPES = {
    'technocore_auth': 'docs_change',
    'technocore_patterns': 'docs_change',
    'technocore_llms': 'docs_change',
    'flop_home': 'docs_change',
    'flop_teaser': 'docs_change',
    'flop_llms': 'docs_change',
    'technocore_repo': 'repo_metadata_change',
    'technocore_commits': 'commit_change',
    'technocore_releases': 'release_change',
    'harness_readiness': 'harness_change',
    'watcher_digest': 'digest_change',
    'watcher_activation_digest': 'digest_activation',
}


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
    date_utc = metadata('date_utc')
    rel = path.relative_to(REPO).as_posix() if path.is_relative_to(REPO) else path.name
    github_url = GITHUB_BASE + quote(rel)
    return {'title': title, 'summary': summary, 'why': why, 'verified': verified, 'source_id': source_id, 'date_utc': date_utc, 'github_url': github_url, 'rel': rel}


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
    return ' '.join(x for x in bits if x).strip()[:3900]


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=180)


def default_state() -> dict:
    return {
        'posts': [],
        'by_update': {},
        'by_message_hash': {},
        'last_success_by_room': {},
        'last_success_by_room_and_event': {},
        'last_attempt_by_update': {},
        'last_attempt_by_message_hash': {},
        'pending_publications': {},
    }


def enrich_pending_item(item: dict) -> dict:
    item = dict(item or {})
    update_path = pathlib.Path(item.get('update_path') or '')
    if update_path.exists():
        try:
            update = parse_update(update_path)
        except Exception:
            update = {}
    else:
        update = {}
    room = item.get('room') or DEFAULT_ROOM
    event_type = item.get('event_type') or 'docs_change'
    item.setdefault('title', update.get('title'))
    item.setdefault('source_id', update.get('source_id'))
    item.setdefault('update_date_utc', update.get('date_utc'))
    item.setdefault('supersession_key', pending_supersession_key(room, event_type, item.get('source_id') or update.get('source_id')))
    return item


def canonicalize_pending_publications(state: dict) -> dict:
    pending = state.setdefault('pending_publications', {})
    canonical = {}
    for raw_key, raw_item in list(pending.items()):
        item = enrich_pending_item(raw_item)
        key = pending_key(item.get('room') or DEFAULT_ROOM, item.get('update_path') or raw_key)
        supersession_key = item.get('supersession_key')
        if supersession_key:
            existing_key = next((k for k, v in canonical.items() if v.get('supersession_key') == supersession_key), None)
            if existing_key is not None:
                if should_replace_pending(canonical[existing_key], item):
                    canonical.pop(existing_key, None)
                else:
                    continue
        canonical[key] = item
    state['pending_publications'] = canonical
    return state


def normalize_state(state: dict | None) -> dict:
    base = default_state()
    state = state or {}
    for key, value in base.items():
        state.setdefault(key, value if not isinstance(value, dict) else dict(value))
    return canonicalize_pending_publications(state)


def load_state() -> dict:
    if STATE_PATH.exists():
        raw = json.loads(STATE_PATH.read_text())
        normalized = normalize_state(copy.deepcopy(raw))
        if normalized != raw:
            save_state(normalized)
        return normalized
    return default_state()


def save_state(state: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(normalize_state(state), indent=2, ensure_ascii=False) + '\n')


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stamp_now() -> str:
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def parse_iso(ts: str | None):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace('Z', '+00:00'))
    except Exception:
        return None


def message_hash(room: str, message: str) -> str:
    return hashlib.sha256(f'{room}\n{message}'.encode()).hexdigest()


def derive_event_type(source_id: str, explicit_event_type: str | None = None) -> str:
    if explicit_event_type:
        return explicit_event_type
    return SOURCE_EVENT_TYPES.get(source_id, 'docs_change')


def resolve_cooldown_minutes(event_type: str, score: dict, requested_minutes: int | None = None) -> dict:
    base = EVENT_COOLDOWNS.get(event_type, DEFAULT_COOLDOWN_MINUTES)
    if requested_minutes is not None:
        base = requested_minutes
    total = score.get('total_score', 0)
    leverage = ((score.get('components') or {}).get('airdrop_leverage') or 0)
    adjustment = 0
    reasons = []
    if total >= 90:
        adjustment -= 30
        reasons.append('score>=90 => -30m')
    elif total >= 85:
        adjustment -= 15
        reasons.append('score>=85 => -15m')
    if leverage >= 13:
        adjustment -= 15
        reasons.append('airdrop_leverage>=13 => -15m')
    elif leverage >= 10:
        adjustment -= 10
        reasons.append('airdrop_leverage>=10 => -10m')
    if event_type in {'docs_change', 'harness_change'} and total < 90:
        adjustment += 30
        reasons.append('docs/harness non-exceptional => +30m')
    resolved = max(30, base + adjustment)
    return {
        'event_type': event_type,
        'base_cooldown_minutes': base,
        'adjustment_minutes': adjustment,
        'resolved_cooldown_minutes': resolved,
        'reasons': reasons,
    }


def evaluate_publish_guardrails(state: dict, room: str, event_type: str, update_path: pathlib.Path, message: str, cooldown_minutes: int) -> dict:
    now = datetime.now(timezone.utc)
    rel_update = str(update_path)
    mhash = message_hash(room, message)
    last_room_ts = parse_iso((state.get('last_success_by_room') or {}).get(room))
    last_room_event_ts = parse_iso((state.get('last_success_by_room_and_event') or {}).get(f'{room}::{event_type}'))
    blockers = []
    details = {'message_hash': mhash, 'room': room, 'event_type': event_type, 'cooldown_minutes': cooldown_minutes}

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

    if last_room_event_ts:
        event_cooldown = max(15, min(cooldown_minutes, EVENT_COOLDOWNS.get(event_type, cooldown_minutes)))
        event_allowed_at = last_room_event_ts + timedelta(minutes=event_cooldown)
        details['last_success_at_same_event'] = last_room_event_ts.isoformat()
        details['same_event_cooldown_minutes'] = event_cooldown
        details['same_event_allows_at'] = event_allowed_at.isoformat()
        if now < event_allowed_at:
            blockers.append('same_event_cooldown_active')
            details['same_event_remaining_minutes'] = round((event_allowed_at - now).total_seconds() / 60, 2)

    return {'allowed': not blockers, 'blockers': blockers, 'details': details}


def record_attempt(state: dict, room: str, event_type: str, update_path: pathlib.Path, msg_hash: str, status: str, extra: dict | None = None):
    ts = iso_now()
    record = {
        'at': ts,
        'room': room,
        'event_type': event_type,
        'update_path': str(update_path),
        'message_hash': msg_hash,
        'status': status,
    }
    if extra:
        record.update(extra)
    state.setdefault('posts', []).append(record)
    state['posts'] = state['posts'][-400:]

    state.setdefault('last_attempt_by_update', {})[str(update_path)] = record
    state.setdefault('last_attempt_by_message_hash', {})[msg_hash] = record

    existing_update = (state.setdefault('by_update', {})).get(str(update_path))
    if status == 'success' or not existing_update:
        state['by_update'][str(update_path)] = {
            'status': status,
            'at': ts,
            'room': room,
            'event_type': event_type,
            'message_hash': msg_hash,
            **(extra or {}),
        }

    existing_message = (state.setdefault('by_message_hash', {})).get(msg_hash)
    if status == 'success' or not existing_message:
        state['by_message_hash'][msg_hash] = {
            'status': status,
            'at': ts,
            'room': room,
            'event_type': event_type,
            'update_path': str(update_path),
            **(extra or {}),
        }

    if status == 'success':
        state.setdefault('last_success_by_room', {})[room] = ts
        state.setdefault('last_success_by_room_and_event', {})[f'{room}::{event_type}'] = ts
    save_state(state)


def make_log_path(update_path: pathlib.Path, room: str) -> pathlib.Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return LOG_DIR / f'{stamp_now()}_{update_path.stem}_{room}.json'


def pending_key(room: str, update_path: pathlib.Path | str) -> str:
    return f'{room}::{update_path}'


def pending_supersession_key(room: str, event_type: str, source_id: str | None) -> str | None:
    source_id = (source_id or '').strip()
    if not source_id:
        return None
    return f'{room}::{event_type}::{source_id}'


def pending_sort_timestamp(item: dict) -> datetime:
    return (
        parse_iso(item.get('update_date_utc'))
        or parse_iso(item.get('queued_at'))
        or parse_iso(item.get('updated_at'))
        or datetime.fromtimestamp(0, tz=timezone.utc)
    )


def should_replace_pending(existing: dict, candidate: dict) -> bool:
    existing_ts = pending_sort_timestamp(existing)
    candidate_ts = pending_sort_timestamp(candidate)
    if candidate_ts != existing_ts:
        return candidate_ts > existing_ts
    existing_score = existing.get('score') or 0
    candidate_score = candidate.get('score') or 0
    if candidate_score != existing_score:
        return candidate_score > existing_score
    existing_leverage = existing.get('airdrop_leverage') or 0
    candidate_leverage = candidate.get('airdrop_leverage') or 0
    if candidate_leverage != existing_leverage:
        return candidate_leverage >= existing_leverage
    return (candidate.get('update_path') or '') >= (existing.get('update_path') or '')


def remove_superseded_pending_publications(state: dict, candidate: dict):
    supersession_key = candidate.get('supersession_key')
    if not supersession_key:
        return
    pending = state.setdefault('pending_publications', {})
    for key, existing in list(pending.items()):
        if existing.get('supersession_key') != supersession_key:
            continue
        if should_replace_pending(existing, candidate):
            pending.pop(key, None)


def resolve_pending_eligible_at(details: dict) -> str | None:
    candidates = [parse_iso(details.get('cooldown_allows_at')), parse_iso(details.get('same_event_allows_at'))]
    candidates = [c for c in candidates if c]
    if not candidates:
        return None
    return max(candidates).isoformat()


def is_retryable_cooldown_block(blockers: list[str]) -> bool:
    if not blockers:
        return False
    allowed = {'room_cooldown_active', 'same_event_cooldown_active'}
    return set(blockers).issubset(allowed)


def upsert_pending_publication(state: dict, room: str, event_type: str, update_path: pathlib.Path, score: dict, guardrails: dict, log_path: pathlib.Path):
    blockers = guardrails.get('blockers') or []
    if not is_retryable_cooldown_block(blockers):
        return None
    details = guardrails.get('details') or {}
    now = iso_now()
    key = pending_key(room, update_path)
    pending = state.setdefault('pending_publications', {})
    existing = pending.get(key) or {}
    update = parse_update(update_path)
    supersession_key = pending_supersession_key(room, event_type, update.get('source_id'))
    record = {
        'room': room,
        'event_type': event_type,
        'update_path': str(update_path),
        'queued_at': existing.get('queued_at') or now,
        'updated_at': now,
        'title': update.get('title'),
        'source_id': update.get('source_id'),
        'update_date_utc': update.get('date_utc'),
        'supersession_key': supersession_key,
        'eligible_at': resolve_pending_eligible_at(details),
        'score': score.get('total_score'),
        'airdrop_leverage': ((score.get('components') or {}).get('airdrop_leverage') or 0),
        'recommendation': score.get('recommendation'),
        'blockers': blockers,
        'reason': ','.join(blockers),
        'cooldown_policy': {
            'cooldown_minutes': details.get('cooldown_minutes'),
            'same_event_cooldown_minutes': details.get('same_event_cooldown_minutes'),
        },
        'log_path': str(log_path),
    }
    if supersession_key:
        for existing_key, existing_item in list(pending.items()):
            if existing_key == key:
                continue
            if existing_item.get('supersession_key') != supersession_key:
                continue
            if not should_replace_pending(existing_item, record):
                return existing_item
        remove_superseded_pending_publications(state, record)
    pending[key] = record
    save_state(state)
    return record


def remove_pending_publication(state: dict, room: str, update_path: pathlib.Path):
    pending = state.setdefault('pending_publications', {})
    key = pending_key(room, update_path)
    removed = pending.pop(key, None)
    supersession_key = (removed or {}).get('supersession_key')
    if supersession_key:
        for other_key, other_item in list(pending.items()):
            if other_item.get('supersession_key') == supersession_key:
                pending.pop(other_key, None)


def select_pending_publication(state: dict, room: str | None = None, now: datetime | None = None) -> dict | None:
    now = now or datetime.now(timezone.utc)
    pending = list((state.get('pending_publications') or {}).values())
    if room:
        pending = [item for item in pending if item.get('room') == room]
    eligible = []
    for item in pending:
        eligible_at = parse_iso(item.get('eligible_at'))
        if eligible_at and eligible_at > now:
            continue
        eligible.append(item)
    if not eligible:
        return None
    eligible.sort(
        key=lambda item: (
            parse_iso(item.get('eligible_at')) or datetime.fromtimestamp(0, tz=timezone.utc),
            -(item.get('score') or 0),
            -(item.get('airdrop_leverage') or 0),
            item.get('queued_at') or '',
        )
    )
    return eligible[0]


def publish_once(update_path: pathlib.Path, room: str, event_type: str, skip_github_push: bool, force: bool, cooldown_minutes: int | None = None) -> pathlib.Path:
    data = parse_update(update_path)
    s = run(['python', str(SCORE), str(update_path)])
    if s.returncode != 0:
        print(s.stdout)
        print(s.stderr, file=sys.stderr)
        raise SystemExit(s.returncode)
    score = json.loads(s.stdout)
    cooldown = resolve_cooldown_minutes(event_type, score, cooldown_minutes)
    post = build_post(data, score)
    state = load_state()
    guardrails = evaluate_publish_guardrails(state, room, event_type, update_path, post, cooldown['resolved_cooldown_minutes'])
    results = {
        'attempt_at': iso_now(),
        'update_path': str(update_path),
        'room': room,
        'event_type': event_type,
        'cooldown_policy': cooldown,
        'score': score,
        'guardrails': guardrails,
        'github_pushed': None,
        'technocore_posted': None,
        'message': post,
        'pending_publication': None,
    }
    msg_hash = guardrails['details']['message_hash']

    if score.get('recommendation') != 'autopublish' and not force:
        log = make_log_path(update_path, room)
        results['technocore_posted'] = {'skipped': True, 'reason': f"recommendation={score.get('recommendation')} score={score.get('total_score')}"}
        log.write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n')
        remove_pending_publication(state, room, update_path)
        record_attempt(state, room, event_type, update_path, msg_hash, 'skipped_score', {'reason': results['technocore_posted']['reason'], 'log_path': str(log)})
        print(str(log))
        return log

    if not guardrails['allowed'] and not force:
        log = make_log_path(update_path, room)
        results['technocore_posted'] = {'skipped': True, 'reason': ','.join(guardrails['blockers'])}
        log.write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n')
        pending = upsert_pending_publication(state, room, event_type, update_path, score, guardrails, log)
        if pending:
            results['pending_publication'] = pending
            log.write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n')
        record_attempt(state, room, event_type, update_path, msg_hash, 'skipped_guardrails', {'reason': results['technocore_posted']['reason'], 'log_path': str(log)})
        print(str(log))
        return log

    if not skip_github_push:
        p = run(['python', str(PUSH)])
        results['github_pushed'] = {'returncode': p.returncode, 'stdout': p.stdout.strip(), 'stderr': p.stderr.strip()}
        if p.returncode != 0 and 'nothing_to_push' not in p.stdout:
            record_attempt(state, room, event_type, update_path, msg_hash, 'failed_github_push', {'stdout': p.stdout.strip(), 'stderr': p.stderr.strip()})
            print(p.stdout)
            print(p.stderr, file=sys.stderr)
            raise SystemExit(p.returncode)

    t = run(['python', str(AGENT), 'checkin', '--room', room, '--message', post])
    results['technocore_posted'] = {'returncode': t.returncode, 'stdout': t.stdout.strip(), 'stderr': t.stderr.strip()}
    if t.returncode != 0:
        record_attempt(state, room, event_type, update_path, msg_hash, 'failed_agent_command', {'stdout': t.stdout.strip(), 'stderr': t.stderr.strip()})
        print(t.stdout)
        print(t.stderr, file=sys.stderr)
        raise SystemExit(t.returncode)
    try:
        tech = json.loads(t.stdout)
    except json.JSONDecodeError:
        record_attempt(state, room, event_type, update_path, msg_hash, 'failed_invalid_json', {'stdout': t.stdout.strip()[:2000]})
        print(t.stdout)
        print('invalid technocore publish response json', file=sys.stderr)
        raise SystemExit(3)

    post_status = ((tech.get('post') or {}).get('response') or [None])[0]
    verify_status = ((tech.get('verify') or {}).get('response') or [None])[0]
    results['technocore_posted']['post_status'] = post_status
    results['technocore_posted']['verify_status'] = verify_status
    log = make_log_path(update_path, room)
    if post_status != 200 or verify_status != 200:
        log.write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n')
        record_attempt(state, room, event_type, update_path, msg_hash, 'failed_technocore_confirmation', {'post_status': post_status, 'verify_status': verify_status, 'log_path': str(log)})
        print(t.stdout)
        print(f'technocore publish not confirmed: post_status={post_status} verify_status={verify_status}', file=sys.stderr)
        raise SystemExit(4)

    remove_pending_publication(state, room, update_path)
    log.write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n')
    record_attempt(state, room, event_type, update_path, msg_hash, 'success', {'post_status': post_status, 'verify_status': verify_status, 'log_path': str(log)})
    print(str(log))
    return log


def retry_pending_publication(room: str, skip_github_push: bool, force: bool, dry_run: bool = False) -> pathlib.Path | None:
    state = load_state()
    item = select_pending_publication(state, room=room)
    if not item:
        print('no_retryable_pending_publications')
        return None
    if dry_run:
        print(json.dumps({'action': 'retry_pending_dry_run', 'selected_pending_publication': item}, indent=2, ensure_ascii=False))
        return None
    update_path = pathlib.Path(item['update_path'])
    event_type = item.get('event_type') or 'docs_change'
    return publish_once(update_path, room, event_type, skip_github_push=skip_github_push, force=force)


def main():
    ap = argparse.ArgumentParser(description='Push repo docs and publish a Technocore post for a verified update')
    ap.add_argument('update_path', nargs='?')
    ap.add_argument('--room', default=DEFAULT_ROOM)
    ap.add_argument('--skip-github-push', action='store_true')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--cooldown-minutes', type=int)
    ap.add_argument('--event-type', default='')
    ap.add_argument('--retry-pending', action='store_true', help='Retry the next queued publication whose cooldown has expired')
    ap.add_argument('--dry-run', action='store_true', help='Preview retry-pending selection without pushing or posting')
    args = ap.parse_args()

    if args.retry_pending:
        retry_pending_publication(args.room, skip_github_push=args.skip_github_push, force=args.force, dry_run=args.dry_run)
        return

    if not args.update_path:
        print('missing update path', file=sys.stderr)
        raise SystemExit(2)

    update_path = pathlib.Path(args.update_path)
    if not update_path.exists():
        print(f'missing update path: {update_path}', file=sys.stderr)
        raise SystemExit(2)

    source_id = parse_update(update_path).get('source_id') or ''
    event_type = derive_event_type(source_id, args.event_type or None)
    publish_once(update_path, args.room, event_type, skip_github_push=args.skip_github_push, force=args.force, cooldown_minutes=args.cooldown_minutes)


if __name__ == '__main__':
    main()
