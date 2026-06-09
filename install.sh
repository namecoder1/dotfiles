#!/usr/bin/env bash
set -euo pipefail

REPO="https://github.com/namecoder1/dotfiles.git"
DOTFILES="$HOME/.dotfiles"
BACKUP_DIR="$HOME/.dotfiles-backup/$(date +%Y%m%d_%H%M%S)"

# ── Output ─────────────────────────────────────────────────────────────────
info() { printf '\033[0;34m→\033[0m  %s\n' "$*"; }
ok()   { printf '\033[0;32m✓\033[0m  %s\n' "$*"; }
warn() { printf '\033[0;33m!\033[0m  %s\n' "$*"; }
die()  { printf '\033[0;31m✗\033[0m  %s\n' "$*" >&2; exit 1; }

dotfiles() { /usr/bin/git --git-dir="$DOTFILES" --work-tree="$HOME" "$@"; }

# ── 1. Prerequisiti ────────────────────────────────────────────────────────
[[ "$(uname)" == "Darwin" ]] || die "Questo script è pensato per macOS"

if ! command -v git >/dev/null 2>&1; then
  die "git non trovato — installa Xcode CLT con: xcode-select --install"
fi

# ── 2. Clone bare repo ─────────────────────────────────────────────────────
if [[ -d "$DOTFILES" ]]; then
  warn "~/.dotfiles già presente — salto il clone"
else
  info "Clono il bare repo..."
  git clone --bare "$REPO" "$DOTFILES"
  ok "Clone completato"
fi

# ── 3. Checkout con gestione conflitti ─────────────────────────────────────
info "Checkout dei dotfile..."
tmp=$(mktemp)
if ! dotfiles checkout 2>"$tmp"; then
  conflicting=$(grep '^\s' "$tmp" | awk '{print $1}')
  if [[ -n "$conflicting" ]]; then
    warn "File in conflitto trovati — backup in $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    while IFS= read -r file; do
      mkdir -p "$BACKUP_DIR/$(dirname "$file")"
      mv "$HOME/$file" "$BACKUP_DIR/$file"
    done <<< "$conflicting"
    dotfiles checkout
  else
    cat "$tmp" >&2
    die "Checkout fallito per un motivo inatteso"
  fi
fi
rm -f "$tmp"
ok "Checkout completato"

# ── 4. Configura il repo locale ────────────────────────────────────────────
dotfiles config --local status.showUntrackedFiles no
ok "Repository configurato"

# ── 5. Verifica alias in .zshrc ────────────────────────────────────────────
# Il checkout porta già il .zshrc con l'alias — questo è solo un safety net
ALIAS="alias dotfiles='/usr/bin/git --git-dir=\$HOME/.dotfiles/ --work-tree=\$HOME'"
if grep -qF 'alias dotfiles=' "$HOME/.zshrc" 2>/dev/null; then
  ok "Alias dotfiles già presente in .zshrc"
else
  printf '\n%s\n' "$ALIAS" >> "$HOME/.zshrc"
  ok "Alias dotfiles aggiunto a .zshrc"
fi

# ── 6. Homebrew ────────────────────────────────────────────────────────────
if command -v brew >/dev/null 2>&1; then
  ok "Homebrew già installato ($(brew --version | head -1 | awk '{print $2}'))"
else
  info "Installo Homebrew..."
  NONINTERACTIVE=1 /bin/bash -c \
    "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  # Aggiungi brew al PATH per il resto dello script
  if   [[ -x /opt/homebrew/bin/brew ]]; then eval "$(/opt/homebrew/bin/brew shellenv)"   # Apple Silicon
  elif [[ -x /usr/local/bin/brew    ]]; then eval "$(/usr/local/bin/brew shellenv)"       # Intel
  fi
  ok "Homebrew installato"
fi

# ── 7. Brew bundle ─────────────────────────────────────────────────────────
if [[ -f "$HOME/Brewfile" ]]; then
  info "Installo pacchetti dal Brewfile (può richiedere alcuni minuti)..."
  brew bundle install --file="$HOME/Brewfile"
  ok "Pacchetti installati"
fi

# ── Fine ───────────────────────────────────────────────────────────────────
printf '\n\033[0;32m✓  Setup completato!\033[0m\n'
printf '   Riavvia il terminale o esegui: \033[1msource ~/.zshrc\033[0m\n'
[[ -d "$BACKUP_DIR" ]] && printf '   File sostituiti in backup: \033[1m%s\033[0m\n' "$BACKUP_DIR"
