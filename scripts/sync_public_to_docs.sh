#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

mkdir -p \
  "$ROOT/docs" \
  "$ROOT/docs/data" \
  "$ROOT/docs/homes" \
  "$ROOT/docs/homes/data"

cp "$ROOT/index.html" "$ROOT/docs/index.html"
cp "$ROOT/dev.html" "$ROOT/docs/dev.html"
cp "$ROOT/manifest.json" "$ROOT/docs/manifest.json"
cp "$ROOT/manifest-dev.json" "$ROOT/docs/manifest-dev.json"
cp "$ROOT/icon.svg" "$ROOT/docs/icon.svg"
cp "$ROOT/icon-dev.svg" "$ROOT/docs/icon-dev.svg"
cp "$ROOT/service-worker.js" "$ROOT/docs/service-worker.js"
cp "$ROOT/homes.html" "$ROOT/docs/homes.html"
cp "$ROOT/data/house-markets.json" "$ROOT/docs/data/house-markets.json"

cp "$ROOT/homes/index.html" "$ROOT/docs/homes/index.html"
cp "$ROOT/homes/manifest.json" "$ROOT/docs/homes/manifest.json"
cp "$ROOT/homes/icon.svg" "$ROOT/docs/homes/icon.svg"
cp "$ROOT/homes/service-worker.js" "$ROOT/docs/homes/service-worker.js"
cp "$ROOT/homes/data/house-markets.json" "$ROOT/docs/homes/data/house-markets.json"

touch "$ROOT/docs/.nojekyll"

echo "Synced public site files to docs/"
