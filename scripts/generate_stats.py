#!/usr/bin/env python3
"""
Enigmuz // self-hosted GitHub stats cards (no third-party Vercel instances).

Runs inside GitHub Actions with the built-in GITHUB_TOKEN and writes:
  dist/stats.svg     — headline numbers
  dist/langs.svg     — top languages across owned public repos
  dist/activity.svg  — daily contributions, last 60 days

Usage (locally):  GITHUB_TOKEN=ghp_xxx python scripts/generate_stats.py --user enigmuz --out dist
"""
import argparse
import json
import os
import urllib.request
from datetime import date

BG, BORDER, TEXT, MUTED = "#0d1117", "#30363d", "#e6edf3", "#7d8590"
G, C = "#39ff14", "#00e5ff"
FONT = "font-family=\"'JetBrains Mono','Fira Code',Consolas,'Courier New',monospace\""

QUERY = """
query($login:String!){
  user(login:$login){
    name login
    followers{totalCount}
    pullRequests{totalCount}
    issues{totalCount}
    repositories(ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC,first:100){
      totalCount
      nodes{ stargazerCount
        languages(first:10,orderBy:{field:SIZE,direction:DESC}){ edges{ size node{name color} } } }
    }
    contributionsCollection{
      totalCommitContributions restrictedContributionsCount
      contributionCalendar{ totalContributions
        weeks{ contributionDays{ date contributionCount } } }
    }
  }
}"""


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "enigmuz-stats"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]


def frame(w, h, title, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{title}">'
            '<style>.in{opacity:0;animation:in .6s ease forwards}@keyframes in{to{opacity:1}}'
            '.grow{transform-box:fill-box;transform-origin:left;animation:grow 1.2s ease-out forwards;transform:scaleX(0)}'
            '@keyframes grow{to{transform:scaleX(1)}}'
            '.draw{stroke-dasharray:3000;stroke-dashoffset:3000;animation:draw 2.4s ease-out forwards}'
            '@keyframes draw{to{stroke-dashoffset:0}}</style>'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="12" fill="{BG}" stroke="{BORDER}"/>'
            f'<text x="24" y="34" {FONT} font-size="15" font-weight="700" fill="{G}">{title}</text>'
            f'{body}</svg>')


def stats_svg(u):
    cc = u["contributionsCollection"]
    stars = sum(r["stargazerCount"] for r in u["repositories"]["nodes"])
    rows = [
        ("Contributions (1y)", cc["contributionCalendar"]["totalContributions"]),
        ("Commits (1y)", cc["totalCommitContributions"] + cc["restrictedContributionsCount"]),
        ("Public repos", u["repositories"]["totalCount"]),
        ("Pull requests", u["pullRequests"]["totalCount"]),
        ("Issues", u["issues"]["totalCount"]),
        ("Stars earned", stars),
    ]
    body = []
    for i, (k, v) in enumerate(rows):
        y = 70 + i * 26
        body.append(f'<g class="in" style="animation-delay:{0.15 * i:.2f}s">'
                    f'<text x="24" y="{y}" {FONT} font-size="13" fill="{C}">❯</text>'
                    f'<text x="42" y="{y}" {FONT} font-size="13" fill="{TEXT}">{k}</text>'
                    f'<text x="290" y="{y}" {FONT} font-size="13" font-weight="700" fill="{G}" '
                    f'text-anchor="end">{v:,}</text></g>')
    total = cc["contributionCalendar"]["totalContributions"]
    # ring
    cx, cy, r = 375, 115, 46
    circ = 2 * 3.14159 * r
    frac = min(1, total / 1000)
    body.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{BORDER}" stroke-width="7"/>'
                f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{G}" stroke-width="7" stroke-linecap="round" '
                f'stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ:.1f}" transform="rotate(-90 {cx} {cy})">'
                f'<animate attributeName="stroke-dashoffset" from="{circ:.1f}" to="{circ * (1 - frac):.1f}" '
                f'dur="1.6s" fill="freeze"/></circle>'
                f'<text x="{cx}" y="{cy + 2}" {FONT} font-size="20" font-weight="800" fill="{TEXT}" '
                f'text-anchor="middle">{total:,}</text>'
                f'<text x="{cx}" y="{cy + 20}" {FONT} font-size="9.5" fill="{MUTED}" text-anchor="middle">'
                f'contribs / yr</text>')
    return frame(460, 230, f"{u['name'] or u['login']} // Telemetry", "".join(body))


