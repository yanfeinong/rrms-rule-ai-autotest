#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m pip install -r requirements.txt
python3 run.py --all --env local --release "${RELEASE_ID:-R_LOCAL}" --biz-date "${BIZ_DATE:-2026-03-24}"

echo "Local CI run finished."
