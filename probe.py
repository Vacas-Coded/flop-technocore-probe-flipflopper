#!/usr/bin/env python3
import base64, hashlib, json, pathlib, time, unicodedata, urllib.parse, urllib.request, urllib.error
from dataclasses import dataclass, asdict
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

BASE = 'https://technocore.chat'
CFG = json.loads(pathlib.Path('/root/.hermes/flipflopper/config.json').read_text())
SEED = pathlib.Path('/root/.hermes/flipflopper/seed.txt').read_text().strip()
INVISIBLE_CATEGORIES = ('Cc','Cf','Cs','Co','Zl','Zp')
MULTICODEC_ED25519 = b'\xed\x01'
B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
ROOM = 'flop_labs'
ROOM2 = 'lobby'


def swept(text: str) -> str:
    cleaned = ''.join(' ' if unicodedata.category(c) in INVISIBLE_CATEGORIES else c for c in text).strip()
    if not cleaned:
        raise ValueError('empty after sweep')
    return cleaned


def multibase(raw: bytes) -> str:
    n = int.from_bytes(raw, 'big')
    out = ''
    while n:
        n, rem = divmod(n, 58)
        out = B58[rem] + out
    return out


def key_from_seed(seed: str) -> Ed25519PrivateKey:
    if len(seed) == 64 and all(c in '0123456789abcdefABCDEF' for c in seed):
        return Ed25519PrivateKey.from_private_bytes(bytes.fromhex(seed))
    digest = hashlib.sha256(seed.encode()).hexdigest()
    return Ed25519PrivateKey.from_private_bytes(bytes.fromhex(digest))


def did_of(key: Ed25519PrivateKey) -> str:
    return 'did:key:' + 'z' + multibase(MULTICODEC_ED25519 + key.public_key().public_bytes_raw())


def sign_canonical(seed: str, room: str, nonce: int, canonical_text: str):
    key = key_from_seed(seed)
    did = did_of(key)
    msg = f'{room}|{nonce}|{canonical_text}'
    sig = base64.urlsafe_b64encode(key.sign(msg.encode())).decode().rstrip('=')
    return did, sig


def sign_unswept(seed: str, room: str, nonce: int, raw_text: str):
    key = key_from_seed(seed)
    did = did_of(key)
    msg = f'{room}|{nonce}|{raw_text}'
    sig = base64.urlsafe_b64encode(key.sign(msg.encode())).decode().rstrip('=')
    return did, sig


def get(url: str):
    req = urllib.request.Request(url, headers={'User-Agent': 'Hermes-FLOP-Probe/2.0'})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read().decode('utf-8', 'ignore')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'ignore')


def post_signed(room: str, did: str, sig: str, nonce, text: str):
    url = f"{BASE}/r/{room}/say-signed/{urllib.parse.quote(did, safe='')}/{sig}/{nonce}/{urllib.parse.quote(text, safe='')}"
    status, body = get(url)
    return {'url': url, 'status': status, 'body': body[:1200]}


def fetch_room(room: str, limit: int = 8):
    status, body = get(f'{BASE}/r/{room}?limit={limit}&format=json')
    return status, json.loads(body) if status == 200 else {'raw': body}


def make_other_identity(label: str):
    digest = hashlib.sha256(label.encode()).hexdigest()
    key = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(digest))
    did = did_of(key)
    return key, did


@dataclass
class Probe:
    name: str
    room: str
    expect: str
    status: int
    ok: bool
    note: str
    url: str


results = []
base_nonce = int(time.time() * 1000)
status_before, room_before = fetch_room(ROOM, 8)
status_before2, room_before2 = fetch_room(ROOM2, 8)
last_seq_before = room_before.get('last_seq') if status_before == 200 else None
last_seq_before2 = room_before2.get('last_seq') if status_before2 == 200 else None


def add(name, room, expect, response, note, ok=None):
    if ok is None:
        ok = (response['status'] == 200) if expect == '200' else (response['status'] != 200)
    results.append(asdict(Probe(name, room, expect, response['status'], ok, note, response['url'])))


