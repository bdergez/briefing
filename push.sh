#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

bash ./scripts/sync_public_to_docs.sh

# Use argument if provided, otherwise prompt
if [ "$#" -gt 0 ] && [ -n "${1-}" ]; then
  msg="$1"
else
  echo ""
  read -p "📝 Describe this update (press Enter for 'Update dashboard'): " msg
  msg=${msg:-"Update dashboard"}
fi

git add \
  public \
  docs \
  push.sh README.md wrangler.toml \
  scripts/sync_public_to_docs.sh \
  .gitignore
git commit -m "$msg"
git push
echo ""
echo "✅ Done! Cloudflare should update https://pmdash.bdergez.workers.dev/ in ~60 seconds."
echo ""
read -p "Press Enter to close..."
