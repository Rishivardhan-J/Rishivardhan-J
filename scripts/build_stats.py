"""Builds an aurora-themed GitHub stats dashboard SVG from the GraphQL API."""
import base64, datetime as dt, html, json, os, sys, urllib.request

USER = os.environ.get("PROFILE_USER", "Rishivardhan-J")
TOKEN = os.environ["GH_TOKEN"]
OUT = sys.argv[1] if len(sys.argv) > 1 else "github-stats.svg"

import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from palette import CY, VI, PK, AM, GR, BL, BG, FONT, HEAT, tx

LANG_COLORS = [CY, VI, PK, AM, GR, BL, "#475569"]  # "Other" is the dimmest

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


def all_days(created):
    """Every contribution day since the account was created (API caps a range at 1 year)."""
    y0, y1 = int(created[:4]), dt.date.today().year
    fields = "".join(
        f'y{y}: contributionsCollection(from:"{y}-01-01T00:00:00Z",to:"{y}-12-31T23:59:59Z")'
        '{contributionCalendar{weeks{contributionDays{date contributionCount}}}} '
        for y in range(y0, y1 + 1))
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": 'query($l:String!){user(login:$l){' + fields + '}}', "variables": {"l": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "User-Agent": "profile-stats"})
    data = json.load(urllib.request.urlopen(req))
    if "errors" in data:
        sys.exit(str(data["errors"]))
    seen = {}
    for blk in data["data"]["user"].values():
        for w in blk["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                seen[d["date"]] = d["contributionCount"]
    return sorted((k, v) for k, v in seen.items() if k <= dt.date.today().isoformat())


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

hist = all_days(u["createdAt"])
fmt = lambda iso: dt.date.fromisoformat(iso).strftime("%b %d, %Y").replace(" 0", " ")
best, run, run_start, best_rng = 0, 0, None, None
for d, c in hist:
    if c:
        if not run: run_start = d
        run += 1
        if run > best: best, best_rng = run, (run_start, d)
    else:
        run = 0
cur, cur_rng = 0, None
for d, c in reversed(hist):
    if c:
        cur += 1; cur_rng = (d, cur_rng[1] if cur_rng else d)
    elif d != today:
        break
total_all = sum(c for _, c in hist)
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
  f'<text x="1160" y="82" text-anchor="end" font-family="{FONT}" font-size="12" fill="#8B9BB4">live from the GitHub API</text>')

# tiles
tiles = [
    (cal["totalContributions"], "CONTRIBUTIONS · 1Y", CY),
    (u["contributionsCollection"]["totalCommitContributions"], "COMMITS · 1Y", VI),
    (u["repositories"]["totalCount"], "REPOSITORIES", PK),
    (u["pullRequests"]["totalCount"], "PULL REQUESTS", AM),
    (stars, "STARS EARNED", CY),
    (u["followers"]["totalCount"], "FOLLOWERS", PK),
]
tw, gap = 170, 20
for i, (n, label, c) in enumerate(tiles):
    x = 40 + i * (tw + gap)
    a(f'<g>'
      f'<rect x="{x}" y="130" width="{tw}" height="96" rx="14" fill="{c}" fill-opacity=".08" stroke="{c}" stroke-opacity=".6"/>'
      f'<rect x="{x+16}" y="130" width="40" height="3" rx="1.5" fill="{c}"><animate attributeName="width" values="40;110;40" dur="4s" begin="{i*0.4:.1f}s" repeatCount="indefinite"/></rect>'
      f'<text x="{x+16}" y="182" font-family="{FONT}" font-size="36" font-weight="800" fill="{tx(c)}">{n:,}</text>'
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
a(f'<text x="150" y="436" font-family="{FONT}" font-size="11" fill="#8B9BB4">less → more</text>')
sx = 1030
a(f'<text x="{sx}" y="300" font-family="{FONT}" font-size="11" letter-spacing="2" fill="#8B9BB4">ACTIVE DAYS</text>'
  f'<text x="{sx}" y="330" font-family="{FONT}" font-size="28" font-weight="800" fill="{CY}">{active}</text>'
  f'<text x="{sx}" y="362" font-family="{FONT}" font-size="11" letter-spacing="2" fill="#8B9BB4">BEST DAY</text>'
  f'<text x="{sx}" y="392" font-family="{FONT}" font-size="28" font-weight="800" fill="{PK}">{top_day["contributionCount"]}</text>'
  f'<text x="{sx+50}" y="392" font-family="{FONT}" font-size="11" fill="#8B9BB4">{top_day["date"]}</text>')

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
      f'<text x="{cx+24}" y="{cy+17}" font-family="{FONT}" font-size="12" fill="#8B9BB4">{100*v/total:.1f}%</text>')

