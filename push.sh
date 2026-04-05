#!/bin/bash
set -euo pipefail

cd "/Users/bedergez/Code/Codex/Briefing_claude"
rm -f .git/index.lock

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
  index.html dev.html news-dashboard.html \
  manifest.json manifest-dev.json \
  icon.svg icon-dev.svg \
  service-worker.js homes.html \
  data/house-markets.json \
  homes/index.html homes/manifest.json homes/icon.svg homes/service-worker.js homes/data/house-markets.json \
  docs \
  push.sh PROJECT.md scripts/sync_public_to_docs.sh
git commit -m "$msg"
git push
echo ""
echo "✅ Done! Site will update at https://bdergez.github.io/briefing/ in ~60 seconds."
echo ""
read -p "Press Enter to close..."
