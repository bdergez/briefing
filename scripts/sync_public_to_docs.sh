#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

mkdir -p \
  "$ROOT/docs"

cp "$ROOT/index.html" "$ROOT/docs/index.html"
cp "$ROOT/dev.html" "$ROOT/docs/dev.html"
cp "$ROOT/manifest.json" "$ROOT/docs/manifest.json"
cp "$ROOT/manifest-dev.json" "$ROOT/docs/manifest-dev.json"
cp "$ROOT/icon.svg" "$ROOT/docs/icon.svg"
cp "$ROOT/icon-dev.svg" "$ROOT/docs/icon-dev.svg"
cp "$ROOT/service-worker.js" "$ROOT/docs/service-worker.js"

touch "$ROOT/docs/.nojekyll"

echo "Synced public site files to docs/"
