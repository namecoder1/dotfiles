"""Shared helpers for the tobi-extras herdr plugin."""
import json
import os
import subprocess
from collections import Counter

HERDR = os.environ.get("HERDR_BIN_PATH") or "herdr"


def run(cmd, cwd=None, timeout=20):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""


def herdr_json(*args):
    code, out = run([HERDR, *args])
    if code != 0 or not out:
        return None
    try:
        return json.loads(out).get("result")
    except ValueError:
        return None


def git_root(path):
    code, out = run(["git", "-C", path, "rev-parse", "--show-toplevel"], timeout=5)
    return out if code == 0 and out else None


def workspace_repos():
    """Map workspace_id -> git toplevel of the cwd most used by its panes."""
    res = herdr_json("pane", "list") or {}
    cwds = {}
    for p in res.get("panes", []):
        cwd = p.get("foreground_cwd") or p.get("cwd")
        if cwd:
            cwds.setdefault(p["workspace_id"], Counter())[cwd] += 1
    repos = {}
    for ws, counter in cwds.items():
        roots = Counter()
        for cwd, n in counter.items():
            root = git_root(cwd)
            if root:
                roots[root] += n
        repos[ws] = roots.most_common(1)[0][0] if roots else None
    return repos


def remote_slug(repo):
    """owner/name of the origin remote, lowercased (github only)."""
    code, url = run(["git", "-C", repo, "remote", "get-url", "origin"], timeout=5)
    if code != 0 or "github.com" not in url:
        return None
    slug = url.split("github.com", 1)[1].lstrip(":/")
    return slug.removesuffix(".git").lower()