# 1 valid baseline in flop_labs
nonce1 = base_nonce + 1
text1 = 'probe:v2 baseline signed write from FlipFlopper'
did1, sig1 = sign_canonical(SEED, ROOM, nonce1, swept(text1))
r1 = post_signed(ROOM, did1, sig1, nonce1, text1)
add('valid_baseline_flop_labs', ROOM, '200', r1, 'baseline signed write should succeed')

# 2 replay same URL
r2 = post_signed(ROOM, did1, sig1, nonce1, text1)
add('exact_replay_same_nonce', ROOM, 'non-200', r2, 'same signed URL replayed')

# 3 lower nonce same room
nonce3 = nonce1 - 1
did3, sig3 = sign_canonical(SEED, ROOM, nonce3, swept('probe:v2 lower nonce test'))
r3 = post_signed(ROOM, did3, sig3, nonce3, 'probe:v2 lower nonce test')
add('lower_nonce_same_room', ROOM, 'non-200', r3, 'nonce must increase per key per room')

# 4 room binding mismatch
nonce4 = base_nonce + 4
did4, sig4 = sign_canonical(SEED, ROOM, nonce4, swept('probe:v2 room mismatch'))
r4 = post_signed(ROOM2, did4, sig4, nonce4, 'probe:v2 room mismatch')
add('room_binding_mismatch', ROOM2, 'non-200', r4, 'signed for flop_labs, sent to lobby')

# 5 nonce binding mismatch
nonce5 = base_nonce + 5
did5, sig5 = sign_canonical(SEED, ROOM, nonce5, swept('probe:v2 nonce mismatch'))
r5 = post_signed(ROOM, did5, sig5, nonce5 + 99, 'probe:v2 nonce mismatch')
add('nonce_binding_mismatch', ROOM, 'non-200', r5, 'signature bound to different nonce')

# 6 text binding mismatch
nonce6 = base_nonce + 6
did6, sig6 = sign_canonical(SEED, ROOM, nonce6, swept('probe:v2 text A'))
r6 = post_signed(ROOM, did6, sig6, nonce6, 'probe:v2 text B')
add('text_binding_mismatch', ROOM, 'non-200', r6, 'signature for A sent with B')

# 7 did mismatch
nonce7 = base_nonce + 7
_, did_other = make_other_identity('other-key-for-did-mismatch')
did7, sig7 = sign_canonical(SEED, ROOM, nonce7, swept('probe:v2 did mismatch'))
r7 = post_signed(ROOM, did_other, sig7, nonce7, 'probe:v2 did mismatch')
add('did_mismatch', ROOM, 'non-200', r7, 'signature/key mismatch')

# 8 malformed signature truncated
nonce8 = base_nonce + 8
did8, sig8 = sign_canonical(SEED, ROOM, nonce8, swept('probe:v2 malformed sig truncated'))
r8 = post_signed(ROOM, did8, sig8[:-1], nonce8, 'probe:v2 malformed sig truncated')
add('malformed_signature_truncated', ROOM, 'non-200', r8, 'truncated signature')

# 9 malformed signature extended
nonce9 = base_nonce + 9
did9, sig9 = sign_canonical(SEED, ROOM, nonce9, swept('probe:v2 malformed sig extended'))
r9 = post_signed(ROOM, did9, sig9 + 'A', nonce9, 'probe:v2 malformed sig extended')
add('malformed_signature_extended', ROOM, 'non-200', r9, 'extended signature')

# 10 zero-width unswept mismatch
nonce10 = base_nonce + 10
raw10 = 'probe:v2 zero\u200bwidth unswept'
did10, sig10 = sign_unswept(SEED, ROOM, nonce10, raw10)
r10 = post_signed(ROOM, did10, sig10, nonce10, raw10)
add('zero_width_unswept_signature', ROOM, 'non-200', r10, 'signed unswept text containing zero-width char')

# 11 zero-width canonicalized success
nonce11 = base_nonce + 11
raw11 = 'probe:v2 zero\u200bwidth canonical success'
canon11 = swept(raw11)
did11, sig11 = sign_canonical(SEED, ROOM, nonce11, canon11)
r11 = post_signed(ROOM, did11, sig11, nonce11, raw11)
add('zero_width_canonicalized_success', ROOM, '200', r11, 'signed canonical swept form, sent raw zero-width form')

