#!/usr/bin/env python3
import argparse
import base64
import hashlib
import json
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

INVISIBLE_CATEGORIES = ('Cc', 'Cf', 'Cs', 'Co', 'Zl', 'Zp')
B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
MULTICODEC_ED25519 = b'\xed\x01'


def swept(text: str) -> str:
    cleaned = ''.join(' ' if unicodedata.category(c) in INVISIBLE_CATEGORIES else c for c in text).strip()
    return cleaned


def b58decode(s: str) -> bytes:
    n = 0
    for ch in s:
        n = n * 58 + B58.index(ch)
    raw = n.to_bytes((n.bit_length() + 7) // 8, 'big') if n else b''
    pad = 0
    for ch in s:
        if ch == '1':
            pad += 1
        else:
            break
    return b'\x00' * pad + raw


def pubkey_from_did(did: str) -> bytes:
    if not did.startswith('did:key:z'):
        raise ValueError('expected did:key:z...')
    raw = b58decode(did[len('did:key:z'):])
    if not raw.startswith(MULTICODEC_ED25519):
        raise ValueError('did:key is not Ed25519 multicodec')
    pub = raw[len(MULTICODEC_ED25519):]
    if len(pub) != 32:
        raise ValueError(f'expected 32-byte Ed25519 pubkey, got {len(pub)} bytes')
    return pub


def parse_signed_url(url: str) -> dict[str, Any]:
    parsed = urllib.parse.urlparse(url)
    path = urllib.parse.unquote(parsed.path)
    m = re.match(r'^/r/([^/]+)/say-signed/(did:key:z[^/]+)/([^/]+)/([^/]+)/(.+)$', path)
    if not m:
        raise ValueError('URL does not match /r/<room>/say-signed/<did>/<sig>/<nonce>/<text>')
    room, did, sig, nonce, text = m.groups()
    raw_text = text
    canonical_text = swept(raw_text)
    return {
        'url': url,
        'room': room,
        'did': did,
        'sig': sig,
        'nonce': nonce,
        'raw_text': raw_text,
        'canonical_text': canonical_text,
        'payload': f'{room}|{nonce}|{canonical_text}',
        'query': parsed.query,
    }


def verify_signature(did: str, payload: str, sig_b64url: str) -> tuple[bool, str | None]:
    try:
        pub = pubkey_from_did(did)
        pad = '=' * (-len(sig_b64url) % 4)
        sig = base64.urlsafe_b64decode(sig_b64url + pad)
        Ed25519PublicKey.from_public_bytes(pub).verify(sig, payload.encode())
        return True, None
    except Exception as e:
        return False, str(e)


def live_room_nonce_check(room: str, did: str, nonce: str, limit: int = 200) -> dict[str, Any]:
    out = {'checked': False, 'room_read_ok': False, 'last_seen_nonce_for_did': None, 'risk': 'unknown', 'detail': None}
    try:
        u = f'https://technocore.chat/r/{urllib.parse.quote(room)}?limit={limit}&format=json'
        req = urllib.request.Request(u, headers={'User-Agent': 'FlipFlopper-Validator/1.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode('utf-8', 'ignore'))
        out['checked'] = True
        out['room_read_ok'] = True
        nonces = []
        for msg in data.get('messages', []):
            if msg.get('from') == did and msg.get('nonce') is not None:
                try:
                    nonces.append(int(msg['nonce']))
                except Exception:
                    pass
        if nonces:
            last_seen = max(nonces)
            out['last_seen_nonce_for_did'] = last_seen
            try:
                current = int(nonce)
                if current <= last_seen:
                    out['risk'] = 'high'
                    out['detail'] = 'nonce is not greater than the highest recently observed nonce for this DID in this room'
                else:
                    out['risk'] = 'low'
                    out['detail'] = 'nonce is greater than the highest recently observed nonce for this DID in this room'
            except Exception:
                out['risk'] = 'high'
                out['detail'] = 'nonce is not numeric'
        else:
            out['risk'] = 'unknown'
            out['detail'] = 'no recent messages for this DID found in the sampled room window'
    except Exception as e:
        out['detail'] = str(e)
    return out


def analyze(url: str, check_live: bool = False) -> dict[str, Any]:
    parsed = parse_signed_url(url)
    sig_ok, sig_error = verify_signature(parsed['did'], parsed['payload'], parsed['sig'])
    warnings = []
    if parsed['raw_text'] != parsed['canonical_text']:
        warnings.append('raw text is altered by Technocore sweep/trim; signatures must cover the canonical text, not the raw visual input')
    try:
        int(parsed['nonce'])
    except Exception:
        warnings.append('nonce is not numeric; live endpoint should reject it')
    if len(parsed['nonce']) > 19:
        warnings.append('nonce is longer than 19 digits; live endpoint should reject it')
    if len(parsed['canonical_text']) > 4096:
        warnings.append('canonical text exceeds 4096 chars; live endpoint should reject it')
    result = {
        'valid_signature': sig_ok,
        'signature_error': sig_error,
        'room': parsed['room'],
        'did': parsed['did'],
        'nonce': parsed['nonce'],
        'raw_text': parsed['raw_text'],
        'canonical_text': parsed['canonical_text'],
        'canonical_text_changed': parsed['raw_text'] != parsed['canonical_text'],
        'payload': parsed['payload'],
        'warnings': warnings,
        'limitations': [
            'offline validation cannot prove whether the live server will reject replay or stale nonce without checking recent room state',
            'offline validation cannot prove duplicate-filter outcomes',
        ],
    }
    if check_live:
        result['live_room_nonce_check'] = live_room_nonce_check(parsed['room'], parsed['did'], parsed['nonce'])
    return result


def main():
    ap = argparse.ArgumentParser(description='Validate a Technocore say-signed URL offline.')
    ap.add_argument('--url', required=True, help='Full /r/<room>/say-signed/... URL')
    ap.add_argument('--check-live', action='store_true', help='Also sample recent room messages to estimate nonce freshness risk')
    ap.add_argument('--pretty', action='store_true', help='Pretty-print JSON')
    args = ap.parse_args()
    out = analyze(args.url, check_live=args.check_live)
    json.dump(out, sys.stdout, indent=2 if args.pretty else None, ensure_ascii=False)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
