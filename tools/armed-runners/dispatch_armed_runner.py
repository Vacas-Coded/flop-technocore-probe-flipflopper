#!/usr/bin/env python3
import argparse
import pathlib
import subprocess

BASE = pathlib.Path('/root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/armed-runners')
MAP = {
    'claim': BASE / 'claim_runner.py',
    'wallet': BASE / 'wallet_connect_runner.py',
    'docs': BASE / 'docs_probe_runner.py',
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('runner', choices=['claim', 'wallet', 'docs'])
    ap.add_argument('url')
    ap.add_argument('--armed', action='store_true')
    ap.add_argument('--acknowledge-side-effects', action='store_true')
    ap.add_argument('--allow-get-probe', action='store_true')
    ap.add_argument('--pretty', action='store_true')
    args = ap.parse_args()
    cmd = ['python', str(MAP[args.runner]), args.url]
    if args.armed:
        cmd.append('--armed')
    if args.acknowledge_side_effects:
        cmd.append('--acknowledge-side-effects')
    if args.allow_get_probe:
        cmd.append('--allow-get-probe')
    if args.pretty:
        cmd.append('--pretty')
    raise SystemExit(subprocess.call(cmd))


if __name__ == '__main__':
    main()