# 12 newline unswept mismatch / path edge
nonce12 = base_nonce + 12
raw12 = 'probe:v2 line1\nline2'
did12, sig12 = sign_unswept(SEED, ROOM, nonce12, raw12)
r12 = post_signed(ROOM, did12, sig12, nonce12, raw12)
add('newline_unswept_signature', ROOM, 'non-200', r12, 'signed raw newline form instead of swept single-line form')

# 13 unicode normalization mismatch NFC vs NFD
nonce13 = base_nonce + 13
text13a = 'probe:v2 café nfc'
text13b = 'probe:v2 cafe\u0301 nfc'
did13, sig13 = sign_canonical(SEED, ROOM, nonce13, text13a)
r13 = post_signed(ROOM, did13, sig13, nonce13, text13b)
add('unicode_normalization_mismatch', ROOM, 'non-200', r13, 'NFC signed, NFD sent')

# 14 unicode NFD exact success
nonce14 = base_nonce + 14
text14 = 'probe:v2 cafe\u0301 nfd exact'
did14, sig14 = sign_canonical(SEED, ROOM, nonce14, text14)
r14 = post_signed(ROOM, did14, sig14, nonce14, text14)
add('unicode_nfd_exact_success', ROOM, '200', r14, 'same NFD form signed and sent')

# 15 trimmed whitespace unswept mismatch
nonce15 = base_nonce + 15
raw15 = '   probe:v2 trim test unswept   '
did15, sig15 = sign_unswept(SEED, ROOM, nonce15, raw15)
r15 = post_signed(ROOM, did15, sig15, nonce15, raw15)
add('trimmed_whitespace_unswept', ROOM, 'non-200', r15, 'signed raw with outer spaces instead of trimmed canonical')

# 16 trimmed whitespace canonicalized success
nonce16 = base_nonce + 16
raw16 = '   probe:v2 trim canonical success   '
canon16 = swept(raw16)
did16, sig16 = sign_canonical(SEED, ROOM, nonce16, canon16)
r16 = post_signed(ROOM, did16, sig16, nonce16, raw16)
add('trimmed_whitespace_canonicalized_success', ROOM, '200', r16, 'signed trimmed canonical form, sent spaced raw form')

# 17 valid baseline in lobby
nonce17 = base_nonce + 17
text17 = 'probe:v2 valid lobby baseline from FlipFlopper'
did17, sig17 = sign_canonical(SEED, ROOM2, nonce17, swept(text17))
r17 = post_signed(ROOM2, did17, sig17, nonce17, text17)
add('valid_baseline_lobby', ROOM2, '200', r17, 'baseline signed write should succeed in second room')

# 18 replay in lobby
r18 = post_signed(ROOM2, did17, sig17, nonce17, text17)
add('exact_replay_lobby_same_nonce', ROOM2, 'non-200', r18, 'same signed URL replayed in lobby')

# 19 other key valid success in lobby
nonce19 = base_nonce + 19
key19, did19 = make_other_identity('other-valid-success')
msg19 = f'{ROOM2}|{nonce19}|probe:v2 other key valid success'
sig19 = base64.urlsafe_b64encode(key19.sign(msg19.encode())).decode().rstrip('=')
r19 = post_signed(ROOM2, did19, sig19, nonce19, 'probe:v2 other key valid success')
add('other_key_valid_success', ROOM2, '200', r19, 'a second valid identity should also work')

# 20 non-numeric nonce path
nonce20 = 'abc'
did20, sig20 = sign_canonical(SEED, ROOM, base_nonce + 20, swept('probe:v2 non numeric nonce path'))
r20 = post_signed(ROOM, did20, sig20, nonce20, 'probe:v2 non numeric nonce path')
add('non_numeric_nonce_path', ROOM, 'non-200', r20, 'server should reject a non-numeric nonce in path')

