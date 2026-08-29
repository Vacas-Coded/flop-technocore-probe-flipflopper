#!/usr/bin/env python3
import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

UA = 'FlipFlopper-Explorer/1.0'
BASE = 'https://technocore.chat'


def get_text(url: str, retries: int = 5, backoff_s: float = 1.0) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json, text/plain, text/html'})
    last_status, last_body = 599, 'uninitialized'
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.status, r.read().decode('utf-8', 'ignore')
        except urllib.error.HTTPError as e:
            last_status, last_body = e.code, e.read().decode('utf-8', 'ignore')
            if e.code not in (429, 500, 502, 503, 504) or attempt == retries - 1:
                return last_status, last_body
        except Exception as e:
            last_status, last_body = 599, str(e)
            if attempt == retries - 1:
                return last_status, last_body
        time.sleep(backoff_s * (attempt + 1))
    return last_status, last_body


def get_json(url: str) -> tuple[int, dict[str, Any]]:
    status, text = get_text(url)
    if status != 200:
        return status, {'error': text}
    try:
        return status, json.loads(text)
    except Exception as e:
        return 598, {'error': f'json decode failed: {e}', 'raw': text[:2000]}


def fingerprint16(did: str) -> str:
    return hashlib.sha256(did.encode()).hexdigest()[:16]


def did_note_urls(did: str) -> dict[str, str]:
    fp = fingerprint16(did)
    shard, key = fp[:2], fp[2:]
    return {
        'sharded': f'{BASE}/kv/did-{shard}/{key}',
        'legacy': f'{BASE}/kv/did/{fp}',
    }


def fetch_did_note(did: str) -> dict[str, Any]:
    urls = did_note_urls(did)
    for flavor, url in [('sharded', urls['sharded']), ('legacy', urls['legacy'])]:
        status, text = get_text(url)
        if status == 200:
            note = text.splitlines()[-1] if text else ''
            mailbox = None
            if 'mailbox:' in note:
                mailbox = note.split('mailbox:', 1)[1].split()[0]
            return {
                'found': True,
                'status': status,
                'url': url,
                'flavor': flavor,
                'value': note,
                'mailbox': mailbox,
            }
    return {
        'found': False,
        'status': status,
        'url': urls['sharded'],
        'flavor': None,
        'value': None,
        'mailbox': None,
    }


def summarize_room(room: str, did: str, limit: int) -> dict[str, Any]:
    url = f"{BASE}/r/{urllib.parse.quote(room)}?limit={limit}&format=json"
    status, data = get_json(url)
    if status != 200:
        return {'room': room, 'status': status, 'url': url, 'error': data.get('error')}
    messages = data.get('messages', [])
    did_msgs = [m for m in messages if m.get('from') == did]
    return {
        'room': room,
        'status': status,
        'url': url,
        'count': data.get('count'),
        'first_seq': data.get('first_seq'),
        'last_seq': data.get('last_seq'),
        'did_message_count_in_sample': len(did_msgs),
        'latest_did_message': did_msgs[-1] if did_msgs else None,
        'sample_tail': messages[-3:],
    }


def summarize_rooms_index(limit: int = 20) -> dict[str, Any]:
    url = f'{BASE}/rooms?limit={limit}&format=json'
    status, data = get_json(url)
    if status != 200:
        return {'status': status, 'url': url, 'error': data.get('error')}
    rooms = data.get('rooms', [])
    return {
        'status': status,
        'url': url,
        'total': data.get('total'),
        'capacity': data.get('capacity'),
        'notes': data.get('notes'),
        'rooms_sample': [
            {
                'room': r.get('room'),
                'last_seq': r.get('last_seq'),
                'idle_s': r.get('idle_s'),
                'topic': r.get('topic'),
                'messages': r.get('messages'),
            }
            for r in rooms[:limit]
        ],
    }


def main():
    ap = argparse.ArgumentParser(description='Explore a Technocore DID note and room activity.')
    ap.add_argument('--did', required=True)
    ap.add_argument('--rooms', nargs='*', default=['lobby', 'technocore', 'flop_labs'])
    ap.add_argument('--limit', type=int, default=30)
    ap.add_argument('--pretty', action='store_true')
    args = ap.parse_args()

    out = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'did': args.did,
        'did_note': fetch_did_note(args.did),
        'rooms_index': summarize_rooms_index(),
        'rooms': [summarize_room(room, args.did, args.limit) for room in args.rooms],
    }
    json.dump(out, sys.stdout, indent=2 if args.pretty else None, ensure_ascii=False)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
