#!/usr/bin/env python3
import os
import pathlib
import subprocess
import sys
from datetime import datetime, timezone

REPO = pathlib.Path('/root/.hermes/document_cache/flop-technocore-probe-flipflopper')
ENV = pathlib.Path('/root/.hermes/.env')


def load_env():
    vals = {}
    if ENV.exists():
        for line in ENV.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            vals[k] = v
    return vals


def run(cmd):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=180)


def main():
    envvals = load_env()
    user = envvals.get('GITHUB_USER', '')
    token = envvals.get('GITHUB_TOKEN', '')
    if not user or not token:
        print('missing_github_credentials', file=sys.stderr)
        raise SystemExit(2)

    status = run(['git', 'status', '--short', 'docs', 'README.md', 'tools/change-capture', 'tests'])
    if status.returncode != 0:
        print(status.stderr, file=sys.stderr)
        raise SystemExit(status.returncode)
    if not status.stdout.strip():
        print('nothing_to_push')
        return

    run(['git', 'add', 'docs', 'README.md', 'tools/change-capture', 'tests'])
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    commit = run(['git', '-c', 'user.name=Hermes Agent', '-c', 'user.email=hermes@local', 'commit', '-m', f'docs: record FlipFlopper ecosystem updates ({ts})'])
    if commit.returncode != 0:
        print(commit.stdout)
        print(commit.stderr, file=sys.stderr)
        raise SystemExit(commit.returncode)

    remote = f'https://{user}:{token}@github.com/Vacas-Coded/flop-technocore-probe-flipflopper.git'
    push = run(['git', 'push', remote, 'HEAD:main'])
    if push.returncode != 0:
        print(push.stdout)
        print(push.stderr, file=sys.stderr)
        raise SystemExit(push.returncode)

    sha = run(['git', 'rev-parse', '--short', 'HEAD'])
    print(f'pushed {sha.stdout.strip()}')


if __name__ == '__main__':
    main()
