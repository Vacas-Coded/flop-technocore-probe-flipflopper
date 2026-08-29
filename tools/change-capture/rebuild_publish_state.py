#!/usr/bin/env python3
import json
import pathlib
from datetime import datetime, timezone

LOG_DIR = pathlib.Path('/root/.hermes/document_cache/flop_publish_logs')
STATE_PATH = pathlib.Path('/root/.hermes/flipflopper/publish_state.json')


def parse_iso_from_path(path: pathlib.Path) -> str:
    stem = path.stem.split('_')[0]
    try:
        dt = datetime.strptime(stem, '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()


def main():
    state = {'posts': [], 'by_update': {}, 'by_message_hash': {}, 'last_success_by_room': {}, 'last_attempt_by_update': {}, 'last_attempt_by_message_hash': {}}
    for path in sorted(LOG_DIR.glob('*.json')):
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        room = data.get('room') or 'technocore'
        update_path = data.get('update_path')
        message = data.get('message', '')
        tech = data.get('technocore_posted') or {}
        score = data.get('score') or {}
        post_status = None
        verify_status = None
        if tech.get('stdout'):
            try:
                raw = json.loads(tech['stdout'])
                post_status = ((raw.get('post') or {}).get('response') or [None])[0]
                verify_status = ((raw.get('verify') or {}).get('response') or [None])[0]
            except Exception:
                pass
        if tech.get('skipped'):
            status = 'skipped'
        elif post_status == 200 and verify_status == 200:
            status = 'success'
        else:
            continue
        at = data.get('attempt_at') or parse_iso_from_path(path)
        import hashlib
        mhash = hashlib.sha256(f'{room}\n{message}'.encode()).hexdigest()
        rec = {
            'at': at,
            'room': room,
            'update_path': update_path,
            'message_hash': mhash,
            'status': status,
            'log_path': str(path),
            'post_status': post_status,
            'verify_status': verify_status,
            'score': score.get('total_score'),
        }
        state['posts'].append(rec)
        state['last_attempt_by_update'][update_path] = rec
        state['last_attempt_by_message_hash'][mhash] = rec
        if update_path:
            prev = state['by_update'].get(update_path)
            if status == 'success' or not prev:
                state['by_update'][update_path] = {k: rec[k] for k in ['status', 'at', 'room', 'message_hash', 'log_path', 'post_status', 'verify_status']}
        prev_msg = state['by_message_hash'].get(mhash)
        if status == 'success' or not prev_msg:
            state['by_message_hash'][mhash] = {k: rec[k] for k in ['status', 'at', 'room', 'update_path', 'log_path', 'post_status', 'verify_status'] if k in rec}
        if status == 'success':
            prev = state['last_success_by_room'].get(room)
            if not prev or at > prev:
                state['last_success_by_room'][room] = at
    state['posts'] = state['posts'][-200:]
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'rebuilt_from': str(LOG_DIR), 'state_path': str(STATE_PATH), 'successes': len([x for x in state['posts'] if x['status']=='success']), 'last_success_by_room': state['last_success_by_room']}, indent=2))


if __name__ == '__main__':
    main()
