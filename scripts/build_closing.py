"""Builds orbit-log.svg and transmission.svg (run by CI after build_stats.py).

usage: build_closing.py <snake-raw.svg> <orbit-data.json> <out-dir>
"""
import datetime as dt, html, json, math, os, random, re, sys, urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from palette import AC, AC_D, AC_L, SIG, BG, PANEL, TRACK, TEXT, DIM, MUTED, FONT, GRAD_STOPS, HEAT

SNAKE, DATA, DIST = sys.argv[1:4]
USER = os.environ.get("PROFILE_USER", "Rishivardhan-J")
esc = html.escape
W = 1200


def head(h, title, desc, extra=""):
    return (f'<svg width="{W}" height="{h}" viewBox="0 0 {W} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<title>{esc(title)}</title><desc>{esc(desc)}</desc>'
            f'<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0">{GRAD_STOPS}</linearGradient>'
            f'<radialGradient id="r1"><stop offset="0" stop-color="{AC_D}" stop-opacity=".24"/><stop offset="1" stop-color="{AC_D}" stop-opacity="0"/></radialGradient>'
            f'<clipPath id="card"><rect width="{W}" height="{h}" rx="18"/></clipPath>{extra}</defs>'
            f'<rect width="{W}" height="{h}" rx="18" fill="{BG}"/>')


def frame(h):
    return f'<rect x="1" y="1" width="{W-2}" height="{h-2}" rx="17" fill="none" stroke="url(#g)" stroke-opacity=".55" stroke-width="2"/>'


def dust(rng, n, y0, y1):
    return "".join(
        f'<circle cx="{rng.uniform(10, W-10):.1f}" cy="{rng.uniform(y0, y1):.1f}" r="{rng.choice([.6, .9, 1.2]):.1f}" fill="{TEXT}" fill-opacity="{rng.uniform(.12, .32):.2f}"/>'
        for _ in range(n))


# ------------------------------------------------------------------ orbit log
raw = open(SNAKE, encoding="utf8").read()
data = json.load(open(DATA, encoding="utf8"))
try:
    style = re.search(r"<style>(.*?)</style>", raw, re.S).group(1)
    body = raw[raw.index("</style>") + 8: raw.rindex("</svg>")]
except (AttributeError, ValueError):
    sys.exit("snake svg has an unexpected layout")
style = re.sub(r":root\{[^}]*\}",
               f":root{{--cb:transparent;--cs:{SIG};--ce:{TRACK};--c0:{TRACK};--c1:{HEAT[1]};--c2:{HEAT[2]};--c3:{HEAT[3]};--c4:{HEAT[4]}}}", style, count=1)
style += f".s{{filter:drop-shadow(0 0 3px {SIG})}}"

cells = re.findall(r'<rect class="c[^"]*" x="(\d+)" y="(\d+)"', body)
if not cells:
    sys.exit("snake svg has no grid cells")
cols = max(int(x) for x, _ in cells) // 16 + 1
body, n = re.subn(r'<rect class="(c[^"]*)" x="(\d+)" y="(\d+)" rx="2" ry="2"/>',
                  lambda m: f'<circle class="{m.group(1)}" cx="{int(m.group(2)) + 6}" cy="{int(m.group(3)) + 6}" r="5.4"/>', body)
body = re.sub(r'(<rect class="u u\d+") height="12" (width="[^"]*" x="[^"]*") y="144"', r'\1 height="8" rx="4" ry="4" \2 y="148"', body)

VBW, VBH = cols * 16, 160
GX, GY, GW = 40, 118, 1120   # grid sits low enough that the snake's start (one cell above the grid) clears the month labels
SC = GW / VBW
GH = VBH * SC
H = int(GY + GH + 94)
weeks = data["weeks"]
rng = random.Random(8)

month_totals = {}
for wk in weeks:
    d0 = dt.date.fromisoformat(wk["start"])
    for i, c in enumerate(wk["counts"]):
        d = d0 + dt.timedelta(days=i)
        month_totals[d.strftime("%Y-%m")] = month_totals.get(d.strftime("%Y-%m"), 0) + c
