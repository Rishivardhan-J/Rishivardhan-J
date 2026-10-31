import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
random.seed(11)
from palette import AC_L, AC as A, AC_D as B, SIG as Y, BG as N, FONT, GRAD_STOPS, STAR_PEAK, TEXT, DIM, tx

GRAD=lambda w:f'<linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{w}" y2="0">{GRAD_STOPS}</linearGradient>'
def stars(w,h,n,cls=""):
    s=""
    for _ in range(n):
        x,y=random.randint(5,w-5),random.randint(5,h-5)
        r=random.choice([.7,1,1.4]);d=random.uniform(2,5);b=random.uniform(0,4)
        s+=f'<circle cx="{x}" cy="{y}" r="{r}" fill="{TEXT}"><animate attributeName="opacity" values="0.1;{STAR_PEAK};0.1" dur="{d:.1f}s" begin="{b:.1f}s" repeatCount="indefinite"/></circle>'
    return s
def wrap(w,h,body,defs=""):
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg"><defs>{GRAD(w)}{defs}</defs>{body}</svg>'
def out(n,s): open(f"assets/{n}","w").write(s)

# ---- header
d=f'<radialGradient id="a1"><stop offset="0" stop-color="{A}" stop-opacity=".22"/><stop offset="1" stop-color="{A}" stop-opacity="0"/></radialGradient><radialGradient id="a2"><stop offset="0" stop-color="{B}" stop-opacity=".32"/><stop offset="1" stop-color="{B}" stop-opacity="0"/></radialGradient><radialGradient id="a3"><stop offset="0" stop-color="{A}" stop-opacity=".14"/><stop offset="1" stop-color="{A}" stop-opacity="0"/></radialGradient><clipPath id="hc"><rect width="1200" height="320" rx="16"/></clipPath>'
b=f'<rect width="1200" height="320" rx="16" fill="{N}"/><g clip-path="url(#hc)">'
b+=f'<circle cx="220" cy="90" r="260" fill="url(#a1)"><animate attributeName="cx" values="220;300;220" dur="14s" repeatCount="indefinite"/></circle>'
b+=f'<circle cx="640" cy="330" r="300" fill="url(#a2)"><animate attributeName="cx" values="640;560;640" dur="16s" repeatCount="indefinite"/></circle>'
b+=f'<circle cx="1020" cy="80" r="250" fill="url(#a3)"><animate attributeName="cy" values="80;150;80" dur="12s" repeatCount="indefinite"/></circle>'
b+=stars(1200,320,110)
for i,(y,dl) in enumerate([(40,0),(120,5),(210,9)]):
    b+=f'<line x1="0" y1="0" x2="90" y2="0" stroke="url(#g)" stroke-width="2" stroke-linecap="round" opacity="0"><animateTransform attributeName="transform" type="translate" values="-100 {y};1300 {y+130}" dur="1.8s" begin="{dl}s;{dl+12}s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;1;0" dur="1.8s" begin="{dl}s;{dl+12}s" repeatCount="indefinite"/></line>'
b+='</g>'
b+=f'<text x="600" y="62" text-anchor="middle" font-family="{FONT}" font-size="14" letter-spacing="7" fill="{tx(A)}" opacity=".85">&lt; SYSTEM ONLINE /&gt;</text>'
b+=f'<text x="600" y="152" text-anchor="middle" font-family="{FONT}" font-size="68" font-weight="800" fill="url(#g)">Rishivardhan J</text>'
b+=f'<text x="600" y="200" text-anchor="middle" font-family="{FONT}" font-size="22" fill="{TEXT}">Full Stack &amp; Mobile Developer · CS Student</text>'
chips=[("🏆 2× FINALIST",Y),("🚀 5 PROJECTS",A),("📱 WEB + MOBILE",A),("🧠 ML CURIOUS",A)]
x=600-(4*190+3*14)/2
for t,c in chips:
    b+=f'<rect x="{x}" y="240" width="190" height="36" rx="18" fill="{c}" fill-opacity=".12" stroke="{c}" stroke-opacity=".7"/><text x="{x+95}" y="263" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="700" fill="{tx(c)}">{t}</text>'
    x+=204
b+=f'<rect x="1" y="1" width="1198" height="318" rx="15" fill="none" stroke="url(#g)" stroke-opacity=".5" stroke-width="2"/>'
out("header.svg",wrap(1200,320,b,d))

