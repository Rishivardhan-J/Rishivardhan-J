"""Builds a Starlight-themed GitHub stats dashboard SVG from the GraphQL API."""
import base64, datetime as dt, html, json, os, sys, urllib.request

USER = os.environ.get("PROFILE_USER", "Rishivardhan-J")
TOKEN = os.environ["GH_TOKEN"]
OUT = sys.argv[1] if len(sys.argv) > 1 else "github-stats.svg"

import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from palette import AC, AC_D, AC_L, SIG, BG, PANEL, TRACK, FONT, GRAD_STOPS, HEAT, RAMP, TEXT, SOFT, DIM, MUTED, tx


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

# ---------- stats panel: star chart + language solar system ----------
import math, random, zlib

RANKS = [("CADET", 0), ("PILOT", 100), ("NAVIGATOR", 300), ("COMMANDER", 1000), ("ADMIRAL", 3000)]  # all-time contributions
rank_i = max(i for i, (_, floor) in enumerate(RANKS) if total_all >= floor)
rank_name, rank_floor = RANKS[rank_i]
if rank_i + 1 < len(RANKS):
    rank_next, rank_ceil = RANKS[rank_i + 1]
    rank_frac = (total_all - rank_floor) / (rank_ceil - rank_floor)
    rank_note = f"{rank_ceil - total_all:,} to {rank_next}"
else:
    rank_frac, rank_note = 1.0, "MAX RANK"

W, H = 1200, 846
SKY_X, SKY_Y, SKY_W, SKY_H = 40, 296, 1120, 220
BAND_T, BAND_H = 318, 150          # stars live in this band; height within it is decorative
SYS_X, SYS_Y = 270, 694            # solar-system centre

d_first = dt.date.fromisoformat(past[0]["date"])
d_last = dt.date.fromisoformat(today)
span = max((d_last - d_first).days, 1)
sx_of = lambda d: SKY_X + 28 + (d - d_first).days / span * (SKY_W - 56)
sy_of = lambda iso, dd: BAND_T + BAND_H * (.5 + .30 * math.sin(dd.toordinal() / 23) + .12 * math.sin(dd.toordinal() / 7)) + ((zlib.crc32(iso.encode()) % 1000) / 1000 - .5) * 28

act = [(dt.date.fromisoformat(d["date"]), d["date"], d["contributionCount"]) for d in past if d["contributionCount"]]
mx = max((c for _, _, c in act), default=1)
slevel = lambda n: 1 if n / mx <= .25 else 2 if n / mx <= .5 else 3 if n / mx <= .75 else 4
STAR_COL = {1: HEAT[2], 2: HEAT[2], 3: HEAT[3], 4: HEAT[4]}
by_month = {}
for d in past:
    by_month[d["date"][:7]] = by_month.get(d["date"][:7], 0) + d["contributionCount"]
months = sorted(by_month)[-12:]
trunc = lambda s, n=18: s if len(s) <= n else s[:n - 1] + "…"

planets = [(n, v) for n, v in top if n != "Other"]
other_v = next((v for n, v in top if n == "Other"), 0)
lang_col = lambda i, n: RAMP[-1] if n == "Other" else RAMP[min(i, len(RAMP) - 2)]
summary = (f'{cal["totalContributions"]} contributions in the last year, rank {rank_name}, '
           f'top languages: {", ".join(n for n, _ in top[:3]) or "none yet"}.')

o = []
a = o.append
a(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">'
  f'<title>GitHub stats for {esc(u["login"])}</title><desc>{esc(summary)}</desc>')
