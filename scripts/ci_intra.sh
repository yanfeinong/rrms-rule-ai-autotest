#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -z "${RULE_API_TOKEN:-}" ]]; then
  echo "RULE_API_TOKEN is required in intra mode"
  exit 1
fi

python3 -m pip install -r requirements.txt
python3 run.py --all --env intra --release "${RELEASE_ID:-R_INTRA}" --biz-date "${BIZ_DATE:-2026-03-24}"

echo "Intra CI run finished."
