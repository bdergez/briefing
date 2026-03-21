#!/bin/bash
cd "/Users/bedergez/Code/Claude Code/Briefing"
rm -f .git/index.lock
git add index.html news-dashboard.html manifest.json service-worker.js icon.svg push.sh
git commit -m "Update dashboard"
git push
echo "✅ Done! Site will update at https://bdergez.github.io/briefing/ in ~60 seconds."
read -p "Press Enter to close..."
