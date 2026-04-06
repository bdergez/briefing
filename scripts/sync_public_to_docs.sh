#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PUBLIC_DIR="$ROOT/public"
DOCS_DIR="$ROOT/docs"

mkdir -p \
  "$DOCS_DIR"

cp "$PUBLIC_DIR/index.html" "$DOCS_DIR/index.html"
cp "$PUBLIC_DIR/dev.html" "$DOCS_DIR/dev.html"
cp "$PUBLIC_DIR/manifest.json" "$DOCS_DIR/manifest.json"
cp "$PUBLIC_DIR/manifest-dev.json" "$DOCS_DIR/manifest-dev.json"
cp "$PUBLIC_DIR/icon.svg" "$DOCS_DIR/icon.svg"
cp "$PUBLIC_DIR/icon-dev.svg" "$DOCS_DIR/icon-dev.svg"
cp "$PUBLIC_DIR/service-worker.js" "$DOCS_DIR/service-worker.js"

touch "$DOCS_DIR/.nojekyll"

echo "Synced public/ site files to docs/"
