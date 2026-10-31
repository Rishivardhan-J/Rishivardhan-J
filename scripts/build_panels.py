"""Builds assets/briefing.svg and assets/milestones.svg (Starlight theme)."""
import html, math, random, re

import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from palette import AC, AC_D, AC_L, SIG, BG, PANEL, TRACK, TEXT, SOFT, DIM, MUTED, FONT, GRAD_STOPS, STAR_PEAK, tx
random.seed(5)
esc = html.escape


def head(w, h, extra=""):
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg"><defs>'
            f'<linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{w}" y2="0">{GRAD_STOPS}</linearGradient>{extra}</defs>'
            f'<rect width="{w}" height="{h}" rx="18" fill="{BG}"/>')


def frame(w, h):
    return f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="17" fill="none" stroke="url(#g)" stroke-opacity=".5" stroke-width="2"/>'


def stars(w, h, n):
    return "".join(
        f'<circle cx="{random.randint(8,w-8)}" cy="{random.randint(8,h-8)}" r="{random.choice([.7,1,1.3])}" fill="{TEXT}"><animate attributeName="opacity" values="0.1;{STAR_PEAK};0.1" dur="{random.uniform(2,5):.1f}s" begin="{random.uniform(0,4):.1f}s" repeatCount="indefinite"/></circle>'
        for _ in range(n))


def colorize(line):
    """Tiny JS tokenizer -> tspans."""
    out = []
    for tok in re.findall(r'"[^"]*"|\b(?:const)\b|\b[A-Za-z_]+(?=:)|\s+|[^\s"A-Za-z_]+|[A-Za-z_]+', line):
        if tok.startswith('"'): c = AC_L
        elif tok == "const": c = DIM
        elif re.fullmatch(r'[A-Za-z_]+', tok) and line[line.index(tok) + len(tok):].startswith(":"): c = AC
        elif tok.strip() == "": c = None
        elif re.fullmatch(r'[A-Za-z_]+', tok): c = TEXT
        else: c = MUTED
        t = esc(tok).replace(" ", "&#160;")
        out.append(f'<tspan fill="{c}">{t}</tspan>' if c else f'<tspan>{t}</tspan>')
    return "".join(out)