# ---- marquee (2 counter-scrolling rows, fixed-width cells)
def row(y,items,cell,col,dur,rev):
    total=cell*len(items); g=""
    for k in range(3):
        for i,(e,t) in enumerate(items):
            cx=k*total+i*cell+cell/2
            g+=f'<rect x="{cx-cell/2+8}" y="{y}" width="{cell-16}" height="40" rx="20" fill="{col}" fill-opacity=".1" stroke="{col}" stroke-opacity=".55"/><text x="{cx}" y="{y+26}" text-anchor="middle" font-family="{FONT}" font-size="17" font-weight="700" fill="{tx(col)}">{e} {t}</text>'
    fr,to=("-%d 0"%total,"0 0") if rev else ("0 0","-%d 0"%total)
    return f'<g>{g}<animateTransform attributeName="transform" type="translate" from="{fr}" to="{to}" dur="{dur}s" repeatCount="indefinite"/></g>'
P=[("🚀","Bench"),("⚒️","Forge"),("🌾","HarvestPro"),("📋","TrackIt"),("🚦","Transit"),("🌌","Galaxy")]
T=[("⚛️","React"),("🟦","TypeScript"),("🐍","Python"),("🎯","Flutter"),("🟢","Node.js"),("🐳","Docker"),("🍃","MongoDB"),("🐘","PostgreSQL"),("☕","Java"),("🔥","Firebase")]
fade=f'<linearGradient id="f" x1="0" x2="1"><stop offset="0" stop-color="{N}"/><stop offset=".08" stop-color="{N}" stop-opacity="0"/><stop offset=".92" stop-color="{N}" stop-opacity="0"/><stop offset="1" stop-color="{N}"/></linearGradient><clipPath id="mc"><rect width="1200" height="120" rx="14"/></clipPath>'
b=f'<rect width="1200" height="120" rx="14" fill="{N}"/><g clip-path="url(#mc)">{row(14,P,240,A,24,False)}{row(66,T,190,A,34,True)}<rect width="1200" height="120" fill="url(#f)"/></g><rect x=".5" y=".5" width="1199" height="119" rx="14" fill="none" stroke="url(#g)" stroke-opacity=".4"/>'
out("marquee.svg",wrap(1200,120,b,fade))

# ---- divider (gradient in userSpace so the line renders)
b=f'<line x1="0" y1="15" x2="1200" y2="15" stroke="url(#g)" stroke-opacity=".5" stroke-width="2"/><circle cx="600" cy="15" r="5" fill="{Y}"><animate attributeName="r" values="3;7;3" dur="3s" repeatCount="indefinite"/></circle><circle cy="15" r="3" fill="{TEXT}"><animate attributeName="cx" values="0;1200" dur="5s" repeatCount="indefinite"/></circle>'
out("divider.svg",wrap(1200,30,b))

# ---- footer: planet horizon finale
import math
from palette import AC_L, PANEL, MUTED, TRACK
fr=random.Random(23)
FW,FH,PR=1200,240,1400                     # card size, planet radius (centre sits PR below the horizon line)
PCX,PCY=600,140+PR
fd=(f'<clipPath id="fc"><rect width="{FW}" height="{FH}" rx="18"/></clipPath>'
    f'<radialGradient id="pl" cx=".5" cy="0" r=".5"><stop offset="0" stop-color="{PANEL}"/><stop offset="1" stop-color="{N}"/></radialGradient>'
    f'<linearGradient id="rim" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{FW}" y2="0"><stop offset="0" stop-color="{A}" stop-opacity="0"/><stop offset=".5" stop-color="{AC_L}"/><stop offset="1" stop-color="{A}" stop-opacity="0"/></linearGradient>'
    f'<radialGradient id="atm" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{A}" stop-opacity=".28"/><stop offset="1" stop-color="{A}" stop-opacity="0"/></radialGradient>')
b=f'<rect width="{FW}" height="{FH}" rx="18" fill="{N}"/><g clip-path="url(#fc)">'
for i in range(80):
    x,y=fr.uniform(10,FW-10),fr.uniform(8,128)
    tw=f'<animate attributeName="opacity" values=".15;.7;.15" dur="{fr.uniform(2.4,5.5):.1f}s" begin="{fr.uniform(0,4):.1f}s" repeatCount="indefinite"/>' if i%3==0 else ''
    b+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{fr.choice([.6,.9,1.3]):.1f}" fill="{TEXT}" fill-opacity="{fr.uniform(.2,.5):.2f}">{tw}</circle>'
b+=(f'<ellipse cx="{PCX}" cy="150" rx="620" ry="80" fill="url(#atm)"/>'
    f'<circle cx="{PCX}" cy="{PCY}" r="{PR}" fill="url(#pl)"/>'
    f'<circle cx="{PCX}" cy="{PCY}" r="{PR}" fill="none" stroke="url(#rim)" stroke-width="2.5"/>'
    f'<circle cx="{PCX}" cy="{PCY}" r="{PR+7}" fill="none" stroke="url(#rim)" stroke-opacity=".25" stroke-width="8"/>')
