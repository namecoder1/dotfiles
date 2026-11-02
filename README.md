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
| `.zshrc`, `.zshenv`, `.zprofile`, `.zfunc/` | Zsh (+ completions `placr`, `radar`) |
| `.p10k.zsh` | Powerlevel10k |
| `.gitconfig`, `.gitconfig-bracket`, `.gitconfig-materia` | Git (identità per cartella via `includeIf`) |
| `.gitignore` | Esclusioni del repo dotfiles |
| `.config/git/ignore` | Gitignore globale |
| `.aerospace.toml` | AeroSpace (window manager) |
| `Library/Application Support/com.mitchellh.ghostty/config.ghostty` | Ghostty |
| `.config/herdr/config.toml`, `.config/herdr/tobi/` | herdr (TUI) + plugin locale `tobi-extras` |
| `.config/herdr-app/{settings,keys}.json`, `layouts/` | Herdr.app |
| `.config/nvim/` | Neovim (Lazy.nvim) |
| `.config/fastfetch/config.jsonc` | Fastfetch |
| `.config/btop/btop.conf` | btop |
| `.config/gh/config.yml` | GitHub CLI |
| `.config/fish/conf.d/` | Fish shell |
| `.config/yt-dlp/config` | yt-dlp |
| `Library/Application Support/Code/User/{settings,keybindings,mcp}.json` | VS Code |
| `.claude/` (`CLAUDE.md`, `settings.json`, statusline, hooks, skill custom) | Claude Code (account personale) |
| `.claude-materia/settings.json`, `.claude-accounts.md` | Claude Code (account lavoro + promemoria) |
| `.codex/config.toml`, `hooks.json` | Codex CLI |
| `Brewfile` | Homebrew (formule, cask, estensioni VS Code, npm/uv/cargo/go globali) |

Aggiornare il Brewfile: `brew bundle dump --force --no-describe --file=~/Brewfile`

## Non tracciato

| File | Motivo |
|---|---|
| `.zshrc.local` | Segreti/variabili locali (caricato da `.zshrc`) |
| `.wakatime.cfg` | API key |
| `.config/stripe/` | Chiavi Stripe |
| `.config/sanity/config.json` | Auth token Sanity |
| `.config/gh/hosts.yml` | OAuth session GitHub |
| `.ssh/` | Chiavi SSH private |
| `.codex/auth.json`, `.claude.json` | Sessioni/auth Codex e Claude |
| `.config/bracket/`, `.config/code-server/` | Service account / password |
| `.zsh_history`, `.viminfo` | Cronologie locali |
