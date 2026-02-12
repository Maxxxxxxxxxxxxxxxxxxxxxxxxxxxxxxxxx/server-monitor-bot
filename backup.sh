#!/bin/bash
set -e
cd /root/apps/FishBot

git add -A

# если нет изменений — просто выходим
if git diff --cached --quiet; then
  echo "No changes to backup."
  exit 0
fi

git commit -m "Auto backup: $(date +'%Y-%m-%d %H:%M:%S')"
git push -u origin main
