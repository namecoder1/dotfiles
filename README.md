# dotfiles

Personal macOS dotfiles managed with a bare git repo — no symlinks, no extra tools.

## Restore on a new machine

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/namecoder1/dotfiles/main/install.sh)"
```

Lo script in ordine:
1. Clona il bare repo in `~/.dotfiles`
2. Fa il checkout di tutti i file in `$HOME`
3. Se trova conflitti, li sposta in `~/.dotfiles-backup/<timestamp>/` e riprova
4. Installa Homebrew se mancante (Apple Silicon e Intel)
5. Esegue `brew bundle install` dal Brewfile

> Prerequisito: `git` disponibile — su macOS basta `xcode-select --install`

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