a(f'<line x1="40" y1="650" x2="1160" y2="650" stroke="url(#g)" stroke-opacity=".4"/>'
  f'<text x="600" y="678" text-anchor="middle" font-family="{FONT}" font-size="11" letter-spacing="2" fill="#8B9BB4">'
  f'{stars} STARS · UPDATED {dt.datetime.now(dt.timezone.utc).strftime("%d %b %Y %H:%M UTC").upper()}</text>')
a('</svg>')
open(OUT, "w").write("".join(o))
print("wrote", OUT, len("".join(o)) // 1024, "KB")


# ---------- streak panel ----------
import math
SW, SH = 1200, 240
ring_r = 62
rng_txt = lambda r: f"{fmt(r[0])} – {fmt(r[1])}" if r else "no streak yet"
prog = min(1.0, cur / best) if best else 0
circ = 2 * math.pi * ring_r
t = [f'<svg width="{SW}" height="{SH}" viewBox="0 0 {SW} {SH}" xmlns="http://www.w3.org/2000/svg">',
     f'<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{SW}" y2="0"><stop offset="0" stop-color="{CY}"/><stop offset=".55" stop-color="{VI}"/><stop offset="1" stop-color="{PK}"/></linearGradient>'
     f'<linearGradient id="rg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CY}"/><stop offset="1" stop-color="{PK}"/></linearGradient>'
     f'<radialGradient id="glow"><stop offset="0" stop-color="{VI}" stop-opacity=".4"/><stop offset="1" stop-color="{VI}" stop-opacity="0"/></radialGradient></defs>',
     f'<rect width="{SW}" height="{SH}" rx="18" fill="{BG}"/><circle cx="600" cy="120" r="200" fill="url(#glow)"/>',
     f'<rect x="1" y="1" width="{SW-2}" height="{SH-2}" rx="17" fill="none" stroke="url(#g)" stroke-opacity=".55" stroke-width="2"/>']
def stat(cx, big, label, sub, col):
    return (f'<text x="{cx}" y="112" text-anchor="middle" font-family="{FONT}" font-size="54" font-weight="800" fill="{tx(col)}">{big:,}</text>'
            f'<text x="{cx}" y="146" text-anchor="middle" font-family="{FONT}" font-size="14" letter-spacing="2" fill="#E2E8F0">{label}</text>'
            f'<text x="{cx}" y="170" text-anchor="middle" font-family="{FONT}" font-size="12" fill="#8B9BB4">{sub}</text>')
t.append(stat(190, total_all, "TOTAL CONTRIBUTIONS", f"{fmt(hist[0][0])} – present", CY))
t.append(stat(1010, best, "LONGEST STREAK", rng_txt(best_rng), PK))
t.append(f'<line x1="380" y1="50" x2="380" y2="190" stroke="url(#g)" stroke-opacity=".4"/><line x1="820" y1="50" x2="820" y2="190" stroke="url(#g)" stroke-opacity=".4"/>')
t.append(f'<circle cx="600" cy="108" r="{ring_r}" fill="none" stroke="#121A33" stroke-width="12"/>'
         f'<circle cx="600" cy="108" r="{ring_r}" fill="none" stroke="url(#rg)" stroke-width="12" stroke-linecap="round" stroke-dasharray="{circ*max(prog,0.02):.1f} {circ:.1f}" transform="rotate(-90 600 108)">'
         f'<animate attributeName="stroke-opacity" values="1;.55;1" dur="3s" repeatCount="indefinite"/></circle>'
         f'<circle cx="600" cy="108" r="{ring_r+14}" fill="none" stroke="{CY}" stroke-opacity=".25" stroke-dasharray="2 8"><animateTransform attributeName="transform" type="rotate" from="0 600 108" to="360 600 108" dur="24s" repeatCount="indefinite"/></circle>'
         f'<text x="600" y="126" text-anchor="middle" font-family="{FONT}" font-size="48" font-weight="800" fill="#fff">{cur}</text>'
         f'<text x="600" y="38" text-anchor="middle" font-size="26">🔥<animateTransform attributeName="transform" type="translate" values="0 0;0 -3;0 0" dur="1.6s" repeatCount="indefinite"/></text>'
         f'<text x="600" y="208" text-anchor="middle" font-family="{FONT}" font-size="14" font-weight="700" letter-spacing="2" fill="{CY}">CURRENT STREAK</text>'
         f'<text x="600" y="228" text-anchor="middle" font-family="{FONT}" font-size="12" fill="#8B9BB4">{rng_txt(cur_rng)}</text>')
t.append('</svg>')
streak_out = sys.argv[2] if len(sys.argv) > 2 else OUT.replace("stats", "streak")
open(streak_out, "w").write("".join(t))
print("wrote", streak_out)
