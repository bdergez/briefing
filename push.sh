#!/bin/bash
cd "/Users/bedergez/Code/Claude Code/Briefing"
rm -f .git/index.lock

# Use argument if provided, otherwise prompt
if [ -n "$1" ]; then
  msg="$1"
else
  echo ""
  read -p "📝 Describe this update (press Enter for 'Update dashboard'): " msg
  msg=${msg:-"Update dashboard"}
fi

git add index.html news-dashboard.html dev.html manifest.json manifest-dev.json service-worker.js icon.svg icon-dev.svg push.sh PROJECT.md
git commit -m "$msg"
git push
echo ""
echo "✅ Done! Site will update at https://bdergez.github.io/briefing/ in ~60 seconds."
echo ""
read -p "Press Enter to close..."
