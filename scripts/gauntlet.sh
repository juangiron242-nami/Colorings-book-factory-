#!/usr/bin/env bash
# Gauntlet: specification → measurement → comparison → verification
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== Coloring Book Factory Gauntlet =="
echo "repo: $ROOT"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install -q -e ".[dev]"

echo "-- pytest --"
python -m pytest -q

if [[ -x "$ROOT/scripts/smoke_factory.sh" ]]; then
  echo "-- smoke --"
  "$ROOT/scripts/smoke_factory.sh"
fi

echo "GAUNTLET PASS"