def langs_svg(u, top=7):
    agg = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            n = e["node"]["name"]
            agg.setdefault(n, [0, e["node"]["color"] or C])
            agg[n][0] += e["size"]
    items = sorted(agg.items(), key=lambda kv: -kv[1][0])[:top]
    total = sum(v[0] for _, v in items) or 1
    body, x = [], 24
    bw = 412
    body.append(f'<clipPath id="bar"><rect x="24" y="52" width="{bw}" height="10" rx="5"/></clipPath><g clip-path="url(#bar)">')
    for name, (size, col) in items:
        w = bw * size / total
        body.append(f'<rect x="{x:.1f}" y="52" width="{w:.1f}" height="10" fill="{col}" class="grow"/>')
        x += w
    body.append("</g>")
    for i, (name, (size, col)) in enumerate(items):
        cx = 24 + (i % 2) * 210
        y = 90 + (i // 2) * 26
        body.append(f'<g class="in" style="animation-delay:{0.12 * i + 0.4:.2f}s">'
                    f'<circle cx="{cx + 5}" cy="{y - 4}" r="5" fill="{col}"/>'
                    f'<text x="{cx + 16}" y="{y}" {FONT} font-size="12.5" fill="{TEXT}">{name}</text>'
                    f'<text x="{cx + 196}" y="{y}" {FONT} font-size="12" fill="{MUTED}" text-anchor="end">'
                    f'{100 * size / total:.1f}%</text></g>')
    return frame(460, 230, "Language Footprint", "".join(body))


def activity_svg(u, days=60):
    cal = [d for w in u["contributionsCollection"]["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    cal = [d for d in cal if d["date"] <= date.today().isoformat()][-days:]
    W, H = 940, 260
    L, R, T, B = 50, 24, 56, 40
    mx = max([d["contributionCount"] for d in cal] + [1])
    step = (W - L - R) / max(1, len(cal) - 1)
    pts = [(L + i * step, H - B - (H - T - B) * d["contributionCount"] / mx) for i, d in enumerate(cal)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{L},{H - B} " + line + f" {pts[-1][0]:.1f},{H - B}"
    body = ['<defs><linearGradient id="ag" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{G}" stop-opacity=".35"/><stop offset="1" stop-color="{G}" stop-opacity="0"/>'
            '</linearGradient></defs>']
    for k in range(5):
        y = T + (H - T - B) * k / 4
        val = round(mx * (1 - k / 4))
        body.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W - R}" y2="{y:.1f}" stroke="{BORDER}" stroke-dasharray="3 5"/>'
                    f'<text x="{L - 10}" y="{y + 4:.1f}" {FONT} font-size="10" fill="{MUTED}" text-anchor="end">{val}</text>')
    body.append(f'<polygon points="{area}" fill="url(#ag)" class="in" style="animation-delay:1s"/>')
    body.append(f'<polyline points="{line}" fill="none" stroke="{C}" stroke-width="2.2" stroke-linejoin="round" class="draw"/>')
    for i, ((x, y), d) in enumerate(zip(pts, cal)):
        if d["contributionCount"]:
            body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{G}" class="in" '
                        f'style="animation-delay:{0.5 + 1.9 * i / len(pts):.2f}s"><title>{d["date"]}: '
                        f'{d["contributionCount"]}</title></circle>')
        if i % 10 == 0 or i == len(cal) - 1:
            body.append(f'<text x="{x:.1f}" y="{H - B + 20}" {FONT} font-size="10" fill="{MUTED}" '
                        f'text-anchor="middle">{d["date"][5:]}</text>')
    return frame(W, H, f"Contribution Signal // last {len(cal)} days", "".join(body))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.getenv("GITHUB_REPOSITORY_OWNER", "enigmuz"))
    ap.add_argument("--out", default="dist")
    a = ap.parse_args()
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required")
    u = fetch(a.user, token)
    os.makedirs(a.out, exist_ok=True)
    for name, svg in (("stats.svg", stats_svg(u)), ("langs.svg", langs_svg(u)), ("activity.svg", activity_svg(u))):
        with open(os.path.join(a.out, name), "w", encoding="utf-8") as f:
            f.write(svg)
        print("wrote", name)


if __name__ == "__main__":
    main()
