#!/usr/bin/env python3
import argparse
import pathlib
import re
from datetime import datetime, timezone

REPO = pathlib.Path('/root/.hermes/document_cache/flop-technocore-probe-flipflopper')
UPDATES_DIR = REPO / 'docs' / 'project-updates'
DRAFTS_DIR = REPO / 'docs' / 'publication-drafts'
INDEX = REPO / 'docs' / 'PROJECT_UPDATES.md'


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return re.sub(r'-+', '-', text).strip('-') or 'update'


def main():
    ap = argparse.ArgumentParser(description='Record a verified FLOP/Technocore project update')
    ap.add_argument('--title', required=True)
    ap.add_argument('--source-id', required=True)
    ap.add_argument('--source-url', required=True)
    ap.add_argument('--summary', required=True)
    ap.add_argument('--why-it-matters', required=True)
    ap.add_argument('--verified', action='append', default=[])
    ap.add_argument('--uncertain', action='append', default=[])
    ap.add_argument('--evidence', action='append', default=[])
    ap.add_argument('--post-angle', default='Useful operator update: what changed, why it matters, and how to verify it.')
    args = ap.parse_args()

    ts = datetime.now(timezone.utc)
    stamp = ts.strftime('%Y%m%dT%H%M%SZ')
    day = ts.strftime('%Y-%m-%d')
    slug = slugify(args.title)
    UPDATES_DIR.mkdir(parents=True, exist_ok=True)
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

    update_path = UPDATES_DIR / f'{stamp}_{slug}.md'
    draft_path = DRAFTS_DIR / f'{stamp}_{slug}.md'

    verified = args.verified or ['No extra verified bullets supplied.']
    uncertain = args.uncertain or ['No explicit uncertainty note supplied.']
    evidence = args.evidence or ['No evidence paths supplied.']

    update_body = [
        f'# {args.title}',
        '',
        f'- date_utc: {ts.isoformat()}',
        f'- source_id: {args.source_id}',
        f'- source_url: {args.source_url}',
        '',
        '## Summary',
        args.summary,
        '',
        '## Why it matters',
        args.why_it_matters,
        '',
        '## Verified',
        *[f'- {x}' for x in verified],
        '',
        '## Still uncertain',
        *[f'- {x}' for x in uncertain],
        '',
        '## Evidence',
        *[f'- {x}' for x in evidence],
        '',
        '## Publication assessment',
        '- Worth publishing only if it helps other operators understand a real change faster.',
        f'- Suggested angle: {args.post_angle}',
        '',
    ]
    update_path.write_text('\n'.join(update_body))

    draft_body = [
        f'# Draft — {args.title}',
        '',
        '## Short post',
        f'{args.summary} {args.why_it_matters} Evidence-first takeaway: {args.post_angle}',
        '',
        '## Bullet version',
        f'- Change: {args.summary}',
        f'- Why it matters: {args.why_it_matters}',
        f'- Verification: {verified[0]}',
        f'- Evidence: {evidence[0]}',
        '',
        '## Guardrail',
        '- Do not publish stronger claims than the evidence supports.',
        '',
    ]
    draft_path.write_text('\n'.join(draft_body))

    line = f'- {day} — [{args.title}](project-updates/{update_path.name}) | [draft](publication-drafts/{draft_path.name})\n'
    existing = INDEX.read_text() if INDEX.exists() else '# FlipFlopper Project Updates\n\n## Entries\n'
    INDEX.write_text(existing + line)

    print(update_path)
    print(draft_path)


if __name__ == '__main__':
    main()
