#!/usr/bin/env python3
"""Claude 5h / 7d usage line for herdr's tab bar (ui.tab_bar_right command entry).

Prints instantly from a cache and refreshes it in the background via the
quota-axi collector bundled with the herdr-quota plugin.
"""
import glob
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

CACHE_DIR = os.path.expanduser("~/.cache/herdr-tobi")
MAX_AGE = 60  # seconds between refreshes (per profile)
FIVE_H, SEVEN_D = 5 * 3600, 7 * 86400
HOME = os.path.expanduser("~")
HERDR = os.environ.get("HERDR_BIN_PATH") or "herdr"

# profile name -> (label, CLAUDE_CONFIG_DIR or None for the default account)
PROFILES = {
    "personal": ("Personale", None),
    "materia": ("Materia", os.path.join(HOME, ".claude-materia")),
}
MATERIA_DIR = os.path.join(HOME, "Developer", "materia")


def cache_path(profile):
    return os.path.join(CACHE_DIR, f"claude-usage-{profile}.json")


def profile_from_config_dir(cfg):
    if not cfg:
        return "personal"
    cfg = os.path.realpath(os.path.expanduser(cfg))
    for name, (_, d) in PROFILES.items():
        if d and os.path.realpath(d) == cfg:
            return name
    return "personal"


def claude_env_config_dir(pid):
    """CLAUDE_CONFIG_DIR of a running process ('' if unset, None if unreadable)."""
    try:
        out = subprocess.run(["ps", "-E", "-ww", "-o", "command=", "-p", str(pid)],
                             capture_output=True, text=True, timeout=2).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    if not out:
        return None
    for tok in out.split():
        if tok.startswith("CLAUDE_CONFIG_DIR="):
            return tok.split("=", 1)[1]
    return ""


def active_profile():
    """Profile of the claude running in the focused pane; else the cwd rule
    used by the claude() function in ~/.zshrc."""
    pane = os.environ.get("HERDR_PANE_ID")
    cwd = os.getcwd()
    if pane:
        try:
            out = subprocess.run([HERDR, "pane", "process-info", "--pane", pane],
                                 capture_output=True, text=True, timeout=2).stdout
            procs = json.loads(out)["result"]["process_info"]["foreground_processes"]
            for p in procs:
                if p.get("argv0") == "claude" or p.get("name") == "claude":
                    cfg = claude_env_config_dir(p["pid"])
                    if cfg is not None:
                        return profile_from_config_dir(cfg)
            cwd = next((p["cwd"] for p in procs if p.get("cwd")), cwd)
        except Exception:
            pass
    if cwd == MATERIA_DIR or cwd.startswith(MATERIA_DIR + os.sep):
        return "materia"
    return "personal"


def quota_axi():
    hits = sorted(glob.glob(os.path.expanduser(
        "~/.config/herdr/plugins/github/herdr-quota-*/node_modules/.bin/quota-axi")))
    return hits[-1] if hits else None


def refresh(profile):
    """Run quota-axi for one profile and atomically replace its cache."""
    cache = cache_path(profile)
    try:
        exe = quota_axi()
        if not exe:
            data = {"error": "quota-axi mancante"}
        else:
            env = dict(os.environ)
            env.pop("CLAUDE_CONFIG_DIR", None)
            cfg = PROFILES[profile][1]
            if cfg:
                env["CLAUDE_CONFIG_DIR"] = cfg
            out = subprocess.run([exe, "--json", "--full", "--provider", "claude"],
                                 capture_output=True, text=True, timeout=30, env=env)
            data = json.loads(out.stdout)
        tmp = cache + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f)
        os.replace(tmp, cache)
    except Exception:
        pass
    finally:
        try:
            os.remove(cache + ".lock")
        except OSError:
            pass


def maybe_spawn_refresh(profile):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache, lock = cache_path(profile), cache_path(profile) + ".lock"
    try:
        age = time.time() - os.path.getmtime(cache)
    except OSError:
        age = 1e9
    if age < MAX_AGE:
        return
    try:  # stale lock (crashed refresh) older than 2 min is ignored
        if time.time() - os.path.getmtime(lock) < 120:
            return
    except OSError:
        pass
    open(lock, "w").close()
    subprocess.Popen([sys.executable, "-I", os.path.abspath(__file__), "--refresh", profile],
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, start_new_session=True)


def bar(pct, cells=5):
    filled = min(cells, max(1 if pct > 0 else 0, round(pct / 100 * cells)))
    return "▰" * filled + "▱" * (cells - filled)


def until(iso):
    try:
        t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return ""
    secs = int((t - datetime.now(timezone.utc)).total_seconds())
    if secs <= 0:
        return ""
    d, rem = divmod(secs, 86400)
    h, m = divmod(rem // 60, 60)
    return f"{d}g{h}h" if d else (f"{h}h{m:02d}" if h else f"{m}m")


def pick(windows, seconds):
    cands = [w for w in windows if w.get("windowSeconds") == seconds
             and isinstance(w.get("percentUsed"), (int, float))]
    # prefer the account-wide window over model-specific ones (opus/sonnet)
    generic = [w for w in cands
               if not any(m in (w.get("id", "") + w.get("label", "")).lower()
                          for m in ("opus", "sonnet", "haiku", "fable"))]
    return (generic or cands or [None])[0]


def render(profile):
    name = f"Claude {PROFILES[profile][0]}"
    try:
        with open(cache_path(profile)) as f:
            data = json.load(f)
    except (OSError, ValueError):
        return f"{name} …"
    if "error" in data:
        return f"{name}: {data['error']}"
    prov = next((p for p in data.get("providers", []) if p.get("provider") == "claude"), None)
    if not prov:
        return f"{name}: n/d"
    state = prov.get("state", {})
    if state.get("reason") == "keychain_access_required":
        return f"{name}: autorizza Portachiavi"
    windows = prov.get("windows") or []
    parts = []
    for label, secs, show_reset in (("5h", FIVE_H, True), ("7d", SEVEN_D, True)):
        w = pick(windows, secs)
        if not w:
            continue
        pct = round(w["percentUsed"])
        reset = until(w.get("resetsAt", "")) if show_reset else ""
        parts.append(f"{label} {bar(pct)}   {pct}%" + (f"  ↻ {reset}" if reset else ""))
    if not parts:
        return f"{name}: {state.get('status', 'n/d')}"
    stale = " (vecchio)" if state.get("stale") else ""
    return f"{name}  " + " · ".join(parts) + stale


if __name__ == "__main__":
    if "--refresh" in sys.argv:
        refresh(sys.argv[sys.argv.index("--refresh") + 1])
    else:
        prof = sys.argv[sys.argv.index("--profile") + 1] if "--profile" in sys.argv else active_profile()
        maybe_spawn_refresh(prof)
        print(render(prof))
