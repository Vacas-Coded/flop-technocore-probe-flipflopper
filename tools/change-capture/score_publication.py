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


def score_update(path: pathlib.Path) -> dict:
    text = path.read_text()
    title = text.splitlines()[0].lstrip('#').strip() if text.splitlines() else path.stem
    summary = section(text, 'Summary')
    why = section(text, 'Why it matters')
    verified = bullets(section(text, 'Verified'))
    uncertain = bullets(section(text, 'Still uncertain'))
    evidence = bullets(section(text, 'Evidence'))

    utility = 25 if why else 10
    if re.search(r'operator|verify|readiness|claim|wallet|docs|surface|watcher|testnet|api|auth', (summary + ' ' + why).lower()):
        utility = min(30, utility + 5)

    evidence_score = min(25, len(evidence) * 8 + (5 if len(evidence) >= 2 else 0))
    verification_score = min(20, len(verified) * 7)

    novelty = 10
    if re.search(r'added|new|first|integrated|automation|pipeline|runner|adapter|playbook|scoring', title.lower() + ' ' + summary.lower()):
        novelty = 18
    if re.search(r'live|activated|launch|opened|faucet|testnet', title.lower() + ' ' + summary.lower()):
        novelty = 20

    actionability = 8
    if re.search(r'how to verify|what changed|why it matters|operator|checklist|playbook|workflow|ready', (summary + ' ' + why).lower()):
        actionability = 15

    uncertainty_penalty = min(20, len(uncertain) * 4)
    if any('still needs human' in x.lower() or 'semantic meaning' in x.lower() for x in uncertain):
        uncertainty_penalty += 3
    uncertainty_penalty = min(20, uncertainty_penalty)

    total = utility + evidence_score + verification_score + novelty + actionability - uncertainty_penalty
    total = max(0, min(100, total))

    if total >= 70:
        recommendation = 'autopublish'
    elif total >= 50:
        recommendation = 'draft_only'
    else:
        recommendation = 'kb_only'

    return {
        'title': title,
        'path': str(path),
        'components': {
            'utility': utility,
            'evidence': evidence_score,
            'verification': verification_score,
            'novelty': novelty,
            'actionability': actionability,
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
