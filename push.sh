#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

./scripts/sync_public_to_docs.sh

# Use argument if provided, otherwise prompt
if [ -n "$1" ]; then
  msg="$1"
else
  echo ""
  read -p "📝 Describe this update (press Enter for 'Update dashboard'): " msg
  msg=${msg:-"Update dashboard"}
fi

git add \
  index.html dev.html \
  manifest.json manifest-dev.json \
  icon.svg icon-dev.svg \
  service-worker.js \
  docs \
  push.sh README.md scripts/sync_public_to_docs.sh
git commit -m "$msg"
git push
echo ""
echo "✅ Done! Site will update at https://bdergez.github.io/briefing/ in ~60 seconds."
echo ""
read -p "Press Enter to close..."
