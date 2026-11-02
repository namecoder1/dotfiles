export TERM=xterm-256color
typeset -g POWERLEVEL9K_INSTANT_PROMPT=quiet

# Enable Powerlevel10k instant prompt
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

source ~/powerlevel10k/powerlevel10k.zsh-theme

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

. "$HOME/.local/bin/env"

# placr: DB e cartella progetto fissi indipendentemente da dove lanci il comando globale
export PLACR_DB="/Users/tobi/Developer/active/bracket/tools/placr/data/placr.db"
export PLACR_HOME="/Users/tobi/Developer/active/bracket/tools/placr"
export PATH="/opt/homebrew/opt/node@24/bin:$PATH"

# Segreti/override locali (non tracciati nel repo dotfiles)
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local

# Added by Antigravity
export PATH="/Users/tobi/.antigravity/antigravity/bin:$PATH"

alias dotfiles='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'
alias tailscale="/Applications/Tailscale.app/Contents/MacOS/Tailscale"
alias c='clear'
alias ls='lsd'
alias cat="bat "
# Added by Antigravity
export PATH="/Users/tobi/.antigravity/antigravity/bin:$PATH"
fastfetch

# >>> juliaup initialize >>>

# !! Contents within this block are managed by juliaup !!

path=('/Users/tobi/.juliaup/bin' $path)
export PATH

# <<< juliaup initialize <<<

fpath+=~/.zfunc; autoload -Uz compinit; compinit

zstyle ':completion:*' menu select

# Claude Code: in ~/Developer/materia usa la config Materia (guides/claude-code-materia.md)
# Fuori da materia toglie CLAUDE_CONFIG_DIR ereditato (es. terminale aperto da una sessione materia):
# impostarlo a ~/.claude NON equivale al default e usa un Keychain separato, non loggato.
claude() {
  local dir=""
  case "${CLAUDE_ACCOUNT:-auto}" in
    work)     dir="$HOME/.claude-materia" ;;
    personal) dir="" ;;
    *) [[ "$PWD" == "$HOME/Developer/materia" || "$PWD" == "$HOME/Developer/materia/"* ]] && dir="$HOME/.claude-materia" ;;
  esac
  if [[ -n "$dir" ]]; then
    CLAUDE_CONFIG_DIR="$dir" command claude "$@"
  else
    command env -u CLAUDE_CONFIG_DIR claude "$@"
  fi
}
alias claude-work='CLAUDE_ACCOUNT=work claude'
alias claude-personal='CLAUDE_ACCOUNT=personal claude'
alias claude-help='cat ~/.claude-accounts.md'
