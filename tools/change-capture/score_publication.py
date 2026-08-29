#!/usr/bin/env python3
import argparse
import json
import pathlib
import re


def section(text: str, name: str) -> str:
    m = re.search(rf'^## {re.escape(name)}\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    return (m.group(1).strip() if m else '')


def bullets(body: str) -> list[str]:
    return [re.sub(r'^-\s*', '', x).strip() for x in body.splitlines() if x.strip()]


def metadata_value(text: str, key: str) -> str:
    m = re.search(rf'^-\s*{re.escape(key)}:\s*(.+)$', text, re.M)
    return m.group(1).strip() if m else ''


def has_any(text: str, patterns: list[str]) -> bool:
    low = text.lower()
    return any(p in low for p in patterns)


def score_update(path: pathlib.Path) -> dict:
    text = path.read_text()
    title = text.splitlines()[0].lstrip('#').strip() if text.splitlines() else path.stem
    source_id = metadata_value(text, 'source_id')
    summary = section(text, 'Summary')
    why = section(text, 'Why it matters')
    verified = bullets(section(text, 'Verified'))
    uncertain = bullets(section(text, 'Still uncertain'))
    evidence = bullets(section(text, 'Evidence'))
    body = ' '.join([title, source_id, summary, why, ' '.join(verified), ' '.join(uncertain), ' '.join(evidence)])
    low = body.lower()

    utility = 18
    if why:
        utility += 6
    if has_any(low, ['operator', 'verify', 'readiness', 'claim', 'wallet', 'docs', 'surface', 'watcher', 'testnet', 'api', 'auth', 'workflow', 'playbook', 'checklist']):
        utility += 6
    utility = min(30, utility)

    evidence_score = min(22, len(evidence) * 7 + (4 if len(evidence) >= 2 else 0) + (4 if any('/root/.hermes/' in x or 'github.com/' in x for x in evidence) else 0))
    verification_score = min(18, len(verified) * 6 + (3 if len(verified) >= 2 else 0))

    novelty = 8
    if has_any(low, ['added', 'new', 'first', 'integrated', 'automation', 'pipeline', 'runner', 'adapter', 'playbook', 'scoring']):
        novelty = 14
    if has_any(low, ['live', 'activated', 'launch', 'opened', 'faucet', 'testnet', 'release', 'mainnet']):
        novelty = 18
    if has_any(low, ['explicit_live_surface', 'activation detected', 'readiness transition']):
        novelty = 20

    actionability = 6
    if has_any(low, ['how to verify', 'what changed', 'why it matters', 'operator', 'checklist', 'playbook', 'workflow', 'ready', 'guide', 'steps']):
        actionability = 12
    if has_any(low, ['claim', 'wallet', 'faucet', 'auth', 'api', 'surface', 'entrypoint']):
        actionability = min(15, actionability + 3)

    airdrop_leverage = 0
    if has_any(low, ['flop', 'technocore', 'testnet', 'airdrop']):
        airdrop_leverage += 4
    if has_any(low, ['public', 'repo', 'github', 'document', 'evidence', 'proof-of-work', 'proof of work']):
        airdrop_leverage += 4
    if has_any(low, ['watcher', 'runner', 'adapter', 'playbook', 'readiness', 'activation', 'faucet', 'wallet', 'claim']):
        airdrop_leverage += 5
    if has_any(low, ['operator', 'ecosystem', 'useful', 'utility', 'workflow', 'guide']):
        airdrop_leverage += 3
    if has_any(low, ['minor wording', 'cleanup only', 'small wording cleanup only']):
        airdrop_leverage -= 6
    airdrop_leverage = max(0, min(15, airdrop_leverage))

    uncertainty_penalty = min(18, len(uncertain) * 4)
    if any('still needs human' in x.lower() or 'semantic meaning' in x.lower() or 'manual confirmation' in x.lower() for x in uncertain):
        uncertainty_penalty = min(20, uncertainty_penalty + 3)

    total = utility + evidence_score + verification_score + novelty + actionability + airdrop_leverage - uncertainty_penalty
    total = max(0, min(100, total))

    if total >= 70:
        recommendation = 'autopublish'
    elif total >= 50:
        recommendation = 'draft_only'
    else:
        recommendation = 'kb_only'

    return {
        'title': title,
        'source_id': source_id,
        'path': str(path),
        'components': {
            'utility': utility,
            'evidence': evidence_score,
            'verification': verification_score,
            'novelty': novelty,
            'actionability': actionability,
            'airdrop_leverage': airdrop_leverage,
            'uncertainty_penalty': uncertainty_penalty,
        },
        'total_score': total,
        'recommendation': recommendation,
        'thresholds': {
            'autopublish_min': 70,
            'draft_only_min': 50,
            'kb_only_max': 49,
        },
        'counts': {
            'verified': len(verified),
            'uncertain': len(uncertain),
            'evidence': len(evidence),
        },
    }


def main():
    ap = argparse.ArgumentParser(description='Score a FlipFlopper update for publication suitability')
    ap.add_argument('update_path')
    ap.add_argument('--pretty', action='store_true')
    args = ap.parse_args()
    out = score_update(pathlib.Path(args.update_path))
    print(json.dumps(out, indent=2 if args.pretty else None, ensure_ascii=False))


if __name__ == '__main__':
    main()