a(f'<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0">{GRAD_STOPS}</linearGradient>'
  f'<radialGradient id="r1"><stop offset="0" stop-color="{AC_D}" stop-opacity=".26"/><stop offset="1" stop-color="{AC_D}" stop-opacity="0"/></radialGradient>'
  f'<radialGradient id="r2"><stop offset="0" stop-color="{AC}" stop-opacity=".16"/><stop offset="1" stop-color="{AC}" stop-opacity="0"/></radialGradient>'
  f'<radialGradient id="sg"><stop offset="0" stop-color="{AC_L}" stop-opacity=".5"/><stop offset="1" stop-color="{AC_L}" stop-opacity="0"/></radialGradient>'
  f'<radialGradient id="sun"><stop offset="0" stop-color="{AC_L}"/><stop offset="1" stop-color="{AC}"/></radialGradient>'
  f'<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath><clipPath id="av"><circle cx="76" cy="66" r="36"/></clipPath>'
  f'<clipPath id="sky"><rect x="{SKY_X}" y="{SKY_Y}" width="{SKY_W}" height="{SKY_H}" rx="14"/></clipPath></defs>')
a(f'<rect width="{W}" height="{H}" rx="18" fill="{BG}"/><g clip-path="url(#card)">'
  f'<circle cx="150" cy="40" r="320" fill="url(#r2)"/><circle cx="1080" cy="800" r="380" fill="url(#r1)"/></g>')
