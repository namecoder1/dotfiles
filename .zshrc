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
export PATH="/opt/homebrew/opt/node@22/bin:$PATH"
export PATH="/opt/homebrew/opt/node@22/bin:$PATH"

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
