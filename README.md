# dotfiles

Personal macOS dotfiles managed with a bare git repo — no symlinks, no extra tools.

## Restore on a new machine

```bash
# 1. Clone il repo
git clone --bare <REPO_URL> $HOME/.dotfiles

# 2. Definisci l'alias temporaneo
alias dotfiles='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'

# 3. Checkout dei file
dotfiles checkout
dotfiles config --local status.showUntrackedFiles no
```

Se il checkout fallisce per file esistenti, fai il backup e riprova:

```bash
dotfiles checkout 2>&1 | grep "^\s" | awk '{print $1}' | xargs -I{} mv {} {}.bak
dotfiles checkout
```

## Uso quotidiano

```bash
dotfiles status
dotfiles add ~/.zshrc
dotfiles commit -m "zsh: aggiungi alias foo"
dotfiles push
```

## File tracciati

| File / Directory | Tool |
|---|---|
| `.zshrc`, `.zshenv`, `.zprofile` | Zsh |
| `.p10k.zsh` | Powerlevel10k |
| `.gitconfig` | Git |
| `.gitignore` | Git (esclusioni globali repo) |
| `.aerospace.toml` | AeroSpace (window manager) |
| `.config/git/ignore` | Gitignore globale |
| `.config/nvim/` | Neovim (Lazy.nvim) |
| `.config/fastfetch/config.jsonc` | Fastfetch |
| `.config/btop/btop.conf` | btop |
| `.config/gh/config.yml` | GitHub CLI |
| `.config/fish/conf.d/` | Fish shell |

## Non tracciato

| File | Motivo |
|---|---|
| `.wakatime.cfg` | API key |
| `.config/stripe/` | Chiavi Stripe |
| `.config/sanity/config.json` | Auth token Sanity |
| `.config/gh/hosts.yml` | OAuth session GitHub |
| `.ssh/` | Chiavi SSH private |
| `.zsh_history`, `.viminfo` | Cronologie locali |
