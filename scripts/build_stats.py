"""Builds a Starlight-themed GitHub stats dashboard SVG from the GraphQL API."""
import base64, datetime as dt, html, json, os, sys, urllib.request

USER = os.environ.get("PROFILE_USER", "Rishivardhan-J")
TOKEN = os.environ["GH_TOKEN"]
OUT = sys.argv[1] if len(sys.argv) > 1 else "github-stats.svg"

import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from palette import AC, AC_D, AC_L, SIG, BG, TRACK, FONT, GRAD_STOPS, HEAT, RAMP, TEXT, SOFT, DIM, MUTED, tx

LANG_COLORS = RAMP  # ordered by rank; "Other" is neutral

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
a(f'<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0">{GRAD_STOPS}</linearGradient>'
  f'<radialGradient id="r1"><stop offset="0" stop-color="{AC_D}" stop-opacity=".30"/><stop offset="1" stop-color="{AC_D}" stop-opacity="0"/></radialGradient>'
  f'<radialGradient id="r2"><stop offset="0" stop-color="{AC}" stop-opacity=".22"/><stop offset="1" stop-color="{AC}" stop-opacity="0"/></radialGradient>'
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
a(f'<text x="128" y="90" font-family="{FONT}" font-size="14" fill="{DIM}">@{esc(u["login"])} · joined {joined} · {u["followers"]["totalCount"]} followers · {u["following"]["totalCount"]} following</text>')
a(f'<text x="1160" y="62" text-anchor="end" font-family="{FONT}" font-size="12" letter-spacing="4" fill="{AC}" opacity=".85">FLIGHT DATA</text>'
  f'<text x="1160" y="82" text-anchor="end" font-family="{FONT}" font-size="12" fill="{MUTED}">live from the GitHub API</text>')

# tiles
tiles = [
    (cal["totalContributions"], "CONTRIBUTIONS · 1Y", AC),
    (u["contributionsCollection"]["totalCommitContributions"], "COMMITS · 1Y", AC),
    (u["repositories"]["totalCount"], "REPOSITORIES", AC),
    (u["pullRequests"]["totalCount"], "PULL REQUESTS", AC),
    (stars, "STARS EARNED", AC),
    (u["followers"]["totalCount"], "FOLLOWERS", AC),
]
tw, gap = 170, 20
for i, (n, label, c) in enumerate(tiles):
    x = 40 + i * (tw + gap)
    a(f'<g>'
      f'<rect x="{x}" y="130" width="{tw}" height="96" rx="14" fill="{c}" fill-opacity=".08" stroke="{c}" stroke-opacity=".6"/>'
      f'<rect x="{x+16}" y="130" width="40" height="3" rx="1.5" fill="{c}"><animate attributeName="width" values="40;110;40" dur="4s" begin="{i*0.4:.1f}s" repeatCount="indefinite"/></rect>'
      f'<text x="{x+16}" y="182" font-family="{FONT}" font-size="36" font-weight="800" fill="{tx(c)}">{n:,}</text>'
      f'<text x="{x+16}" y="206" font-family="{FONT}" font-size="10" letter-spacing="1" fill="{DIM}">{label}</text></g>')

# heatmap
a(f'<text x="40" y="268" font-family="{FONT}" font-size="14" letter-spacing="3" fill="{AC}">CONTRIBUTION GRID</text>')
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
            a(f'<rect x="{cx-2}" y="{cy-2}" width="{cs+4}" height="{cs+4}" rx="5" fill="none" stroke="{SIG}" stroke-width="1.5"><animate attributeName="opacity" values="1;.2;1" dur="2s" repeatCount="indefinite"/></rect>')
        a(f'<rect x="{cx}" y="{cy}" width="{cs}" height="{cs}" rx="3.5" fill="{HEAT[level(d["contributionCount"])]}">'
          f'<title>{d["date"]}: {d["contributionCount"]}</title></rect>')
for i, c in enumerate(HEAT):
    a(f'<rect x="{40 + i*20}" y="424" width="14" height="14" rx="3" fill="{c}"/>')
a(f'<text x="150" y="436" font-family="{FONT}" font-size="11" fill="{MUTED}">less → more</text>')
sx = 1030
a(f'<text x="{sx}" y="300" font-family="{FONT}" font-size="11" letter-spacing="2" fill="{MUTED}">ACTIVE DAYS</text>'
  f'<text x="{sx}" y="330" font-family="{FONT}" font-size="28" font-weight="800" fill="{AC}">{active}</text>'
  f'<text x="{sx}" y="362" font-family="{FONT}" font-size="11" letter-spacing="2" fill="{MUTED}">BEST DAY</text>'
  f'<text x="{sx}" y="392" font-family="{FONT}" font-size="28" font-weight="800" fill="{SIG}">{top_day["contributionCount"]}</text>'
  f'<text x="{sx+50}" y="392" font-family="{FONT}" font-size="11" fill="{MUTED}">{top_day["date"]}</text>')

# languages
a(f'<text x="40" y="474" font-family="{FONT}" font-size="14" letter-spacing="3" fill="{AC}">LANGUAGE ORBITS</text>')
a(f'<g clip-path="url(#bar)"><rect x="40" y="498" width="1120" height="18" fill="{BG}"/>')
x = 40.0
for i, (n, v) in enumerate(top):
    w = 1120 * v / total
    a(f'<rect x="{x:.1f}" y="498" width="{max(w-2,1):.1f}" height="18" fill="{LANG_COLORS[i]}"/>')
    x += w
a('</g>')
for i, (n, v) in enumerate(top):
    cx, cy = 40 + (i % 4) * 285, 556 + (i // 4) * 38
    a(f'<circle cx="{cx+7}" cy="{cy-5}" r="7" fill="{LANG_COLORS[i]}"/>'
      f'<text x="{cx+24}" y="{cy}" font-family="{FONT}" font-size="15" fill="{TEXT}">{esc(n)}</text>'
      f'<text x="{cx+24}" y="{cy+17}" font-family="{FONT}" font-size="12" fill="{MUTED}">{100*v/total:.1f}%</text>')

a(f'<line x1="40" y1="650" x2="1160" y2="650" stroke="url(#g)" stroke-opacity=".4"/>'
  f'<text x="600" y="678" text-anchor="middle" font-family="{FONT}" font-size="11" letter-spacing="2" fill="{MUTED}">'
  f'{stars} STARS · UPDATED {dt.datetime.now(dt.timezone.utc).strftime("%d %b %Y %H:%M UTC").upper()}</text>')
a('</svg>')
open(OUT, "w").write("".join(o))
print("wrote", OUT, len("".join(o)) // 1024, "KB")


# ---------- flight deck HUD ----------
import math
SW, SH = 1200, 360
CX, CYY = 600, 182
today_d = dt.date.today()
mon = lambda d: d - dt.timedelta(days=d.weekday())
WEEKS = 10
R0, RSTEP = 58, 9
dates = {dt.date.fromisoformat(d): c for d, c in hist}

# derived telemetry
last30 = sum(dates.get(today_d - dt.timedelta(days=k), 0) for k in range(30))
prev30 = sum(dates.get(today_d - dt.timedelta(days=k), 0) for k in range(30, 60))
delta = f"{'+' if last30 >= prev30 else '-'}{abs(last30 - prev30)} vs previous 30d"
act90 = sum(1 for k in range(90) if dates.get(today_d - dt.timedelta(days=k), 0))
dow = [0] * 7
for d, c in dates.items():
    dow[d.weekday()] += c
peak = max(range(7), key=lambda i: dow[i])
DN = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
win = [(mon(today_d) - mon(d)).days // 7 for d in dates if 0 <= (mon(today_d) - mon(d)).days // 7 < WEEKS and d <= today_d]
wmax = max((c for d, c in dates.items() if 0 <= (mon(today_d) - mon(d)).days // 7 < WEEKS), default=1) or 1
rng_txt = lambda r: f"{fmt(r[0])} – {fmt(r[1])}" if r else "no streak yet"
prog = min(1.0, cur / best) if best else 0

t = [f'<svg width="{SW}" height="{SH}" viewBox="0 0 {SW} {SH}" xmlns="http://www.w3.org/2000/svg">',
     f'<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{SW}" y2="0">{GRAD_STOPS}</linearGradient>'
     f'<linearGradient id="rg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{AC}"/><stop offset="1" stop-color="{AC_L}"/></linearGradient>'
     f'<radialGradient id="glow"><stop offset="0" stop-color="{AC_D}" stop-opacity=".38"/><stop offset="1" stop-color="{AC_D}" stop-opacity="0"/></radialGradient>'
     f'<linearGradient id="sw" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{AC}" stop-opacity="0"/><stop offset="1" stop-color="{AC}" stop-opacity=".28"/></linearGradient></defs>',
     f'<rect width="{SW}" height="{SH}" rx="18" fill="{BG}"/><circle cx="{CX}" cy="{CYY}" r="200" fill="url(#glow)"/>',
     f'<rect x="1" y="1" width="{SW-2}" height="{SH-2}" rx="17" fill="none" stroke="url(#g)" stroke-opacity=".55" stroke-width="2"/>',
     f'<text x="40" y="40" font-family="{FONT}" font-size="12" letter-spacing="4" fill="{AC}">FLIGHT DECK</text>',
     f'<circle cx="1012" cy="36" r="4" fill="{AC}"><animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></circle>'
     f'<text x="1160" y="40" text-anchor="end" font-family="{FONT}" font-size="12" letter-spacing="3" fill="{AC}">SIGNAL LOCKED</text>']

# --- left instruments
def instrument(y, label, value, vcol, sub, frac=None):
    o = (f'<text x="40" y="{y}" font-family="{FONT}" font-size="11" letter-spacing="3" fill="{MUTED}">{label}</text>'
         f'<text x="40" y="{y+38}" font-family="{FONT}" font-size="38" font-weight="800" fill="{tx(vcol)}">{value}</text>'
         f'<text x="40" y="{y+58}" font-family="{FONT}" font-size="12" fill="{DIM}">{sub}</text>')
    if frac is not None:
        o += (f'<rect x="40" y="{y+68}" width="250" height="6" rx="3" fill="{TRACK}"/>'
              f'<rect x="40" y="{y+68}" width="{250*min(1,frac):.1f}" height="6" rx="3" fill="{vcol}"/>')
    return o
t.append(instrument(78, "TOTAL CONTRIBUTIONS", f"{total_all:,}", AC, f"since {fmt(hist[0][0])}"))
t.append(instrument(172, "LAST 30 DAYS", f"{last30}", AC_D, delta, last30 / max(prev30, last30, 1)))
t.append(instrument(266, "ACTIVE-DAY RATE · 90D", f"{100*act90/90:.0f}%", AC_L, f"{act90} of 90 days with activity", act90 / 90))

# --- radar
for w in range(WEEKS):
    t.append(f'<circle cx="{CX}" cy="{CYY}" r="{R0 + w*RSTEP}" fill="none" stroke="{AC}" stroke-opacity="{.16 if w % 3 == 0 else .07}" {"" if w % 3 == 0 else "stroke-dasharray=\"2 5\""}/>')
rout = R0 + (WEEKS - 1) * RSTEP
for i in range(7):
    a = math.radians(i * 360 / 7 - 90)
    t.append(f'<line x1="{CX+(R0-6)*math.cos(a):.1f}" y1="{CYY+(R0-6)*math.sin(a):.1f}" x2="{CX+rout*math.cos(a):.1f}" y2="{CYY+rout*math.sin(a):.1f}" stroke="{AC}" stroke-opacity=".1"/>'
             f'<text x="{CX+(rout+14)*math.cos(a):.1f}" y="{CYY+(rout+14)*math.sin(a)+4:.1f}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{MUTED}">{DN[i][0]}</text>')
sweep = f'M{CX},{CYY} L{CX+rout},{CYY} A{rout},{rout} 0 0 0 {CX+rout*math.cos(math.radians(-40)):.1f},{CYY+rout*math.sin(math.radians(-40)):.1f} Z'
t.append(f'<g><path d="{sweep}" fill="url(#sw)"/><line x1="{CX}" y1="{CYY}" x2="{CX+rout}" y2="{CYY}" stroke="{AC}" stroke-opacity=".7"/>'
         f'<animateTransform attributeName="transform" type="rotate" from="0 {CX} {CYY}" to="360 {CX} {CYY}" dur="9s" repeatCount="indefinite"/></g>')
for d in sorted(dates):
    w = (mon(today_d) - mon(d)).days // 7
    if not (0 <= w < WEEKS) or d > today_d: continue
    c = dates[d]
    a = math.radians(d.weekday() * 360 / 7 - 90)
    r = R0 + w * RSTEP
    x, y = CX + r * math.cos(a), CYY + r * math.sin(a)
    if c == 0:
        t.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.8" fill="{HEAT[1]}"/>')
    else:
        lvl = 1 + min(3, int(3.99 * c / wmax))
        t.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{3 + 3.5*c/wmax:.1f}" fill="{HEAT[lvl]}"><title>{d}: {c}</title></circle>')
    if d == today_d:
        t.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="none" stroke="{SIG}" stroke-width="1.5"><animate attributeName="r" values="7;12;7" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;.2;1" dur="2s" repeatCount="indefinite"/></circle>')
# hub
circ = 2 * math.pi * 36
t.append(f'<circle cx="{CX}" cy="{CYY}" r="44" fill="{BG}" stroke="{AC}" stroke-opacity=".25"/>'
         f'<circle cx="{CX}" cy="{CYY}" r="36" fill="none" stroke="{TRACK}" stroke-width="7"/>'
         f'<circle cx="{CX}" cy="{CYY}" r="36" fill="none" stroke="url(#rg)" stroke-width="7" stroke-linecap="round" stroke-dasharray="{circ*max(prog,.03):.1f} {circ:.1f}" transform="rotate(-90 {CX} {CYY})"/>'
         f'<text x="{CX}" y="{CYY+9}" text-anchor="middle" font-family="{FONT}" font-size="28" font-weight="800" fill="{TEXT}">{cur}</text>'
         f'<text x="{CX}" y="{CYY+22}" text-anchor="middle" font-family="{FONT}" font-size="8" letter-spacing="2" fill="{AC}">DAYS</text>'
         f'<text x="{CX}" y="{CYY-21}" text-anchor="middle" font-size="12">🔥<animateTransform attributeName="transform" type="translate" values="0 0;0 -2;0 0" dur="1.6s" repeatCount="indefinite"/></text>')
t.append(f'<text x="{CX}" y="{SH-14}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{MUTED}">RADAR · last {WEEKS} weeks · ring = week, spoke = weekday, dot size = activity</text>')

# --- right instruments
RX = 880
t.append(f'<text x="{RX}" y="78" font-family="{FONT}" font-size="11" letter-spacing="3" fill="{MUTED}">WEEKLY RHYTHM · ALL TIME</text>')
bw, gap, base, hmax = 28, 12, 170, 70
mxd = max(dow) or 1
for i, v in enumerate(dow):
    h = max(3, hmax * v / mxd); x = RX + i * (bw + gap)
    col = AC_L if i == peak else AC
    t.append(f'<rect x="{x}" y="{base-hmax}" width="{bw}" height="{hmax}" rx="5" fill="{TRACK}"/>'
             f'<rect x="{x}" y="{base-h:.1f}" width="{bw}" height="{h:.1f}" rx="5" fill="{col}" fill-opacity="{1 if i == peak else .75}"/>'
             f'<text x="{x+bw/2}" y="{base+16}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{MUTED}">{DN[i][:2]}</text>')
t.append(f'<text x="{RX}" y="{base+38}" font-family="{FONT}" font-size="12" fill="{DIM}">peak day: <tspan fill="{AC_L}" font-weight="700">{DN[peak]}</tspan> · {dow[peak]} contributions</text>')
t.append(f'<text x="{RX}" y="262" font-family="{FONT}" font-size="11" letter-spacing="3" fill="{MUTED}">LONGEST STREAK</text>'
         f'<text x="{RX}" y="300" font-family="{FONT}" font-size="38" font-weight="800" fill="{AC_L}">{best}<tspan font-size="14" fill="{DIM}" font-weight="400"> days</tspan></text>'
         f'<text x="{RX}" y="320" font-family="{FONT}" font-size="12" fill="{DIM}">{rng_txt(best_rng)}</text>'
         f'<text x="{RX}" y="346" font-family="{FONT}" font-size="11" letter-spacing="3" fill="{MUTED}">FUEL</text>'
         f'<rect x="{RX+54}" y="339" width="150" height="6" rx="3" fill="{TRACK}"/><rect x="{RX+54}" y="339" width="{150*prog:.1f}" height="6" rx="3" fill="{AC}"/>'
         f'<text x="{RX+280}" y="346" text-anchor="end" font-family="{FONT}" font-size="11" fill="{DIM}">{cur}/{best} days</text>')
t.append('</svg>')
streak_out = sys.argv[2] if len(sys.argv) > 2 else OUT.replace("stats", "streak")
open(streak_out, "w").write("".join(t))
print("wrote", streak_out)
