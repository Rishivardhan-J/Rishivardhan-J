"""Builds an aurora-themed GitHub stats dashboard SVG from the GraphQL API."""
import base64, datetime as dt, html, json, os, sys, urllib.request

USER = os.environ.get("PROFILE_USER", "Rishivardhan-J")
TOKEN = os.environ["GH_TOKEN"]
OUT = sys.argv[1] if len(sys.argv) > 1 else "github-stats.svg"

CY, VI, PK, AM, BG = "#22D3EE", "#8B5CF6", "#F472B6", "#FBBF24", "#070A1A"
FONT = "Fira Code, Consolas, monospace"
HEAT = ["#121A33", "#0e7490", CY, VI, PK]
LANG_COLORS = [CY, VI, PK, AM, "#34D399", "#60A5FA", "#64748B"]

QUERY = """
query($login:String!){ user(login:$login){
  name login avatarUrl createdAt
  followers{totalCount} following{totalCount}
  pullRequests{totalCount} issues{totalCount}
  repositories(ownerAffiliations:OWNER,isFork:false,first:100){
    totalCount
    nodes{ stargazerCount languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}} } }
  contributionsCollection{
    totalCommitContributions
    contributionCalendar{ totalContributions weeks{ contributionDays{ date weekday contributionCount } } } }
}}"""


def gql():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "User-Agent": "profile-stats"},
    )
    data = json.load(urllib.request.urlopen(req))
    if "errors" in data:
        sys.exit(str(data["errors"]))
    return data["data"]["user"]


def avatar_b64(url):
    req = urllib.request.Request(url + "&s=140", headers={"User-Agent": "profile-stats"})
    return base64.b64encode(urllib.request.urlopen(req).read()).decode()


def esc(s):
    return html.escape(str(s))


u = gql()
cal = u["contributionsCollection"]["contributionCalendar"]
days = [d for w in cal["weeks"] for d in w["contributionDays"]]
today = dt.date.today().isoformat()
past = [d for d in days if d["date"] <= today]

cur = best = run = 0
for d in past:
    run = run + 1 if d["contributionCount"] else 0
    best = max(best, run)
cur = 0
for d in reversed(past):
    if d["contributionCount"]:
        cur += 1
    elif d["date"] != today:
        break
active = sum(1 for d in past if d["contributionCount"])
top_day = max(past, key=lambda d: d["contributionCount"])

repos = u["repositories"]["nodes"]
stars = sum(r["stargazerCount"] for r in repos)
lang = {}
for r in repos:
    for e in r["languages"]["edges"]:
        lang[e["node"]["name"]] = lang.get(e["node"]["name"], 0) + e["size"]
total = sum(lang.values()) or 1
ranked = sorted(lang.items(), key=lambda kv: -kv[1])
top = ranked[:6]
other = sum(v for _, v in ranked[6:])
if other:
    top.append(("Other", other))

