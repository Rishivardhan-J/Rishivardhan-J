"""Builds assets/briefing.svg and assets/milestones.svg (Starlight theme)."""
import html, random, re

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
W, H = 1200, 330
cards = [
    ("🏆", "FINALIST", SIG, ["TechSprint Hackathon", "Google Developer Groups"], "2026"),
    ("🏆", "FINALIST", SIG, ["AI for Social Impact", "Startup TN × HCL Foundations"], "2026"),
    ("🚀", "NEXT MISSION", AC, ["Three missions in orbit", "Forge · HarvestPro · Transit"], "NOW"),
]
b = [head(W, H, f'<radialGradient id="r"><stop offset="0" stop-color="{SIG}" stop-opacity=".10"/><stop offset="1" stop-color="{SIG}" stop-opacity="0"/></radialGradient>'),
     f'<circle cx="400" cy="40" r="320" fill="url(#r)"/>', stars(W, H, 35), frame(W, H)]
cw, gap = 350, 35
b.append(f'<line x1="60" y1="52" x2="1140" y2="52" stroke="url(#g)" stroke-width="3" stroke-opacity=".7"/>'
         f'<circle cy="52" r="5" fill="{TEXT}"><animate attributeName="cx" values="60;1140" dur="6s" repeatCount="indefinite"/></circle>')
for i, (e, tag, c, lines, yr) in enumerate(cards):
    x = 40 + i * (cw + gap)
    cx = x + cw / 2
    dash = ' stroke-dasharray="6 6"' if tag == "NEXT MISSION" else ""
    b.append(f'<circle cx="{cx}" cy="52" r="11" fill="{BG}" stroke="{c}" stroke-width="3"/><circle cx="{cx}" cy="52" r="4" fill="{c}"><animate attributeName="opacity" values="1;.3;1" dur="2.4s" begin="{i*.6}s" repeatCount="indefinite"/></circle>'
             f'<line x1="{cx}" y1="64" x2="{cx}" y2="90" stroke="{c}" stroke-opacity=".6"/>'
             f'<rect x="{x}" y="90" width="{cw}" height="214" rx="16" fill="{c}" fill-opacity=".06" stroke="{c}" stroke-opacity=".6"{dash}/>'
             f'<text x="{x+30}" y="150" font-size="44">{e}<animateTransform attributeName="transform" type="translate" values="0 0;0 -4;0 0" dur="3s" begin="{i*.5}s" repeatCount="indefinite"/></text>'
             f'<rect x="{x+cw-30-(30+len(tag)*9)}" y="116" width="{30+len(tag)*9}" height="26" rx="13" fill="{c}" fill-opacity=".16" stroke="{c}"/>'
             f'<text x="{x+cw-30-(30+len(tag)*9)/2}" y="134" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="800" fill="{tx(c)}">{tag}</text>'
             f'<line x1="{x+30}" y1="176" x2="{x+cw-30}" y2="176" stroke="{c}" stroke-opacity=".25"/>'
             f'<text x="{x+30}" y="212" font-family="{FONT}" font-size="19" font-weight="800" fill="{TEXT}">{esc(lines[0])}</text>'
             f'<text x="{x+30}" y="238" font-family="{FONT}" font-size="14" fill="{DIM}">{esc(lines[1])}</text>'
             f'<text x="{x+30}" y="282" font-family="{FONT}" font-size="13" letter-spacing="3" fill="{tx(c)}">{yr}</text>')
b.append('</svg>')
open("assets/milestones.svg", "w").write("".join(b))
print("ok")