busy = max(month_totals, key=month_totals.get) if data["total"] else None
busy_txt = dt.datetime.strptime(busy, "%Y-%m").strftime("%b %Y").upper() if busy else "NONE YET"

o = [head(H, "Orbit log", f'Contribution grid with an animated comet. {data["active"]} active days, {data["total"]} contributions.'),
     f'<g clip-path="url(#card)"><circle cx="1080" cy="{H}" r="380" fill="url(#r1)"/>{dust(rng, 60, 8, H - 8)}</g>', frame(H)]
o.append(f'<text x="40" y="44" font-family="{FONT}" font-size="14" letter-spacing="3" fill="{AC}">ORBIT LOG</text>'
         f'<text x="40" y="66" font-family="{FONT}" font-size="12" fill="{MUTED}">a comet eats every active day of the past year</text>')
lg = [f'<text x="1160" y="44" text-anchor="end" font-family="{FONT}" font-size="10" letter-spacing="2" fill="{MUTED}">MORE</text>']
for i in range(5):
    lg.append(f'<circle cx="{1114 - (4 - i) * 16}" cy="40" r="5.4" fill="{TRACK if i == 0 else HEAT[i]}"/>')
lg.append(f'<text x="{1114 - 4 * 16 - 14}" y="44" text-anchor="end" font-family="{FONT}" font-size="10" letter-spacing="2" fill="{MUTED}">LESS</text>')
o.append("".join(lg))
if len(weeks) == cols:
    marks, prev = [], None
    for i, wk in enumerate(weeks):
        if wk["start"][:7] != prev:
            prev = wk["start"][:7]
            d = dt.date.fromisoformat(wk["start"])
            marks.append((i, d.strftime("%b %y" if d.month == 1 or i == 0 else "%b").upper()))
    # a partial month at either end can sit one column from its neighbour: drop the label that would collide
    keep = [m for j, m in enumerate(marks) if (j + 1 == len(marks) or marks[j + 1][0] - m[0] >= 4) and m[0] <= cols - 3]
    for i, txt in keep:
        o.append(f'<text x="{GX + (2 + 16 * i) * SC:.1f}" y="92" font-family="{FONT}" font-size="10" fill="{MUTED}">{txt}</text>')
o.append(f'<svg x="{GX}" y="{GY}" width="{GW}" height="{GH:.1f}" viewBox="0 0 {VBW} {VBH}" overflow="visible"><style>{style}</style>{body}</svg>')
cargo_y = GY + 148 * SC + 8 * SC
o.append(f'<text x="40" y="{cargo_y + 24:.0f}" font-family="{FONT}" font-size="10" letter-spacing="2" fill="{MUTED}">CARGO HOLD · DAYS COLLECTED, BY INTENSITY</text>'
         f'<line x1="40" y1="{H - 46}" x2="1160" y2="{H - 46}" stroke="url(#g)" stroke-opacity=".4"/>'
         f'<text x="600" y="{H - 20}" text-anchor="middle" font-family="{FONT}" font-size="11" letter-spacing="2" fill="{MUTED}">'
         f'{data["active"]} ACTIVE DAYS · {data["total"]:,} CONTRIBUTIONS · BUSIEST MONTH {busy_txt}</text></svg>')