W, H = 1200, 700
o = []
a = o.append
a(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">')
a(f'<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0"><stop offset="0" stop-color="{CY}"/><stop offset=".55" stop-color="{VI}"/><stop offset="1" stop-color="{PK}"/></linearGradient>'
  f'<radialGradient id="r1"><stop offset="0" stop-color="{VI}" stop-opacity=".30"/><stop offset="1" stop-color="{VI}" stop-opacity="0"/></radialGradient>'
  f'<radialGradient id="r2"><stop offset="0" stop-color="{CY}" stop-opacity=".22"/><stop offset="1" stop-color="{CY}" stop-opacity="0"/></radialGradient>'
  f'<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath><clipPath id="av"><circle cx="76" cy="66" r="36"/></clipPath>'
  f'<clipPath id="bar"><rect x="40" y="498" width="1120" height="18" rx="9"/></clipPath></defs>')
a(f'<rect width="{W}" height="{H}" rx="18" fill="{BG}"/><g clip-path="url(#card)">'
  f'<circle cx="150" cy="40" r="320" fill="url(#r2)"/><circle cx="1080" cy="640" r="380" fill="url(#r1)"/></g>')
a(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="17" fill="none" stroke="url(#g)" stroke-opacity=".55" stroke-width="2"/>')

# header
a(f'<circle cx="76" cy="66" r="40" fill="none" stroke="url(#g)" stroke-width="3"/>'
  f'<image x="40" y="30" width="72" height="72" clip-path="url(#av)" xlink:href="data:image/jpeg;base64,{avatar_b64(u["avatarUrl"])}"/>')
joined = dt.datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00")).strftime("%b %Y")
a(f'<text x="128" y="62" font-family="{FONT}" font-size="30" font-weight="800" fill="url(#g)">{esc(u["name"] or u["login"])}</text>')
a(f'<text x="128" y="90" font-family="{FONT}" font-size="14" fill="#94A3B8">@{esc(u["login"])} · joined {joined} · {u["followers"]["totalCount"]} followers · {u["following"]["totalCount"]} following</text>')
a(f'<text x="1160" y="62" text-anchor="end" font-family="{FONT}" font-size="12" letter-spacing="4" fill="{CY}" opacity=".85">FLIGHT DATA</text>'
  f'<text x="1160" y="82" text-anchor="end" font-family="{FONT}" font-size="12" fill="#64748B">live from the GitHub API</text>')

# tiles
tiles = [
    (cal["totalContributions"], "CONTRIBUTIONS · 1Y", CY),
    (u["contributionsCollection"]["totalCommitContributions"], "COMMITS · 1Y", VI),
    (u["repositories"]["totalCount"], "REPOSITORIES", PK),
    (u["pullRequests"]["totalCount"], "PULL REQUESTS", AM),
    (cur, "CURRENT STREAK (DAYS)", CY),
    (best, "LONGEST STREAK (DAYS)", PK),
]
tw, gap = 170, 20
for i, (n, label, c) in enumerate(tiles):
    x = 40 + i * (tw + gap)
    a(f'<g>'
      f'<rect x="{x}" y="130" width="{tw}" height="96" rx="14" fill="{c}" fill-opacity=".08" stroke="{c}" stroke-opacity=".6"/>'
      f'<rect x="{x+16}" y="130" width="40" height="3" rx="1.5" fill="{c}"><animate attributeName="width" values="40;110;40" dur="4s" begin="{i*0.4:.1f}s" repeatCount="indefinite"/></rect>'
      f'<text x="{x+16}" y="182" font-family="{FONT}" font-size="36" font-weight="800" fill="{c}">{n:,}</text>'
      f'<text x="{x+16}" y="206" font-family="{FONT}" font-size="10" letter-spacing="1" fill="#94A3B8">{label}</text></g>')

# heatmap
a(f'<text x="40" y="268" font-family="{FONT}" font-size="14" letter-spacing="3" fill="{CY}">CONTRIBUTION GRID</text>')
mx = max(d["contributionCount"] for d in past) or 1
def level(n):
    if n == 0: return 0
    r = n / mx
    return 1 if r <= .25 else 2 if r <= .5 else 3 if r <= .75 else 4
x0, y0, cs, cg = 40, 284, 15, 3
for wi, w in enumerate(cal["weeks"]):
    for d in w["contributionDays"]:
        if d["date"] > today: continue
        cx, cy = x0 + wi * (cs + cg), y0 + d["weekday"] * (cs + cg)
        if d["date"] == today:
            a(f'<rect x="{cx-2}" y="{cy-2}" width="{cs+4}" height="{cs+4}" rx="5" fill="none" stroke="{AM}" stroke-width="1.5"><animate attributeName="opacity" values="1;.2;1" dur="2s" repeatCount="indefinite"/></rect>')
        a(f'<rect x="{cx}" y="{cy}" width="{cs}" height="{cs}" rx="3.5" fill="{HEAT[level(d["contributionCount"])]}">'
          f'<title>{d["date"]}: {d["contributionCount"]}</title></rect>')
for i, c in enumerate(HEAT):
    a(f'<rect x="{40 + i*20}" y="424" width="14" height="14" rx="3" fill="{c}"/>')
a(f'<text x="150" y="436" font-family="{FONT}" font-size="11" fill="#64748B">less → more</text>')
sx = 1030
a(f'<text x="{sx}" y="300" font-family="{FONT}" font-size="11" letter-spacing="2" fill="#64748B">ACTIVE DAYS</text>'
  f'<text x="{sx}" y="330" font-family="{FONT}" font-size="28" font-weight="800" fill="{CY}">{active}</text>'
  f'<text x="{sx}" y="362" font-family="{FONT}" font-size="11" letter-spacing="2" fill="#64748B">BEST DAY</text>'
  f'<text x="{sx}" y="392" font-family="{FONT}" font-size="28" font-weight="800" fill="{PK}">{top_day["contributionCount"]}</text>'
  f'<text x="{sx+50}" y="392" font-family="{FONT}" font-size="11" fill="#64748B">{top_day["date"]}</text>')

# languages
a(f'<text x="40" y="474" font-family="{FONT}" font-size="14" letter-spacing="3" fill="{CY}">LANGUAGE ORBITS</text>')
a('<g clip-path="url(#bar)"><rect x="40" y="498" width="1120" height="18" fill="#121A33"/>')
x = 40.0
for i, (n, v) in enumerate(top):
    w = 1120 * v / total
    a(f'<rect x="{x:.1f}" y="498" width="{w:.1f}" height="18" fill="{LANG_COLORS[i]}"/>')
    x += w
a('</g>')
for i, (n, v) in enumerate(top):
    cx, cy = 40 + (i % 4) * 285, 556 + (i // 4) * 38
    a(f'<circle cx="{cx+7}" cy="{cy-5}" r="7" fill="{LANG_COLORS[i]}"/>'
      f'<text x="{cx+24}" y="{cy}" font-family="{FONT}" font-size="15" fill="#E2E8F0">{esc(n)}</text>'
      f'<text x="{cx+24}" y="{cy+17}" font-family="{FONT}" font-size="12" fill="#64748B">{100*v/total:.1f}%</text>')

a(f'<line x1="40" y1="650" x2="1160" y2="650" stroke="url(#g)" stroke-opacity=".4"/>'
  f'<text x="600" y="678" text-anchor="middle" font-family="{FONT}" font-size="11" letter-spacing="2" fill="#64748B">'
  f'{stars} STARS · UPDATED {dt.datetime.now(dt.timezone.utc).strftime("%d %b %Y %H:%M UTC").upper()}</text>')
a('</svg>')
open(OUT, "w").write("".join(o))
print("wrote", OUT, len("".join(o)) // 1024, "KB")