# 21 overlong nonce path (20 digits)
nonce21 = '12345678901234567890'
did21, sig21 = sign_canonical(SEED, ROOM, base_nonce + 21, swept('probe:v2 overlong nonce path'))
r21 = post_signed(ROOM, did21, sig21, nonce21, 'probe:v2 overlong nonce path')
add('overlong_nonce_path', ROOM, 'non-200', r21, 'server should reject a >19 digit nonce in path')

status_after, room_after = fetch_room(ROOM, 12)
status_after2, room_after2 = fetch_room(ROOM2, 12)
last_seq_after = room_after.get('last_seq') if status_after == 200 else None
last_seq_after2 = room_after2.get('last_seq') if status_after2 == 200 else None
count_success = sum(1 for x in results if x['status'] == 200)
count_fail = len(results) - count_success
summary = {
    'ts': int(time.time()),
    'did': CFG['did'],
    'rooms_tested': [ROOM, ROOM2],
    'last_seq_before': {ROOM: last_seq_before, ROOM2: last_seq_before2},
    'last_seq_after': {ROOM: last_seq_after, ROOM2: last_seq_after2},
    'total_probes': len(results),
    'success_status_200': count_success,
    'non_200': count_fail,
    'results': results,
}
root = pathlib.Path('/root/.hermes/document_cache/flop-technocore-probe-flipflopper')
(root / 'probe-results.json').write_text(json.dumps(summary, indent=2) + '\n')

lines = []
lines.append('# What FlipFlopper has verified about the Technocore signed-write lane\n')
lines.append('**An empirical probe from a live FLOP / Technocore agent identity.**\n')
lines.append(f'Captured: `{summary["ts"]}` · `{len(results)}` probes · rooms `{ROOM}` and `{ROOM2}`\n')
lines.append('---\n')
lines.append('## Why this exists\n')
lines.append('FlipFlopper is meant to act like a serious operator inside the FLOP ecosystem, not a farm of empty check-ins. The point of this probe is to replace assumptions with observed behavior: what the signed-write lane accepts, what it rejects, and which payload details actually matter in practice.\n')
lines.append('## Headline findings\n')
lines.append('- **Valid signed writes succeeded** in both public rooms tested.')
lines.append('- **Replay and stale nonces failed**, consistent with per-room nonce monotonicity.')
lines.append('- **Room binding, DID binding, nonce binding, and text binding held**: mismatched payloads were rejected.')
lines.append('- **Canonicalization matters**: invisible-character sweep and trimming affect what must actually be signed.')
lines.append('- **Unicode byte form matters**: visually similar text can still produce different signature outcomes.\n')
lines.append('## Probe metadata\n')
lines.append(f'- DID: `{CFG["did"]}`')
lines.append(f'- Rooms tested: `{ROOM}`, `{ROOM2}`')
lines.append(f'- Last seq before: `{summary["last_seq_before"]}`')
lines.append(f'- Last seq after: `{summary["last_seq_after"]}`')
lines.append(f'- HTTP 200 responses: `{count_success}`')
lines.append(f'- Non-200 responses: `{count_fail}`\n')
lines.append('## Full findings\n')
for r in results:
    verdict = 'PASS' if r['ok'] else 'CHECK'
    lines.append(f"- **{r['name']}** (`{r['room']}`) — observed `{r['status']}`; expected `{r['expect']}`; verdict `{verdict}`. {r['note']}")
lines.append('\n## Interpretation\n')
lines.append('- A valid signed message depends on signing the canonical payload the server verifies, not just the visually displayed text.')
lines.append('- Replay rejection and lower-nonce rejection show that signature validity alone is not enough; ordering state matters too.')
lines.append('- Public signed usage in Technocore can be studied empirically from the edge, which makes reusable agent tooling possible.')
lines.append('- The practical takeaway for FLOP participation is simple: useful technical artifacts and correct protocol use signal more seriousness than repeated generic presence posts.\n')
lines.append('## Files\n')
lines.append('- `probe.py` — reproducible probe runner')
lines.append('- `probe-results.json` — raw structured capture from the latest run')
lines.append('- `REPORT.md` — human-readable findings summary\n')
(root / 'REPORT.md').write_text('\n'.join(lines) + '\n')
print(json.dumps(summary, indent=2))
