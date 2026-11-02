#!/usr/bin/env python3
"""Publish $pr and $sync tokens for each herdr workspace (Spaces sidebar).

  spaces.py once    -> one pass
  spaces.py daemon  -> detach and loop every INTERVAL seconds (single instance)
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HERDR, run, workspace_repos  # noqa: E402

INTERVAL = 90
SOURCE = "tobi-extras"
TTL_MS = 10 * 60 * 1000  # tokens vanish if the daemon dies
STATE_DIR = os.path.expanduser("~/.cache/herdr-tobi")  # fixed: one daemon, whoever starts it
PIDFILE = os.path.join(STATE_DIR, "spaces.pid")


def pr_token(repo):
    code, out = run(["gh", "pr", "view", "--json",
                     "number,state,isDraft,reviewDecision,statusCheckRollup"], cwd=repo)
    if code != 0 or not out:
        return None
    pr = json.loads(out)
    if pr.get("state") != "OPEN":
        return None
    checks = pr.get("statusCheckRollup") or []
    states = {(c.get("conclusion") or c.get("state") or c.get("status") or "").upper()
              for c in checks}
    if states & {"FAILURE", "ERROR", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED"}:
        ci = "✗"
    elif states & {"PENDING", "IN_PROGRESS", "QUEUED", "EXPECTED", "WAITING", ""} and checks:
        ci = "…"
    elif checks:
        ci = "✓"
    else:
        ci = ""
    review = {"APPROVED": "approvata", "CHANGES_REQUESTED": "modifiche richieste",
              "REVIEW_REQUIRED": "in review"}.get(pr.get("reviewDecision") or "", "")
    parts = [f"PR #{pr['number']}", "bozza" if pr.get("isDraft") else "", ci, review]
    return " ".join(p for p in parts if p)


def sync_token(repo):
    code, out = run(["git", "-C", repo, "rev-list", "--left-right", "--count",
                     "@{upstream}...HEAD"], timeout=5)
    if code != 0 or not out:
        return None
    behind, ahead = (int(x) for x in out.split())
    parts = ([f"↑{ahead}"] if ahead else []) + ([f"↓{behind}"] if behind else [])
    return " ".join(parts) or None


def report(ws, name, value):
    if value:
        run([HERDR, "workspace", "report-metadata", ws, "--source", SOURCE,
             "--token", f"{name}={value}", "--ttl-ms", str(TTL_MS)], timeout=5)
    else:
        run([HERDR, "workspace", "report-metadata", ws, "--source", SOURCE,
             "--clear-token", name], timeout=5)


def once():
    for ws, repo in workspace_repos().items():
        report(ws, "pr", pr_token(repo) if repo else None)
        report(ws, "sync", sync_token(repo) if repo else None)


def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def daemon():
    os.makedirs(STATE_DIR, exist_ok=True)
    try:
        with open(PIDFILE) as f:
            if alive(int(f.read().strip())):
                return  # already running
    except (OSError, ValueError):
        pass
    if os.fork():  # parent returns so the startup hook finishes immediately
        return
    os.setsid()
    if os.fork():
        os._exit(0)
    devnull = os.open(os.devnull, os.O_RDWR)
    for fd in (0, 1, 2):
        os.dup2(devnull, fd)
    with open(PIDFILE, "w") as f:
        f.write(str(os.getpid()))
    failures = 0
    while failures < 3:  # stop once the herdr server is gone
        code, _ = run([HERDR, "workspace", "list"], timeout=5)
        failures = failures + 1 if code != 0 else 0
        if code == 0:
            try:
                once()
            except Exception:
                pass
        time.sleep(INTERVAL)
    os._exit(0)


if __name__ == "__main__":
    {"once": once, "daemon": daemon}.get(sys.argv[1] if len(sys.argv) > 1 else "once", once)()
