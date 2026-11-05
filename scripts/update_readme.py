"""Refresh the live sections of README.md from the public GitHub API.

Sections are delimited by HTML comment markers:
    <!--START_SECTION:recent-->  ...  <!--END_SECTION:recent-->
    <!--START_SECTION:repos-->   ...  <!--END_SECTION:repos-->
Only the standard library is used, so the workflow needs no installs.
"""
import json
import os
import re
import urllib.request
from datetime import datetime, timezone

USER = os.environ.get("GH_USER", "Nishanth-nishu")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
README = os.path.join(os.path.dirname(__file__), "..", "README.md")


def api(path):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-readme-updater"},
    )
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def ago(iso):
    then = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    s = int((datetime.now(timezone.utc) - then).total_seconds())
    for size, name in ((86400 * 30, "mo"), (86400, "d"), (3600, "h"), (60, "m")):
        if s >= size:
            return f"{s // size}{name} ago"
    return "just now"


def esc(text):
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


def recent_activity():
    events = api(f"/users/{USER}/events/public?per_page=100")
    lines, seen = [], set()
    for e in events:
        repo = e["repo"]["name"]
        url = f"https://github.com/{repo}"
        kind, p = e["type"], e["payload"]
        if kind == "PushEvent":
            commits = p.get("commits") or []
            if not commits:
                continue
            msg = esc(commits[-1]["message"].splitlines()[0])[:70]
            n = p.get("size", len(commits))
            text = f"⬆️ Pushed {n} commit{'s' if n != 1 else ''} to [{repo}]({url}) — {msg}"
        elif kind == "PullRequestEvent" and p.get("action") in ("opened", "closed"):
            pr = p["pull_request"]
            verb = "Merged" if pr.get("merged") else p["action"].capitalize()
            purl = f"{url}/pull/{pr['number']}"
            text = f"🔀 {verb} PR [#{pr['number']}]({purl}) in [{repo}]({url})" + (f" — {esc(pr.get('title'))[:60]}" if pr.get('title') else "")
        elif kind == "CreateEvent" and p.get("ref_type") == "repository":
            text = f"🆕 Created [{repo}]({url})"
        elif kind == "ReleaseEvent":
            text = f"🏷️ Released [{esc(p['release'].get('tag_name'))}]({url}/releases) of [{repo}]({url})"
        else:
            continue
        key = text.split(" — ")[0]
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"- {text} · <sub>{ago(e['created_at'])}</sub>")
        if len(lines) == 6:
            break
    return "\n".join(lines) or "- Nothing public lately — heads down building. 🛠️"


def recent_repos():
    repos = api(f"/users/{USER}/repos?sort=pushed&per_page=30&type=owner")
    rows = ["| Repository | What it is | Lang | Updated |", "|---|---|---|---|"]
    count = 0
    for r in repos:
        if r["fork"] or r["name"].lower() == USER.lower():
            continue
        desc = esc(r["description"])[:80] or "—"
        rows.append(f"| [**{r['name']}**]({r['html_url']}) | {desc} | {r['language'] or '—'} | {ago(r['pushed_at'])} |")
        count += 1
        if count == 5:
            break
    return "\n".join(rows)


def replace(text, name, body):
    pattern = re.compile(rf"(<!--START_SECTION:{name}-->)(.*?)(<!--END_SECTION:{name}-->)", re.S)
    if not pattern.search(text):
        raise SystemExit(f"marker {name} not found in README.md")
    return pattern.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(3)}", text)


def main():
    with open(README, encoding="utf-8") as f:
        text = f.read()
    text = replace(text, "recent", recent_activity())
    text = replace(text, "repos", recent_repos())
    with open(README, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("README updated")


if __name__ == "__main__":
    main()
