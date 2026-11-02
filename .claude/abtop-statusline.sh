#!/bin/bash
input=$(cat)

ctx_pct=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | awk '{printf "%.0f", $1}')
model=$(echo "$input" | jq -r '.model.display_name // "unknown"')
cwd=$(echo "$input" | jq -r '.workspace.current_dir // ""')
cost=$(echo "$input" | jq -r '.cost.total_cost_usd // 0' | awk '{printf "%.4f", $1}')
tokens_in=$(echo "$input" | jq -r '.context_window.total_input_tokens // 0')
tokens_out=$(echo "$input" | jq -r '.context_window.total_output_tokens // 0')

# Limiti di utilizzo (Pro/Max) — assenti finché non arriva la prima risposta della sessione
five_pct=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
five_reset=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
week_pct=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
week_reset=$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')

limit_color() {
  local pct_int
  pct_int=$(printf '%.0f' "$1")
  if [ "$pct_int" -ge 80 ]; then echo '\033[01;31m'
  elif [ "$pct_int" -ge 50 ]; then echo '\033[01;33m'
  else echo '\033[01;32m'; fi
}

if [ -n "$five_pct" ]; then
  five_color=$(limit_color "$five_pct")
  five_str=$(printf '%b5h: %.0f%%\033[00m' "$five_color" "$five_pct")
  [ -n "$five_reset" ] && five_str="$five_str (reset $(date -r "${five_reset%.*}" '+%H:%M'))"
else
  five_str=$'\033[02m5h: --\033[00m'
fi

if [ -n "$week_pct" ]; then
  week_color=$(limit_color "$week_pct")
  week_str=$(printf '%b7d: %.0f%%\033[00m' "$week_color" "$week_pct")
  [ -n "$week_reset" ] && week_str="$week_str (reset $(date -r "${week_reset%.*}" '+%d/%m %H:%M'))"
else
  week_str=$'\033[02m7d: --\033[00m'
fi

# Colore contesto
if [ "$ctx_pct" -ge 75 ]; then ctx_color='\033[01;31m'
elif [ "$ctx_pct" -ge 40 ]; then ctx_color='\033[01;33m'
else ctx_color='\033[01;32m'; fi

# Git info
branch=$(git -C "$cwd" rev-parse --abbrev-ref HEAD 2>/dev/null)
repo=$(basename "$cwd")

# Riga 1: repo/branch + modello + contesto
if [ -n "$branch" ]; then
  printf '\033[01;36m %s\033[00m \033[01;35m(%s)\033[00m | \033[01;37m%s\033[00m | ctx: %b%s%%\033[00m | \033[01;33m$%s\033[00m' \
    "$repo" "$branch" "$model" "$ctx_color" "$ctx_pct" "$cost"
else
  printf '\033[01;36m %s\033[00m | \033[01;37m%s\033[00m | ctx: %b%s%%\033[00m | \033[01;33m$%s\033[00m' \
    "$repo" "$model" "$ctx_color" "$ctx_pct" "$cost"
fi

# Newline → seconda riga
printf '\n'

# Riga 2: token in/out
printf '\033[02m  in: %s tok  |  out: %s tok\033[00m' "$tokens_in" "$tokens_out"

printf '\n'

# Riga 3: limiti 5h / settimanale — sempre presente
printf '  %b  |  %b' "$five_str" "$week_str"
