#!/usr/bin/env python3
"""Ctrl+click on a GitHub PR URL -> new herdr tab running a Claude review.

The tab opens in the workspace whose repo matches the PR (falls back to the
current workspace). Claude is asked to review only, without editing files.
"""
import json
import os
import re
import shlex
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import herdr_json, remote_slug, run, HERDR, workspace_repos  # noqa: E402


def clicked_url():
    url = os.environ.get("HERDR_PLUGIN_CLICKED_URL")
    if not url:
        try:
            url = json.loads(os.environ.get("HERDR_PLUGIN_CONTEXT_JSON", "{}")).get("clicked_url")
        except ValueError:
            url = None
    return url or (sys.argv[1] if len(sys.argv) > 1 else None)


def main():
    url = clicked_url()
    m = re.match(r"^https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", url or "")
    if not m:
        print(f"URL non riconosciuto: {url}", file=sys.stderr)
        return 1
    slug, number = f"{m[1]}/{m[2]}".lower(), m[3]
    pr_url = f"https://github.com/{m[1]}/{m[2]}/pull/{number}"

    ws, cwd = os.environ.get("HERDR_WORKSPACE_ID"), os.path.expanduser("~")
    for w, repo in workspace_repos().items():
        if repo and remote_slug(repo) == slug:
            ws, cwd = w, repo
            break

    args = ["tab", "create", "--cwd", cwd, "--label", f"PR #{number}", "--focus"]
    if ws:
        args[2:2] = ["--workspace", ws]
    res = herdr_json(*args)
    pane = (res or {}).get("root_pane", {}).get("pane_id")
    if not pane:
        print("Impossibile creare la tab", file=sys.stderr)
        return 1

    prompt = (f"Fai la code review della PR {pr_url}. Usa `gh pr view` e `gh pr diff` "
              "per leggerla. Elenca bug, rischi e miglioramenti in ordine di gravità, "
              "con file:riga. Non modificare file e non pubblicare commenti sulla PR.")
    run([HERDR, "pane", "run", pane, f"claude {shlex.quote(prompt)}"], timeout=10)
    return 0


if __name__ == "__main__":
    sys.exit(main())