# ------------------------------------------------ milestones
# One entry per milestone: add a line here and re-run. kind "finalist" = achievement (gold); "next" = what's in progress (accent).
MILESTONES = [
    dict(kind="finalist", title="TechSprint Hackathon", org="Google Developer Groups", when="2026"),
    dict(kind="finalist", title="AI for Social Impact", org="Startup TN × HCL Foundations", when="2026"),
    dict(kind="next", title="Three missions in orbit", org="Forge · HarvestPro · Transit", when="NOW"),
]
# ------------------------------------------------ briefing
# Editorial constants: keep in sync with the README sections they summarise.
LAUNCHED = ["Galaxy", "TrackIt", "Bench", "Forge", "HarvestPro", "Transit"]
IN_ORBIT = ["Forge", "HarvestPro", "Transit"]
TECH_COUNT = 37   # Navigation Systems tiles (build_stack.py LANES)
W, H = 1200, 566
CH = 14 * .6      # Fira Code advance at 14px, only used to place the cursor
code = [
    'const rishivardhan = {',
    '  callsign: "Rishivardhan J",',
    '  role: "Full Stack & Mobile Developer",',
    '  base: "Tamil Nadu, India",',
    '  orbits: ["Forge", "HarvestPro", "Transit"],',
    '  shipped: ["TrackIt", "Bench", "Galaxy"],',
    '  finalist: ["TechSprint", "Social Impact"],',
    '  charting: ["DevOps", "System Design"],',
    '  motto: "Learn by building.",',
    '};',
]
lab = lambda x, y, t, size=12, ls=4, c=AC, anchor="start": (
    f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" font-size="{size}" letter-spacing="{ls}" fill="{c}">{t}</text>')
b = [head(W, H, f'<radialGradient id="r"><stop offset="0" stop-color="{AC_D}" stop-opacity=".24"/><stop offset="1" stop-color="{AC_D}" stop-opacity="0"/></radialGradient>'),
     f'<circle cx="1000" cy="60" r="300" fill="url(#r)"/>', stars(W, H, 50), frame(W, H)]
b.append(lab(40, 40, "MISSION BRIEFING", 13)
         + lab(1160, 40, "CLEARANCE OPEN · SECTOR TAMIL NADU", 11, 2, MUTED, "end"))
CT, CHT = 64, 316   # card top / height

# --- pilot ID card (x 40-340)
cx = 190
ring = "".join(f'<line x1="{30 * math.cos(a):.1f}" y1="{30 * math.sin(a):.1f}" x2="{39 * math.cos(a):.1f}" y2="{39 * math.sin(a):.1f}" stroke="{AC}" stroke-opacity=".55" stroke-width="2" stroke-linecap="round"/>'
               for a in (k * math.pi / 12 for k in range(24)))
bars, x = [], 70
while x < 300:
    w_ = random.choice([1.5, 1.5, 3, 4.5]); bars.append(f'<rect x="{x}" y="318" width="{w_}" height="16" fill="{AC}" fill-opacity=".45"/>'); x += w_ + random.choice([2, 3, 4])
b.append(f'<rect x="40" y="{CT}" width="300" height="{CHT}" rx="14" fill="{PANEL}" stroke="{AC}" stroke-opacity=".3"/>'
         + lab(64, CT + 30, "// PILOT ID")
         + f'<g transform="translate({cx} 168)"><g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="40s" repeatCount="indefinite"/>{ring}</g>'
           f'<circle r="27" fill="{AC}" fill-opacity=".12" stroke="{AC}" stroke-width="2"/><circle r="22" fill="none" stroke="{AC}" stroke-opacity=".35"/>'
           f'<text y="9" text-anchor="middle" font-family="{FONT}" font-size="24" font-weight="800" fill="{AC_L}">RJ</text></g>'
         + f'<text x="{cx}" y="244" text-anchor="middle" font-family="{FONT}" font-size="18" font-weight="800" fill="{TEXT}">Rishivardhan J</text>'
         + f'<text x="{cx}" y="266" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{DIM}">Full Stack &amp; Mobile Developer</text>'
         + f'<text x="{cx}" y="286" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{MUTED}">Computer Science</text>'
         + f'<line x1="64" y1="302" x2="316" y2="302" stroke="{AC}" stroke-opacity=".25"/>' + "".join(bars)
         + lab(cx, 360, "ID · RJ-2026", 10, 3, MUTED, "middle"))

# --- terminal (x 360-840)
b.append(f'<rect x="360" y="{CT}" width="480" height="{CHT}" rx="14" fill="{PANEL}" stroke="{AC}" stroke-opacity=".3"/>'
         f'<path d="M360 {CT + 14}a14 14 0 0 1 14-14h452a14 14 0 0 1 14 14v26H360z" fill="{TRACK}"/>'
         + "".join(f'<circle cx="{384 + 20 * k}" cy="{CT + 20}" r="6" fill="{MUTED}" fill-opacity=".45"/>' for k in range(3))
         + f'<text x="600" y="{CT + 25}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{MUTED}">~/mission-control — briefing.js</text>')
for i, l in enumerate(code):
    b.append(f'<text x="384" y="{134 + i * 21}" font-family="{FONT}" font-size="14" xml:space="preserve">'
             f'<tspan fill="{MUTED}" fill-opacity=".55">{i+1:>2}&#160;&#160;</tspan>{colorize(l)}</text>')
py = 134 + len(code) * 21 + 4
prompt = "> ready for the next mission"
b.append(f'<text x="384" y="{py}" font-family="{FONT}" font-size="14" fill="{AC}">&gt; <tspan fill="{MUTED}">{prompt[2:]}</tspan></text>'
         f'<rect x="{384 + len(prompt) * CH + 4:.1f}" y="{py - 12}" width="8" height="16" fill="{AC}"><animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/></rect>')

# --- capabilities card (x 860-1160)
st = f'fill="none" stroke="{AC}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
GLYPH = {
    "FULL STACK": f'<path d="M-8,-3L0,-8L8,-3L0,2Z" {st}/><path d="M-8,2L0,7L8,2" {st}/>',
    "MOBILE": f'<rect x="-5" y="-8" width="10" height="16" rx="2" {st}/><path d="M-2,5H2" {st}/>',
    "ML": f'<path d="M-6,-4L6,0L-6,4" {st}/><circle cx="-6" cy="-4" r="2" {st}/><circle cx="-6" cy="4" r="2" {st}/><circle cx="6" cy="0" r="2" {st}/>',
    "DEVOPS": f'<path d="M6,-3A7,7 0 1 0 7,2" {st}/><path d="M7,-7V-3H3" {st}/>',
}
CAPS = [("FULL STACK", "React · Vite · Galaxy"), ("MOBILE", "Flutter apps · Forge"), ("ML", "HarvestPro · Transit"), ("DEVOPS", "CI pipelines · this profile")]
b.append(f'<rect x="860" y="{CT}" width="300" height="{CHT}" rx="14" fill="{AC}" fill-opacity=".05" stroke="{AC}" stroke-opacity=".3"/>'
         + lab(884, CT + 30, "// CAPABILITIES")
         + f'<text x="884" y="{CT + 62}" font-family="{FONT}" font-size="12" fill="{SOFT}">I turn real problems into shipped</text>'
         + f'<text x="884" y="{CT + 80}" font-family="{FONT}" font-size="12" fill="{SOFT}">products, not just tutorials.</text>')
for i, (name, proof) in enumerate(CAPS):
    cy = 168 + i * 52 + 22
    if i: b.append(f'<line x1="884" y1="{cy - 26}" x2="1136" y2="{cy - 26}" stroke="{AC}" stroke-opacity=".15"/>')
    b.append(f'<circle cx="904" cy="{cy}" r="16" fill="{AC}" fill-opacity=".12" stroke="{AC}" stroke-opacity=".6"/><g transform="translate(904 {cy})">{GLYPH[name]}</g>'
             f'<text x="934" y="{cy - 2}" font-family="{FONT}" font-size="12" font-weight="700" letter-spacing="2" fill="{AC}">{name}</text>'
             f'<text x="934" y="{cy + 14}" font-family="{FONT}" font-size="11" fill="{MUTED}">{esc(proof)}</text>')

# --- telemetry strip
n_fin = sum(m["kind"] == "finalist" for m in MILESTONES)
TILES = [(len(LAUNCHED), "MISSIONS LAUNCHED", AC), (n_fin, "FINALIST FINISHES", SIG), (len(IN_ORBIT), "IN ORBIT NOW", AC), (TECH_COUNT, "TECHNOLOGIES", AC)]
for i, (n, t, c) in enumerate(TILES):
    x = 40 + i * 285
    b.append(f'<rect x="{x}" y="400" width="265" height="64" rx="14" fill="{c}" fill-opacity=".06" stroke="{c}" stroke-opacity=".35"/>'
             f'<text x="{x + 24}" y="443" font-family="{FONT}" font-size="30" font-weight="800" fill="{c}">{n}</text>'
             f'<text x="{x + 24 + 62}" y="436" font-family="{FONT}" font-size="11" letter-spacing="2" fill="{DIM}">{t}</text>')

# --- status bar
b.append(f'<rect x="40" y="484" width="1120" height="42" rx="21" fill="{AC}" fill-opacity=".06" stroke="url(#g)" stroke-opacity=".6"/>'
         f'<circle cx="72" cy="505" r="5" fill="{SIG}"><animate attributeName="r" values="4;7;4" dur="2s" repeatCount="indefinite"/></circle>'
         f'<text x="92" y="510" font-family="{FONT}" font-size="14" font-weight="700" fill="{SIG}">OPEN TO WORK</text>'
         f'<text x="1136" y="510" text-anchor="end" font-family="{FONT}" font-size="14" fill="{SOFT}">Internships &amp; Full-time  ·  Tamil Nadu, India  ·  Currently building Forge, HarvestPro &amp; Transit</text>')
b.append('</svg>')
open("assets/briefing.svg", "w").write("".join(b))

# ------------------------------------------------ milestones (layout)
W, H = 1200, 384
CW, GAP, CY0 = 350, 35, 122          # card width, gap, card top
n_fin = sum(m["kind"] == "finalist" for m in MILESTONES)
years = sorted({m["when"] for m in MILESTONES if m["kind"] == "finalist"})
wave = lambda x: 78 + 10 * math.sin((x - 40) / 95)   # the flight path; nodes sit on it
path = "M" + " L".join(f"{x},{wave(x):.1f}" for x in range(40, 1161, 8))


def medal(cx, cy, c, kind, i):
    ring = (f'<g transform="translate({cx} {cy})"><g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="{36 + i * 6}s" repeatCount="indefinite"/>'
            + "".join(f'<line x1="{30 * math.cos(a):.1f}" y1="{30 * math.sin(a):.1f}" x2="{39 * math.cos(a):.1f}" y2="{39 * math.sin(a):.1f}" stroke="{c}" stroke-opacity=".55" stroke-width="2" stroke-linecap="round"/>'
                      for a in (k * math.pi / 6 for k in range(12))) + '</g>'
            f'<circle r="27" fill="{c}" fill-opacity=".12" stroke="{c}" stroke-width="2"/><circle r="22" fill="none" stroke="{c}" stroke-opacity=".35"/>')
    st = f'fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "finalist":   # trophy
        ring += (f'<path d="M-10,-13H10V-3C10,3 5,7 0,7C-5,7 -10,3 -10,-3Z" {st}/><path d="M-10,-10H-15C-15,-3 -12,-1 -10,-1M10,-10H15C15,-3 12,-1 10,-1" {st}/>'
                 f'<path d="M0,7V12M-6,13H6" {st}/>')
    else:                    # rocket
        ring += (f'<path d="M0,-15C6,-8 6,4 4,10H-4C-6,4 -6,-8 0,-15Z" {st}/><circle cy="-4" r="2.2" {st}/><path d="M-4,6L-9,12L-4,10M4,6L9,12L4,10M-2,12Q0,18 2,12" {st}/>')
    return ring + "</g>"


b = [head(W, H, f'<radialGradient id="r"><stop offset="0" stop-color="{SIG}" stop-opacity=".10"/><stop offset="1" stop-color="{SIG}" stop-opacity="0"/></radialGradient>'),
     f'<circle cx="400" cy="40" r="320" fill="url(#r)"/>', stars(W, H, 35), frame(W, H)]
b.append(f'<text x="40" y="40" font-family="{FONT}" font-size="13" letter-spacing="4" fill="{AC}">MILESTONES</text>'
         f'<text x="1160" y="40" text-anchor="end" font-family="{FONT}" font-size="11" letter-spacing="2" fill="{MUTED}">{n_fin} FINALIST FINISHES · {" · ".join(years)}</text>'
         f'<path d="{path}" fill="none" stroke="url(#g)" stroke-width="2.5" stroke-opacity=".75"/>'
         f'<circle r="5" fill="{TEXT}"><animateMotion dur="9s" repeatCount="indefinite" path="{path}"/></circle>')
for i, m in enumerate(MILESTONES):
    gold = m["kind"] == "finalist"
    c = SIG if gold else AC
    x = 40 + i * (CW + GAP)
    cx = x + CW / 2
    ny = wave(cx)
    dash = "" if gold else ' stroke-dasharray="6 6"'
    tag = "FINALIST" if gold else "NEXT"
    b.append(f'<circle cx="{cx}" cy="{ny:.1f}" r="11" fill="{BG}" stroke="{c}" stroke-width="3"/><circle cx="{cx}" cy="{ny:.1f}" r="4" fill="{c}"><animate attributeName="opacity" values="1;.3;1" dur="2.4s" begin="{i * .6}s" repeatCount="indefinite"/></circle>'
             f'<line x1="{cx}" y1="{ny + 12:.1f}" x2="{cx}" y2="{CY0}" stroke="{c}" stroke-opacity=".6"/>'
             f'<rect x="{x}" y="{CY0}" width="{CW}" height="232" rx="16" fill="{c}" fill-opacity=".06" stroke="{c}" stroke-opacity=".6"{dash}/>'
             f'{medal(x + 74, CY0 + 76, c, m["kind"], i)}'
             f'<path d="M{x + CW - 112},{CY0}h82v44l-41,-13l-41,13Z" fill="{c}"/>'
             f'<text x="{x + CW - 71}" y="{CY0 + 24}" text-anchor="middle" font-family="{FONT}" font-size="11" font-weight="800" letter-spacing="1" fill="{BG}">{tag}</text>'
             f'<line x1="{x + 30}" y1="{CY0 + 142}" x2="{x + CW - 30}" y2="{CY0 + 142}" stroke="{c}" stroke-opacity=".25"/>'
             f'<text x="{x + 30}" y="{CY0 + 176}" font-family="{FONT}" font-size="19" font-weight="800" fill="{TEXT}">{esc(m["title"])}</text>'
             f'<text x="{x + 30}" y="{CY0 + 200}" font-family="{FONT}" font-size="14" fill="{DIM}">{esc(m["org"])}</text>'
             f'<text x="{x + 30}" y="{CY0 + 220}" font-family="{FONT}" font-size="13" letter-spacing="3" fill="{c}">{m["when"]}</text>')
b.append('</svg>')
open("assets/milestones.svg", "w").write("".join(b))
print("ok")