# a satellite riding just above the rim (quadratic path lifted 14px over the horizon)
b+=(f'<g><rect x="-5" y="-1.5" width="10" height="3" rx="1" fill="{AC_L}"/><rect x="-1.5" y="-4" width="3" height="8" rx="1" fill="{A}"/>'
    f'<animateMotion dur="26s" repeatCount="indefinite" rotate="auto" path="M80,226 Q600,18 1120,226"/></g>')
b+='</g>'
b+=(f'<text x="600" y="78" text-anchor="middle" font-family="{FONT}" font-size="14" letter-spacing="6" fill="{A}">END OF TRANSMISSION · SEE YOU IN ORBIT</text>'
    f'<text x="600" y="104" text-anchor="middle" font-family="{FONT}" font-size="11" letter-spacing="3" fill="{MUTED}">THANKS FOR VISITING</text>'
    f'<rect x="1" y="1" width="{FW-2}" height="{FH-2}" rx="17" fill="none" stroke="url(#g)" stroke-opacity=".5" stroke-width="2"/>')
out("footer.svg",wrap(FW,FH,b,fd))

# ---- hangar: five docking-bay cards (name, language), 220x124
HG=[("hostel","Smart Hostel","Management System","JavaScript","Smart_Hostel_Management_System"),
    ("doctorv","DoctorV","","TypeScript","DoctorV"),
    ("music","Mood-based Music","Playlist Generator","Java","Mood-based-Music-Playlist-Generator"),
    ("worklog","AI WorkLog &amp;","Productivity Tracker","Python","AI-Powered-WorkLog-and-Productivity-Tracker"),
    ("food","Food Delivery","App","JavaScript","Food_delivery_app")]
hr=random.Random(5)
for i,(k,l1,l2,lang,_) in enumerate(HG):
    cw=22+len(lang)*6.6
    b=f'<rect x="1.5" y="1.5" width="217" height="121" rx="16" fill="{N}" stroke="url(#g)" stroke-opacity=".5" stroke-width="2"/>'
    for _ in range(9):
        b+=f'<circle cx="{hr.uniform(8,212):.1f}" cy="{hr.uniform(8,116):.1f}" r="{hr.choice([.6,.9,1.2]):.1f}" fill="{TEXT}" fill-opacity="{hr.uniform(.15,.4):.2f}"/>'
    b+=(f'<text x="20" y="31" font-family="{FONT}" font-size="10" letter-spacing="3" fill="{MUTED}">BAY {i+1:02d}</text>'
        f'<rect x="{200-cw:.1f}" y="17" width="{cw:.1f}" height="21" rx="10.5" fill="{A}" fill-opacity=".1" stroke="{A}" stroke-opacity=".5"/>'
        f'<text x="{200-cw/2:.1f}" y="31" text-anchor="middle" font-family="{FONT}" font-size="10" font-weight="700" fill="{A}">{lang}</text>')
    ys=(64,84) if l2 else (74,)
    for yy,t in zip(ys,(l1,l2)):
        b+=f'<text x="20" y="{yy}" font-family="{FONT}" font-size="14" font-weight="800" fill="{TEXT}">{t}</text>'
    b+=(f'<line x1="20" y1="96" x2="200" y2="96" stroke="{A}" stroke-opacity=".2"/>'
        f'<text x="20" y="113" font-family="{FONT}" font-size="10" font-weight="700" letter-spacing="2" fill="{A}">VIEW REPO ↗</text>'
        f'<circle cx="200" cy="109" r="3" fill="{A}"><animate attributeName="opacity" values="1;.25;1" dur="{2+i*.4:.1f}s" repeatCount="indefinite"/></circle>')
    out(f"hangar-{k}.svg",wrap(220,124,b))

# ---- mission row labels (the cards themselves are built by CI: scripts/build_missions.py)
for k,label in (("active","ACTIVE · IN ORBIT"),("building","BUILDING · ON THE LAUNCHPAD")):
    tx0=34+len(label)*11.5
    b=(f'<circle cx="12" cy="15" r="4" fill="{A}"><animate attributeName="opacity" values="1;.25;1" dur="2s" repeatCount="indefinite"/></circle>'
       f'<text x="28" y="19" font-family="{FONT}" font-size="11" font-weight="700" letter-spacing="4" fill="{A}">{label}</text>'
       f'<line x1="{tx0:.0f}" y1="15" x2="1200" y2="15" stroke="url(#g)" stroke-opacity=".4" stroke-width="2"/>')
    out(f"mission-row-{k}.svg",wrap(1200,30,b))