open(os.path.join(DIST, "orbit-log.svg"), "w", encoding="utf8").write("".join(o))
print("wrote orbit-log.svg", len("".join(o)) // 1024, "KB,", n, "cells")


# ------------------------------------------------------------------ transmission
def fetch_views():
    if os.environ.get("VIEWS"):
        return int(os.environ["VIEWS"])
    try:
        req = urllib.request.Request(f"https://komarev.com/ghpvc/?username={USER}&label=v", headers={"User-Agent": "profile-stats"})
        return int(re.search(r">(\d[\d,]*)<", urllib.request.urlopen(req, timeout=20).read().decode()).group(1).replace(",", ""))
    except Exception as e:
        print("views fetch failed:", e)
    try:  # fall back to the number in the previously published panel
        req = urllib.request.Request(f"https://raw.githubusercontent.com/{USER}/{USER}/output/transmission.svg", headers={"User-Agent": "profile-stats"})
        return int(re.search(r"views=(\d+)", urllib.request.urlopen(req, timeout=20).read().decode()).group(1))
    except Exception as e:
        print("previous panel unavailable:", e)
        return None


views = fetch_views()
TH = 360
QUOTE = ["A computer is a stupid machine with the", "ability to do incredibly smart things, while", "computer programmers are smart people with",
         "the ability to do incredibly stupid things.", "They are, in short, a perfect match."]
rng = random.Random(14)
fade = (f'<linearGradient id="tr" gradientUnits="userSpaceOnUse" x1="40" y1="0" x2="1160" y2="0"><stop offset="0" stop-color="{AC}" stop-opacity="0"/>'
        f'<stop offset=".2" stop-color="{AC}"/><stop offset=".8" stop-color="{AC}"/><stop offset="1" stop-color="{AC}" stop-opacity="0"/></linearGradient>')
t = [head(TH, "Transmission", f'A quote about computers and programmers. Signals received (profile views): {views if views is not None else "unavailable"}. views={views if views is not None else ""}', fade),
     f'<g clip-path="url(#card)"><circle cx="990" cy="130" r="300" fill="url(#r1)"/>{dust(rng, 55, 8, TH - 8)}</g>', frame(TH)]
t.append(f'<circle cx="46" cy="48" r="4" fill="{AC}"><animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></circle>'
         f'<text x="62" y="52" font-family="{FONT}" font-size="12" letter-spacing="5" fill="{AC}">INCOMING TRANSMISSION</text>'
         f'<text x="30" y="170" font-family="Georgia, serif" font-size="130" fill="{AC_D}" fill-opacity=".45">“</text>')
for i, ln in enumerate(QUOTE):
    t.append(f'<text x="96" y="{112 + i * 34}" font-family="{FONT}" font-size="22" fill="{TEXT}">{esc(ln)}</text>')
t.append(f'<line x1="790" y1="40" x2="790" y2="270" stroke="{AC}" stroke-opacity=".18"/>')
for i in range(3):
    t.append(f'<circle cx="990" cy="130" r="20" fill="none" stroke="{AC}" stroke-width="1.5"><animate attributeName="r" values="20;78" dur="3.6s" begin="{i * 1.2}s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values=".6;0" dur="3.6s" begin="{i * 1.2}s" repeatCount="indefinite"/></circle>')
t.append(f'<circle cx="990" cy="130" r="9" fill="{AC_L}"/><circle cx="990" cy="130" r="20" fill="none" stroke="{AC}" stroke-opacity=".5"/>'
         f'<text x="990" y="252" text-anchor="middle" font-family="{FONT}" font-size="{48 if views is None or len(f"{views:,}") <= 6 else 36}" font-weight="800" fill="{AC}">{f"{views:,}" if views is not None else "—"}</text>'
         f'<text x="990" y="276" text-anchor="middle" font-family="{FONT}" font-size="11" letter-spacing="4" fill="{DIM}">SIGNALS RECEIVED</text>'
         f'<text x="990" y="294" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{MUTED}">profile views · refreshed daily</text>')
pts = " ".join(f"{x},{326 + 13 * math.sin(x / 26) * math.sin(x / 190 + .6):.1f}" for x in range(40, 1161, 8))
t.append(f'<polyline points="{pts}" fill="none" stroke="url(#tr)" stroke-width="2" stroke-linejoin="round"/></svg>')
open(os.path.join(DIST, "transmission.svg"), "w", encoding="utf8").write("".join(t))
print("wrote transmission.svg", len("".join(t)) // 1024, "KB, views =", views)
