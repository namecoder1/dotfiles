# Fast setup della config di tobi su un nuovo Mac

Istruzioni per un agente (Claude Code, Codex, …) a cui viene chiesto di
"ripristinare / fare il setup della mia config" su una macchina nuova.

Repo: https://github.com/namecoder1/dotfiles — **bare repo**, working tree = `$HOME`.
Nessun symlink: i file vivono direttamente al loro posto in `~`.
Il repo è **pubblico**: non committare mai segreti (vedi sotto).

## Regole

- **I comandi li lancia l'utente.** Proponi i comandi in blocchi pronti da
  copiare, spiega cosa fanno, e aspetta l'esito. Esegui tu solo letture
  (ls, cat, plutil -p, brew list, …) a meno che l'utente dica altrimenti.
- Prima di sovrascrivere un file esistente in `~`, fai vedere cosa c'è.
  `install.sh` sposta già i conflitti in `~/.dotfiles-backup/<timestamp>/`.
- Lavora in ordine: un passo alla volta, verifica, poi il successivo.

## 1. Prerequisiti

```bash
xcode-select --install          # git + toolchain
```

## 2. Dotfiles + Homebrew + pacchetti

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/namecoder1/dotfiles/main/install.sh)"
```

Fa: clone bare in `~/.dotfiles` → checkout in `~` (backup dei conflitti) →
`status.showUntrackedFiles no` → installa Homebrew → `brew bundle install`
dal `~/Brewfile` (formule, cask, font, estensioni VS Code, npm/uv/cargo/go globali).

Il Brewfile richiede alcuni prerequisiti per le sezioni non-brew: se
`brew bundle` fallisce su `uv`/`cargo`/`go`/`npm`, installa prima i passi 3
e rilancia `brew bundle install --file=~/Brewfile`.

## 3. Cose NON coperte da install.sh (ma richieste da .zshrc/.zshenv)

```bash
# Powerlevel10k (sourced da ~/.zshrc come ~/powerlevel10k)
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/powerlevel10k

# Rust (~/.zshenv fa source di ~/.cargo/env)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# uv (~/.zshrc fa source di ~/.local/bin/env)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Claude Code
curl -fsSL https://claude.ai/install.sh | bash
```

Opzionali (presenti in .zshrc ma non essenziali): juliaup, Antigravity.
Le righe relative in `.zshrc` falliscono in silenzio o danno un warning se mancano.

Tool uv personali (`placr`, `bolkestein-radar`) arrivano da repo privati
sotto `~/Developer/`: saltali se quei repo non sono ancora clonati.

## 4. Login e segreti (non tracciati — vanno rifatti a mano)

| Cosa | Come |
|---|---|
| GitHub CLI | `gh auth login` |
| Claude Code personale | `claude` → `/login` |
| Claude Code lavoro | `CLAUDE_ACCOUNT=work claude` → `/login` (vedi `~/.claude-accounts.md`) |
| Codex | `codex login` |
| SSH | nuove chiavi o copia sicura di `~/.ssh/` — mai nel repo |
| Segreti shell | creare `~/.zshrc.local` (chmod 600), caricato da `.zshrc` |
| WakaTime, Stripe, Sanity, Vercel | login dai rispettivi tool |

## 5. App con configurazione manuale

- **AeroSpace**: concedi Accessibilità in Impostazioni → Privacy e sicurezza.
  Config in `~/.aerospace.toml`.
- **Ghostty**: config in `~/Library/Application Support/com.mitchellh.ghostty/config.ghostty`
  (font FiraCode Nerd Font, già nel Brewfile).
- **Vorssaint**: Impostazioni → Importa → `~/.config/vorssaint/settings.plist`.
- **herdr**: config + plugin locale in `~/.config/herdr/`. I plugin di terze
  parti (heeler, agent-metrics) vanno reinstallati da herdr.
- **Claude Code plugin**: i marketplace sono in `~/.claude/settings.json`
  (`extraKnownMarketplaces`); si scaricano al primo avvio.
- **Raycast**: non tracciato, usare l'export/import nativo o Raycast Cloud Sync.

## 6. Verifica finale

```bash
dotfiles status          # deve essere pulito
brew bundle check --file=~/Brewfile
exec zsh                 # prompt p10k senza errori
```

## Manutenzione (sulla macchina principale)

```bash
brew bundle dump --force --no-describe --file=~/Brewfile
dotfiles status
dotfiles add <file> && dotfiles commit -m "..." && dotfiles push
```

Prima di ogni commit: `dotfiles diff --cached | gitleaks stdin` (deve dire
"no leaks found"). Nuovi segreti → `~/.zshrc.local` o `.gitignore`.
