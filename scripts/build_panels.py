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


# ------------------------------------------------ briefing
W, H = 1200, 420
code = [
    'const rishivardhan = {',
    '  callsign: "Rishivardhan J",',
    '  role: "Full Stack & Mobile Developer",',
    '  education: "Computer Science",',
    '  activeOrbits: ["Forge", "HarvestPro",',
    '                 "Transit", "TrackIt", "Bench"],',
    '  charting: ["DevOps", "System Design"],',
    '  motto: "Learn by building.",',
    '};',
]
b = [head(W, H, f'<radialGradient id="r"><stop offset="0" stop-color="{AC_D}" stop-opacity=".24"/><stop offset="1" stop-color="{AC_D}" stop-opacity="0"/></radialGradient>'),
     f'<circle cx="1000" cy="60" r="300" fill="url(#r)"/>', stars(W, H, 40), frame(W, H)]
# terminal
b.append(f'<rect x="40" y="36" width="650" height="300" rx="14" fill="{PANEL}" stroke="{AC}" stroke-opacity=".3"/>'
         f'<path d="M40 50a14 14 0 0 1 14-14h622a14 14 0 0 1 14 14v26H40z" fill="{TRACK}"/>'
         f'<circle cx="64" cy="56" r="6" fill="{MUTED}" fill-opacity=".45"/><circle cx="84" cy="56" r="6" fill="{MUTED}" fill-opacity=".45"/><circle cx="104" cy="56" r="6" fill="{MUTED}" fill-opacity=".45"/>'
         f'<text x="365" y="61" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{MUTED}">~/mission-control — briefing.js</text>')
for i, l in enumerate(code):
    b.append(f'<text x="64" y="{106+i*23}" font-family="{FONT}" font-size="15" xml:space="preserve">'
             f'<tspan fill="{MUTED}" fill-opacity=".55">{i+1:>2}&#160;&#160;</tspan>{colorize(l)}</text>')
b.append(f'<text x="64" y="{106+len(code)*23+6}" font-family="{FONT}" font-size="15" fill="{AC}">&gt; <tspan fill="{MUTED}">ready for the next mission</tspan></text>'
         f'<rect x="{64+9*28+10}" y="{106+len(code)*23-6}" width="9" height="18" fill="{AC}"><animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/></rect>')
# about card
b.append(f'<rect x="720" y="36" width="440" height="300" rx="14" fill="{AC}" fill-opacity=".05" stroke="{AC}" stroke-opacity=".3"/>'
         f'<text x="744" y="72" font-family="{FONT}" font-size="12" letter-spacing="4" fill="{AC}">// ABOUT</text>')
about = ["I'm a Computer Science student who", "turns ideas into working products:", "web apps, mobile apps and ML-backed", "tools.", "", "I pick up problems people actually", "face and ship something that solves", "them, not just tutorials."]
for i, l in enumerate(about):
    b.append(f'<text x="744" y="{104+i*22}" font-family="{FONT}" font-size="14" fill="{TEXT}">{esc(l)}</text>')
chips = [("FULL STACK", AC), ("MOBILE", AC), ("ML", AC), ("DEVOPS", AC)]
x = 744
for t, c in chips:
    w = 22 + len(t) * 9
    b.append(f'<rect x="{x}" y="290" width="{w}" height="28" rx="14" fill="{c}" fill-opacity=".14" stroke="{c}" stroke-opacity=".7"/>'
             f'<text x="{x+w/2}" y="309" text-anchor="middle" font-family="{FONT}" font-size="11" font-weight="700" fill="{tx(c)}">{t}</text>')
    x += w + 8
# status bar
b.append(f'<rect x="40" y="358" width="1120" height="42" rx="21" fill="{AC}" fill-opacity=".06" stroke="url(#g)" stroke-opacity=".6"/>'
         f'<circle cx="72" cy="379" r="5" fill="{SIG}"><animate attributeName="r" values="4;7;4" dur="2s" repeatCount="indefinite"/></circle>'
         f'<text x="92" y="384" font-family="{FONT}" font-size="14" font-weight="700" fill="{SIG}">OPEN TO WORK</text>'
         f'<text x="1136" y="384" text-anchor="end" font-family="{FONT}" font-size="14" fill="{SOFT}">Internships &amp; Full-time  ·  Tamil Nadu, India  ·  Currently building Forge, HarvestPro &amp; Transit</text>')
b.append('</svg>')
open("assets/briefing.svg", "w").write("".join(b))

# ------------------------------------------------ milestones
# One entry per milestone: add a line here and re-run. kind "finalist" = achievement (gold); "next" = what's in progress (accent).
MILESTONES = [
    dict(kind="finalist", title="TechSprint Hackathon", org="Google Developer Groups", when="2026"),
    dict(kind="finalist", title="AI for Social Impact", org="Startup TN × HCL Foundations", when="2026"),
    dict(kind="next", title="Three missions in orbit", org="Forge · HarvestPro · Transit", when="NOW"),
]
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