# ---- accessible buttons (shields.io always prints white text, which fails on cyan)
# 44px console buttons with vector icons (no emoji: they render per platform). Row widths are chosen so
# the header rows both total 640px: pills 372+268, buttons 288+168+184.
_st = f'fill="none" stroke="{{c}}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
def _icon(kind, c):
    st = _st.format(c=c)
    return {
        "globe": f'<circle r="7" {st}/><ellipse rx="3" ry="7" {st}/><path d="M-7,0H7" {st}/>',
        "in": f'<path d="M-6,-1V6M-6,-5V-5M-1,6V-1M-1,2C-1,-2 6,-2 6,2V6" {st}/>',
        "mail": f'<rect x="-8" y="-5.5" width="16" height="11" rx="2" {st}/><path d="M-7,-4L0,2L7,-4" {st}/>',
        "pin": f'<path d="M0,8C-6,1 -6,-7 0,-7C6,-7 6,1 0,8Z" {st}/><circle cy="-2" r="2" {st}/>',
        "play": f'<path d="M-3,-6L6,0L-3,6Z" {st}/>',
        "repo": f'<path d="M-3,-5L-8,0L-3,5M3,-5L8,0L3,5" {st}/>',
    }[kind]
def btn(name, label, icon, kind, w):
    """kind: primary (filled), secondary (outlined), status (gold, pulsing dot), info (outlined, no chevron)."""
    c = {"primary": N, "secondary": A, "status": Y, "info": A}[kind]
    defs = f'<linearGradient id="p" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AC_L}"/><stop offset="1" stop-color="{A}"/></linearGradient>'
    if kind == "primary":
        body = f'<rect x="1" y="1" width="{w-2}" height="42" rx="12" fill="url(#p)"/><rect x="2" y="2" width="{w-4}" height="40" rx="11" fill="none" stroke="#fff" stroke-opacity=".35"/>'
        badge = f'<circle cx="26" cy="22" r="14" fill="{N}" fill-opacity=".12"/>'
    else:
        edge = f'stroke="{Y}"' if kind == "status" else 'stroke="url(#g)" stroke-opacity=".85"'
        tint = Y if kind == "status" else A
        body = f'<rect x="1" y="1" width="{w-2}" height="42" rx="12" fill="{N}"/><rect x="1" y="1" width="{w-2}" height="42" rx="12" fill="{tint}" fill-opacity=".08" {edge} stroke-width="2"/>'
        badge = f'<circle cx="26" cy="22" r="14" fill="{tint}" fill-opacity=".14"/>'
    if icon == "dot":
        ic = (f'<g transform="translate(26 22)"><circle r="4" fill="{Y}"><animate attributeName="r" values="3.5;5.5;3.5" dur="2s" repeatCount="indefinite"/></circle>'
              f'<circle r="8" fill="none" stroke="{Y}" stroke-opacity=".5"><animate attributeName="r" values="6;10;6" dur="2s" repeatCount="indefinite"/><animate attributeName="stroke-opacity" values=".6;0;.6" dur="2s" repeatCount="indefinite"/></circle></g>')
    else:
        ic = f'<g transform="translate(26 22)">{_icon(icon, c)}</g>'
    chev = ""
    right = w - 22
    if kind in ("primary", "secondary"):
        chev = f'<path d="M{w-30},17L{w-24},22L{w-30},27" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" stroke-opacity=".8"/>'
        right = w - 38
    cx = (46 + right) / 2
    out(name, wrap(w, 44, body + badge + ic + chev +
        f'<text x="{cx:.1f}" y="27" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="800" letter-spacing="1.2" fill="{c}">{label}</text>', defs))
auto = lambda label: int(len(label.replace("&amp;", "&")) * 9.0 + 100)
btn("btn-portfolio.svg", "PORTFOLIO · GALAXY", "globe", "primary", 288)
btn("btn-linkedin.svg", "LINKEDIN", "in", "secondary", 168)
btn("btn-email.svg", "EMAIL", "mail", "secondary", 184)
btn("btn-demo.svg", "LIVE DEMO", "play", "primary", auto("LIVE DEMO"))
btn("btn-repo.svg", "VIEW REPO", "repo", "secondary", auto("VIEW REPO"))
btn("pill-status.svg", "OPEN TO INTERNSHIPS &amp; FULL-TIME", "dot", "status", 372)
btn("pill-location.svg", "TAMIL NADU, INDIA", "pin", "info", 268)
