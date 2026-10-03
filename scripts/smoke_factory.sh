#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source .venv/bin/activate

BOOK="$ROOT/books/cozy-dogs-cats"
cbf validate "$BOOK"
cbf build-interior "$BOOK"
cbf qc "$BOOK"
test -f "$ROOT/output/cozy-dogs-cats/cozy-dogs-cats_interior.pdf"
test -f "$ROOT/output/cozy-dogs-cats/build_manifest.json"
test -f "$ROOT/output/cozy-dogs-cats/qc_report.json"
test -f "$ROOT/output/cozy-dogs-cats/qc_report.txt"
echo "smoke OK"
