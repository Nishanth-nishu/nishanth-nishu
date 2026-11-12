"""Render the stats, top-languages and contribution-graph cards as SVG files.

The public github-readme-stats and github-readme-activity-graph Vercel
instances are shut down, so the cards are generated here from the GitHub
GraphQL API and committed to assets/stats/. Standard library only.
"""
import json
import os
import urllib.request
from datetime import date
from xml.sax.saxutils import escape

USER = os.environ.get("GH_USER", "Nishanth-nishu")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "stats")

BG, TITLE, TEXT, ACCENT, MUTED, GRID = "#000000", "#00ff41", "#9dffb5", "#00ff41", "#3d8f55", "#0f2a17"
FONT = "'Segoe UI', Ubuntu, 'Helvetica Neue', Sans-Serif"

QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    name
    login
    followers { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositoriesContributedTo(contributionTypes: [COMMIT, PULL_REQUEST, ISSUE, REPOSITORY]) { totalCount }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100, after: $cursor) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def gql(variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "User-Agent": "profile-stats-cards"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors"):
        raise SystemExit(f"GraphQL error: {body['errors']}")
    return body["data"]["user"]


def fetch():
    user = gql({"login": USER, "cursor": None})
    repos = user["repositories"]["nodes"]
    page = user["repositories"]["pageInfo"]
    while page["hasNextPage"]:
        more = gql({"login": USER, "cursor": page["endCursor"]})["repositories"]
        repos += more["nodes"]
        page = more["pageInfo"]
    user["repo_nodes"] = repos
    return user


def card(width, height, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" fill="none" role="img">'
        f'<style>text{{font-family:{FONT}}}</style>'
        f'<rect x="0.5" y="0.5" rx="6" width="{width - 1}" height="{height - 1}" fill="{BG}"/>'
        f"{body}</svg>\n"
    )


def stats_svg(u):
    cc = u["contributionsCollection"]
    stars = sum(r["stargazerCount"] for r in u["repo_nodes"])
    rows = [
        ("Total stars earned", stars),
        ("Commits (last 12 months)",
         cc["totalCommitContributions"] + cc["restrictedContributionsCount"]),
        ("Pull requests", u["pullRequests"]["totalCount"]),
        ("Issues", u["issues"]["totalCount"]),
        ("Contributed to (last year)", u["repositoriesContributedTo"]["totalCount"]),
        ("Public repositories", u["repositories"]["totalCount"]),
    ]
    name = escape(u["name"] or u["login"])
    body = f'<text x="25" y="35" fill="{TITLE}" font-size="18" font-weight="600">{name}\'s GitHub Stats</text>'
    for i, (label, value) in enumerate(rows):
        y = 70 + i * 25
        body += (
            f'<circle cx="31" cy="{y - 5}" r="4" fill="{ACCENT}"/>'
            f'<text x="45" y="{y}" fill="{TEXT}" font-size="14">{escape(label)}:</text>'
            f'<text x="300" y="{y}" fill="#ffffff" font-size="14" font-weight="700">{value:,}</text>'
        )
    total = cc["contributionCalendar"]["totalContributions"]
    body += (
        f'<circle cx="410" cy="110" r="45" stroke="{GRID}" stroke-width="6"/>'
        f'<circle cx="410" cy="110" r="45" stroke="{ACCENT}" stroke-width="6" '
        f'stroke-dasharray="283" transform="rotate(-90 410 110)"/>'
        f'<text x="410" y="116" fill="#ffffff" font-size="20" font-weight="700" text-anchor="middle">{total:,}</text>'
        f'<text x="410" y="175" fill="{MUTED}" font-size="11" text-anchor="middle">contributions / year</text>'
    )
    return card(495, 225, body)


def langs_svg(u, top=8):
    sizes, colors = {}, {}
    for r in u["repo_nodes"]:
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            sizes[n] = sizes.get(n, 0) + e["size"]
            colors[n] = e["node"]["color"] or "#888888"
    langs = sorted(sizes.items(), key=lambda kv: kv[1], reverse=True)[:top]
    total = sum(s for _, s in langs) or 1
    body = f'<text x="25" y="35" fill="{TITLE}" font-size="18" font-weight="600">Most Used Languages</text>'
    body += '<mask id="bar"><rect x="25" y="55" width="300" height="8" rx="4" fill="#fff"/></mask><g mask="url(#bar)">'
    x = 25.0
    for name, size in langs:
        w = 300 * size / total
        body += f'<rect x="{x:.2f}" y="55" width="{w + 0.5:.2f}" height="8" fill="{colors[name]}"/>'
        x += w
    body += "</g>"
    for i, (name, size) in enumerate(langs):
        cx, cy = 25 + (i % 2) * 150, 90 + (i // 2) * 25
        body += (
            f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{colors[name]}"/>'
            f'<text x="{cx + 15}" y="{cy}" fill="{TEXT}" font-size="12">{escape(name)} '
            f'<tspan fill="{MUTED}">{100 * size / total:.1f}%</tspan></text>'
        )
    rows = (len(langs) + 1) // 2
    return card(350, max(170, 90 + rows * 25), body)


def activity_svg(u, days=31):
    weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"]
    all_days = [d for w in weeks for d in w["contributionDays"]][-days:]
    counts = [d["contributionCount"] for d in all_days]
    W, H, L, R, T, B = 1000, 320, 60, 30, 60, 50
    pw, ph = W - L - R, H - T - B
    peak = max(max(counts), 1)
    step = max(1, -(-peak // 5))  # ceil(peak / 5)
    top = step * 5
    px = lambda i: L + pw * i / (len(counts) - 1)
    py = lambda c: T + ph - ph * c / top
    pts = [(px(i), py(c)) for i, c in enumerate(counts)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{L},{T + ph} {line} {L + pw},{T + ph}"

    body = (
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{ACCENT}" stop-opacity="0.45"/>'
        f'<stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></linearGradient></defs>'
        f'<text x="{W / 2}" y="35" fill="{TITLE}" font-size="20" font-weight="600" text-anchor="middle">'
        f"Contribution Graph · last {days} days</text>"
    )
    for k in range(6):
        v = step * k
        y = py(v)
        body += (
            f'<line x1="{L}" y1="{y:.1f}" x2="{L + pw}" y2="{y:.1f}" stroke="{GRID}"/>'
            f'<text x="{L - 10}" y="{y + 4:.1f}" fill="{MUTED}" font-size="11" text-anchor="end">{v}</text>'
        )
    for i, d in enumerate(all_days):
        if i % 3 == 0 or i == len(all_days) - 1:
            body += (
                f'<text x="{px(i):.1f}" y="{T + ph + 20}" fill="{MUTED}" font-size="11" '
                f'text-anchor="middle">{int(d["date"][8:])}</text>'
            )
    body += (
        f'<polygon points="{area}" fill="url(#g)"/>'
        f'<polyline points="{line}" stroke="{ACCENT}" stroke-width="2.5" stroke-linejoin="round" fill="none"/>'
    )
    for (x, y), d in zip(pts, all_days):
        body += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="#ffffff"><title>{d["date"]}: {d["contributionCount"]}</title></circle>'
    body += (
        f'<text x="{W / 2}" y="{H - 10}" fill="{MUTED}" font-size="12" text-anchor="middle">'
        f"{escape(all_days[0]['date'])} → {escape(all_days[-1]['date'])} · {sum(counts)} contributions</text>"
    )
    return card(W, H, body)


def main():
    if not TOKEN:
        raise SystemExit("GITHUB_TOKEN is required for the GraphQL API")
    u = fetch()
    os.makedirs(OUT, exist_ok=True)
    for name, svg in (("stats.svg", stats_svg(u)), ("top-langs.svg", langs_svg(u)), ("activity.svg", activity_svg(u))):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(svg)
        print("wrote", name)


if __name__ == "__main__":
    main()