a(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="17" fill="none" stroke="url(#g)" stroke-opacity=".55" stroke-width="2"/>')

# ---- header: mission patch + rank
joined = dt.datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00")).strftime("%b %Y")
a(f'<circle cx="76" cy="66" r="46" fill="none" stroke="{AC}" stroke-opacity=".45" stroke-dasharray="3 6"><animateTransform attributeName="transform" type="rotate" from="0 76 66" to="360 76 66" dur="40s" repeatCount="indefinite"/></circle>'
  f'<circle cx="76" cy="66" r="40" fill="none" stroke="url(#g)" stroke-width="3"/>'
  f'<image x="40" y="30" width="72" height="72" clip-path="url(#av)" xlink:href="data:image/jpeg;base64,{avatar_b64(u["avatarUrl"])}"/>')
a(f'<text x="144" y="62" font-family="{FONT}" font-size="30" font-weight="800" fill="url(#g)">{esc(u["name"] or u["login"])}</text>'
  f'<text x="144" y="90" font-family="{FONT}" font-size="14" fill="{DIM}">@{esc(u["login"])} · joined {joined} · {u["followers"]["totalCount"]:,} followers · {u["following"]["totalCount"]:,} following</text>')
a(f'<text x="1160" y="40" text-anchor="end" font-family="{FONT}" font-size="11" letter-spacing="4" fill="{MUTED}">RANK</text>'
  f'<text x="1160" y="70" text-anchor="end" font-family="{FONT}" font-size="28" font-weight="800" letter-spacing="2" fill="{AC_L}">{rank_name}</text>'
  f'<rect x="900" y="82" width="260" height="6" rx="3" fill="{TRACK}"/><rect x="900" y="82" width="{260*rank_frac:.1f}" height="6" rx="3" fill="{AC}"/>'
  f'<text x="1160" y="108" text-anchor="end" font-family="{FONT}" font-size="11" fill="{DIM}">{rank_note}</text>')

# ---- telemetry: hero tile + five readouts
a(f'<rect x="40" y="130" width="340" height="120" rx="14" fill="{AC}" fill-opacity=".07" stroke="{AC}" stroke-opacity=".45"/>'
  f'<text x="60" y="158" font-family="{FONT}" font-size="10" letter-spacing="2" fill="{DIM}">CONTRIBUTIONS · LAST 12 MONTHS</text>'
  f'<text x="58" y="218" font-family="{FONT}" font-size="{52 if len(f"{cal["totalContributions"]:,}") <= 3 else 40 if len(f"{cal["totalContributions"]:,}") <= 5 else 30}" font-weight="800" fill="{AC}">{cal["totalContributions"]:,}</text>')
mmax = max((by_month[m] for m in months), default=1) or 1
bx0 = 40 + 340 - 18 - (len(months) * 13 - 4)
for i, m in enumerate(months):
    h = max(3, 56 * by_month[m] / mmax)
    a(f'<rect x="{bx0 + i*13}" y="{236-h:.1f}" width="9" height="{h:.1f}" rx="2.5" fill="{AC_L if i == len(months)-1 else AC}" fill-opacity="{1 if i == len(months)-1 else .6}"><title>{m}: {by_month[m]}</title></rect>')
reads = [(u["contributionsCollection"]["totalCommitContributions"], "COMMITS · 1Y"), (u["repositories"]["totalCount"], "REPOSITORIES"),
         (u["pullRequests"]["totalCount"], "PULL REQUESTS"), (stars, "STARS EARNED"), (u["followers"]["totalCount"], "FOLLOWERS")]
for i, (n, label) in enumerate(reads):
    x = 400 + i * 155
    a(f'<rect x="{x}" y="130" width="140" height="120" rx="14" fill="{AC}" fill-opacity=".04" stroke="{AC}" stroke-opacity=".3"/>'
      f'<rect x="{x+16}" y="130" width="28" height="3" rx="1.5" fill="{AC}"/>'
      f'<text x="{x+16}" y="196" font-family="{FONT}" font-size="{36 if len(f"{n:,}") <= 5 else 26 if len(f"{n:,}") <= 7 else 20}" font-weight="800" fill="{AC}">{n:,}</text>'
      f'<text x="{x+16}" y="222" font-family="{FONT}" font-size="10" letter-spacing="1" fill="{DIM}">{label}</text>')

# ---- star chart
a(f'<text x="40" y="284" font-family="{FONT}" font-size="14" letter-spacing="3" fill="{AC}">STAR CHART</text>'
  f'<text x="1160" y="284" text-anchor="end" font-family="{FONT}" font-size="11" letter-spacing="2" fill="{MUTED}">{active} ACTIVE DAYS · LAST 12 MONTHS</text>')
a(f'<rect x="{SKY_X}" y="{SKY_Y}" width="{SKY_W}" height="{SKY_H}" rx="14" fill="{PANEL}" stroke="{AC}" stroke-opacity=".18"/><g clip-path="url(#sky)">')
rng = random.Random(42)
for _ in range(80):
    a(f'<circle cx="{rng.uniform(SKY_X+6, SKY_X+SKY_W-6):.1f}" cy="{rng.uniform(SKY_Y+6, SKY_Y+SKY_H-6):.1f}" r="{rng.choice([.5, .7, 1]):.1f}" fill="{TEXT}" fill-opacity="{rng.uniform(.1, .28):.2f}"/>')
pos = {iso: (sx_of(dd), sy_of(iso, dd)) for dd, iso, _ in act}
for (d1, i1, _), (d2, i2, _) in zip(act, act[1:]):
    if (d2 - d1).days <= 6:
        (x1, y1), (x2, y2) = pos[i1], pos[i2]
        a(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{AC}" stroke-opacity=".38" stroke-width="1"/>')
twinkle = {iso for _, iso, c in sorted(act, key=lambda t: zlib.crc32(t[1].encode())) if slevel(c) >= 2}
twinkle = set(sorted(twinkle, key=lambda i: zlib.crc32(i.encode()))[:25])
for dd, iso, c in act:
    x, y = pos[iso]
    lvl = slevel(c)
    r = 1.8 + 4.2 * math.sqrt(c / mx)
    tw = (f'<animate attributeName="opacity" values="1;.5;1" dur="{2.4 + (zlib.crc32(iso.encode()) % 30) / 10:.1f}s" begin="{(zlib.crc32(iso.encode()) % 40) / 10:.1f}s" repeatCount="indefinite"/>'
          if iso in twinkle else "")
    if lvl == 4:
        R = r * 2.2
        a(f'<g><circle cx="{x:.1f}" cy="{y:.1f}" r="{r*4:.1f}" fill="url(#sg)" fill-opacity=".7"/>'
          f'<path d="M{x:.1f},{y-R:.1f}Q{x:.1f},{y:.1f} {x+R:.1f},{y:.1f}Q{x:.1f},{y:.1f} {x:.1f},{y+R:.1f}Q{x:.1f},{y:.1f} {x-R:.1f},{y:.1f}Q{x:.1f},{y:.1f} {x:.1f},{y-R:.1f}Z" fill="{STAR_COL[4]}">'
          f'<title>{iso}: {c}</title>{tw}</path></g>')
    else:
        a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{STAR_COL[lvl]}"><title>{iso}: {c}</title>{tw}</circle>')
if top_day["contributionCount"]:
    bx, by = pos[top_day["date"]]
    left = bx > SKY_X + SKY_W * .7
    a(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="13" fill="none" stroke="{SIG}" stroke-width="1.2"/>'
      f'<text x="{bx + (-20 if left else 20):.1f}" y="{by+4:.1f}" text-anchor="{"end" if left else "start"}" font-family="{FONT}" font-size="11" font-weight="700" fill="{SIG}" stroke="{PANEL}" stroke-width="3" paint-order="stroke">BEST DAY · {top_day["contributionCount"]} · {top_day["date"]}</text>')
tx_, ty_ = pos.get(today, (sx_of(d_last), BAND_T + BAND_H / 2))
a(f'<circle cx="{tx_:.1f}" cy="{ty_:.1f}" r="9" fill="none" stroke="{SIG}" stroke-width="1.5"><animate attributeName="r" values="7;12;7" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;.2;1" dur="2s" repeatCount="indefinite"/></circle>'
  f'<text x="{tx_+8:.1f}" y="{ty_+26:.1f}" text-anchor="end" font-family="{FONT}" font-size="9" letter-spacing="2" fill="{MUTED}" stroke="{PANEL}" stroke-width="3" paint-order="stroke">TODAY</text>')
if not act:
    a(f'<text x="{SKY_X + SKY_W / 2}" y="{BAND_T + BAND_H / 2}" text-anchor="middle" font-family="{FONT}" font-size="13" letter-spacing="3" fill="{MUTED}">QUIET SKY · NO ACTIVITY IN THE LAST 12 MONTHS</text>')
last_lx = -99
for k in range((d_last - d_first).days + 1):
    day = d_first + dt.timedelta(days=k)
    if day.day == 1:
        x = sx_of(day)
        a(f'<line x1="{x:.1f}" y1="484" x2="{x:.1f}" y2="492" stroke="{AC}" stroke-opacity=".3"/>')
        if x - last_lx >= 56:
            a(f'<text x="{x:.1f}" y="508" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{MUTED}">{day.strftime("%b %y" if day.month == 1 else "%b").upper()}</text>')
            last_lx = x
a('</g>')
a(f'<text x="40" y="538" font-family="{FONT}" font-size="10" fill="{MUTED}">x = date · size = contributions · height is decorative · lines join active days less than a week apart</text>')

# ---- language solar system
a(f'<text x="40" y="574" font-family="{FONT}" font-size="14" letter-spacing="3" fill="{AC}">LANGUAGE ORBITS</text>'
  f'<text x="1160" y="574" text-anchor="end" font-family="{FONT}" font-size="11" letter-spacing="2" fill="{MUTED}">SUN = {u["repositories"]["totalCount"]} REPOSITORIES</text>')
a(f'<circle cx="{SYS_X}" cy="{SYS_Y}" r="70" fill="url(#sg)"/>')
for i in range(len(planets)):
    a(f'<circle cx="{SYS_X}" cy="{SYS_Y}" r="{36 + i*12.5:.1f}" fill="none" stroke="{AC}" stroke-opacity=".14"/>')
if other_v:
    a(f'<circle cx="{SYS_X}" cy="{SYS_Y}" r="106" fill="none" stroke="{RAMP[-1]}" stroke-opacity=".28" stroke-dasharray="1 6"/>')
a(f'<circle cx="{SYS_X}" cy="{SYS_Y}" r="18" fill="url(#sun)"/>')
for i, (n, v) in enumerate(planets):
    r = 36 + i * 12.5
    pr = 4 + 14 * math.sqrt(v / total)
    a0 = (i * 137.5) % 360
    a(f'<g><animateTransform attributeName="transform" type="rotate" from="{a0:.1f} {SYS_X} {SYS_Y}" to="{a0+360:.1f} {SYS_X} {SYS_Y}" dur="{16 + i*9}s" repeatCount="indefinite"/>'
      f'<circle cx="{SYS_X + r:.1f}" cy="{SYS_Y}" r="{pr:.1f}" fill="{lang_col(i, n)}" stroke="{AC_L}" stroke-opacity=".5"><title>{esc(n)}: {100*v/total:.1f}%</title></circle></g>')
    la = math.radians(-100 + i * 34)   # fan the ring numbers out so they don't stack
    a(f'<text x="{SYS_X + r * math.cos(la):.1f}" y="{SYS_Y + r * math.sin(la) + 3:.1f}" text-anchor="middle" font-family="{FONT}" font-size="8" fill="{SOFT}" stroke="{BG}" stroke-width="3" paint-order="stroke">{i+1:02d}</text>')
if other_v:
    belt = "".join(
        f'<circle cx="{SYS_X + (106 + rng.uniform(-3, 3)) * math.cos(k * 2 * math.pi / 40):.1f}" cy="{SYS_Y + (106 + rng.uniform(-3, 3)) * math.sin(k * 2 * math.pi / 40):.1f}" r="{rng.choice([1, 1.4, 1.8]):.1f}" fill="{RAMP[-1]}"/>'
        for k in range(40))
    a(f'<g><animateTransform attributeName="transform" type="rotate" from="0 {SYS_X} {SYS_Y}" to="360 {SYS_X} {SYS_Y}" dur="90s" repeatCount="indefinite"/>{belt}</g>')
a(f'<text x="{SYS_X}" y="{SYS_Y+4}" text-anchor="middle" font-family="{FONT}" font-size="11" font-weight="800" fill="{BG}">{u["repositories"]["totalCount"]}</text>')
if not top:
    a(f'<text x="560" y="{SYS_Y}" font-family="{FONT}" font-size="14" fill="{DIM}">no language data yet</text>')
topv = max((v for _, v in top), default=1)
for i, (n, v) in enumerate(top):
    y = 612 + i * 27
    other = n == "Other"
    a(f'<text x="540" y="{y}" font-family="{FONT}" font-size="11" fill="{MUTED}">{"··" if other else f"{i+1:02d}"}</text>'
      f'<circle cx="582" cy="{y-5}" r="6" fill="{lang_col(i, n)}"/>'
      f'<text x="602" y="{y}" font-family="{FONT}" font-size="15" fill="{TEXT}">{esc(trunc(n))}</text>'
      f'<rect x="860" y="{y-8}" width="200" height="6" rx="3" fill="{TRACK}"/><rect x="860" y="{y-8}" width="{200*v/topv:.1f}" height="6" rx="3" fill="{lang_col(i, n)}"/>'
      f'<text x="1160" y="{y}" text-anchor="end" font-family="{FONT}" font-size="13" fill="{SOFT}">{100*v/total:.1f}%</text>')
a(f'<text x="540" y="806" font-family="{FONT}" font-size="10" fill="{MUTED}">planet size = share of code · orbit order = rank · bars are relative to the top language</text>')

a(f'<line x1="40" y1="820" x2="1160" y2="820" stroke="url(#g)" stroke-opacity=".4"/>'
  f'<text x="600" y="838" text-anchor="middle" font-family="{FONT}" font-size="10" letter-spacing="2" fill="{MUTED}">'
  f'{stars:,} STARS · LIVE FROM THE GITHUB API · UPDATED {dt.datetime.now(dt.timezone.utc).strftime("%d %b %Y %H:%M UTC").upper()}</text>')
a('</svg>')
open(OUT, "w").write("".join(o))
print("wrote", OUT, len("".join(o)) // 1024, "KB")

# data for the Orbit Log panel (build_closing.py): week start dates + daily counts
orbit = {"weeks": [{"start": w["contributionDays"][0]["date"], "counts": [d["contributionCount"] for d in w["contributionDays"]]}
                   for w in cal["weeks"] if w["contributionDays"]],
         "total": cal["totalContributions"], "active": active}
open(os.path.join(os.path.dirname(OUT) or ".", "orbit-data.json"), "w").write(json.dumps(orbit))


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
