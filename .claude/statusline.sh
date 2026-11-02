#!/bin/bash
input=$(cat)

# Extract fields
cwd=$(echo "$input" | jq -r '.workspace.current_dir')
ctx_pct=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
model=$(echo "$input" | jq -r '.model.display_name')

# Color context usage
if [ "$ctx_pct" -ge 60 ]; then
  ctx_color='\033[01;31m'   # red
elif [ "$ctx_pct" -ge 40 ]; then
  ctx_color='\033[01;33m'   # yellow
else
  ctx_color='\033[01;32m'   # green
fi

# Git repo name if available
if git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
  repo=$(basename "$cwd")
  branch=$(git -C "$cwd" rev-parse --abbrev-ref HEAD 2>/dev/null)
  printf '\033[01;36m%s\033[00m (%s) | model: %s | ctx: %b%s%%\033[00m' \
    "$repo" "$branch" "$model" "$ctx_color" "$ctx_pct"
else
  printf '\033[01;36m%s\033[00m | model: %s | ctx: %b%s%%\033[00m' \
    "$cwd" "$model" "$ctx_color" "$ctx_pct"
fi


