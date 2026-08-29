#!/usr/bin/env python3
import argparse
import pathlib
import subprocess
import sys

BASE = pathlib.Path('/root/.hermes/document_cache/flop-technocore-probe-flipflopper/tools/activation-adapters')
MAP = {
    'faucet': BASE / 'faucet_adapter.py',
    'wallet': BASE / 'wallet_adapter.py',
    'app': BASE / 'app_inference_adapter.py',
    'inference': BASE / 'app_inference_adapter.py',
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('surface_type', choices=['faucet', 'wallet', 'app', 'inference'])
    ap.add_argument('url')
    ap.add_argument('--write-report', action='store_true')
    ap.add_argument('--pretty', action='store_true')
    args = ap.parse_args()
    cmd = ['python', str(MAP[args.surface_type]), args.url]
    if args.write_report:
        cmd.append('--write-report')
    if args.pretty:
        cmd.append('--pretty')
    raise SystemExit(subprocess.call(cmd))


if __name__ == '__main__':
    main()
