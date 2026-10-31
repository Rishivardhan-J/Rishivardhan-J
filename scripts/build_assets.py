import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
random.seed(11)
from palette import AC_L, SOFT, MUTED, PANEL, AC as A, AC_D as B, SIG as Y, BG as N, FONT, GRAD_STOPS, STAR_PEAK, TEXT, DIM, tx

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

# ---- hero: header, status strip, bays and marquee share one frame and one bottom gap
PAD=10                                     # transparent space under each hero image, so every gap matches
def panel(w,h,back,front="",defs=""):
    clip=f'<clipPath id="pc"><rect width="{w}" height="{h}" rx="18"/></clipPath>'
    return wrap(w,h+PAD,f'<rect width="{w}" height="{h}" rx="18" fill="{N}"/><g clip-path="url(#pc)">{back}</g>'
                f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="17" fill="none" stroke="url(#g)" stroke-opacity=".5" stroke-width="2"/>{front}',defs+clip)
def pill(x,y,w,c,label,mark):
    """Mark and label are centred together. mark(cx,cy) draws the 16px icon or dot."""
    size,h=13,36
    total=16+8+len(label)*size*.6
    x0=x+(w-total)/2
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{c}" fill-opacity=".12" stroke="{c}" stroke-opacity=".7"/>{mark(x0+8,y+h/2)}'
            f'<text x="{x0+24:.1f}" y="{y+23}" font-family="{FONT}" font-size="{size}" font-weight="700" fill="{tx(c)}">{label}</text>')

# ---- header
def chip_glyph(k,c):
    st=f'fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'
    return {"trophy":f'<path d="M-5,-7H5V-2C5,2 2,4 0,4C-2,4 -5,2 -5,-2ZM-5,-5H-8C-8,-2 -7,-1 -5,-1M5,-5H8C8,-2 7,-1 5,-1M0,4V7M-3,7H3" {st}/>',
            "rocket":f'<path d="M0,-8C4,-4 4,2 3,5H-3C-4,2 -4,-4 0,-8ZM-3,3L-6,7L-3,5.5M3,3L6,7L3,5.5" {st}/><circle cy="-2" r="1.3" {st}/>',
            "phone":f'<rect x="-4.5" y="-7.5" width="9" height="15" rx="2" {st}/><path d="M-1.5,5H1.5" {st}/>',
            "nodes":f'<path d="M-5,-4L5,0L-5,4" {st}/><circle cx="-5" cy="-4" r="1.8" {st}/><circle cx="-5" cy="4" r="1.8" {st}/><circle cx="5" r="1.8" {st}/>'}[k]
HW,HH,HR,HTOP=1200,372,2400,336            # size, planet radius, top of the planet's rim
LOG=["Launching ideas into working products","CS Student | Builder | Problem Solver",
     "2x Finalist · GDG TechSprint &amp; AI for Social Impact","Currently in orbit: Forge, HarvestPro and Transit"]
d=(f'<radialGradient id="a1"><stop offset="0" stop-color="{A}" stop-opacity=".18"/><stop offset="1" stop-color="{A}" stop-opacity="0"/></radialGradient>'
   f'<linearGradient id="nm" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1200" y2="0" spreadMethod="repeat">{GRAD_STOPS}<animateTransform attributeName="gradientTransform" type="translate" values="0 0;1200 0" dur="12s" repeatCount="indefinite"/></linearGradient>'
   f'<radialGradient id="pl" cx=".5" cy="0" r=".5"><stop offset="0" stop-color="{PANEL}"/><stop offset="1" stop-color="{N}"/></radialGradient>'
   f'<linearGradient id="rim" gradientUnits="userSpaceOnUse" x1="120" y1="0" x2="1080" y2="0"><stop offset="0" stop-color="{A}" stop-opacity="0"/><stop offset=".5" stop-color="{AC_L}"/><stop offset="1" stop-color="{A}" stop-opacity="0"/></linearGradient>'
   f'<radialGradient id="atm"><stop offset="0" stop-color="{A}" stop-opacity=".24"/><stop offset="1" stop-color="{A}" stop-opacity="0"/></radialGradient>')
hr=random.Random(41)
sky=[]
while len(sky)<80:                         # stars stay out of the text block and off the planet
    x,y=hr.randint(10,HW-10),hr.randint(8,HTOP-14)
    if not (190<x<1010 and 36<y<306): sky.append((x,y))
back=f'<circle cx="220" cy="90" r="260" fill="url(#a1)"><animate attributeName="cx" values="220;300;220" dur="14s" repeatCount="indefinite"/></circle><circle cx="1020" cy="80" r="250" fill="url(#a1)"><animate attributeName="cy" values="80;130;80" dur="12s" repeatCount="indefinite"/></circle>'
back+="".join(f'<circle cx="{x}" cy="{y}" r="{hr.choice([.7,1,1.4])}" fill="{TEXT}"><animate attributeName="opacity" values="0.1;{STAR_PEAK};0.1" dur="{hr.uniform(2,5):.1f}s" begin="{hr.uniform(0,4):.1f}s" repeatCount="indefinite"/></circle>' for x,y in sky)
back+=(f'<g transform="translate(-200 -200)"><animateTransform attributeName="transform" type="translate" values="700 -30;700 -30;1300 90;1300 90" keyTimes="0;.86;.95;1" dur="15s" repeatCount="indefinite"/>'
       f'<line x1="-90" y1="-18" x2="0" y2="0" stroke="{AC_L}" stroke-width="2" stroke-linecap="round"/></g>')
back+=(f'<ellipse cx="600" cy="{HTOP+6}" rx="620" ry="70" fill="url(#atm)"/><circle cx="600" cy="{HTOP+HR}" r="{HR}" fill="url(#pl)"/>'
       f'<circle cx="600" cy="{HTOP+HR}" r="{HR}" fill="none" stroke="url(#rim)" stroke-width="2.5"/><circle cx="600" cy="{HTOP+HR}" r="{HR+7}" fill="none" stroke="url(#rim)" stroke-opacity=".25" stroke-width="8"/>'
       f'<g><rect x="-5" y="-1.5" width="10" height="3" rx="1" fill="{AC_L}"/><rect x="-1.5" y="-4" width="3" height="8" rx="1" fill="{A}"/><animateMotion dur="26s" repeatCount="indefinite" rotate="auto" path="M180,372 Q600,272 1020,372"/></g>')
fr_=f'<text x="600" y="60" text-anchor="middle" font-family="{FONT}" font-size="14" letter-spacing="7" fill="{A}">&lt; SYSTEM ONLINE /&gt;</text>'
fr_+=f'<text x="600" y="144" text-anchor="middle" font-family="{FONT}" font-size="68" font-weight="800" fill="url(#nm)">Rishivardhan J</text>'
fr_+=f'<text x="600" y="190" text-anchor="middle" font-family="{FONT}" font-size="22" fill="{TEXT}">Full Stack &amp; Mobile Developer · CS Student</text>'
for i,l in enumerate(LOG):                 # first line shows by default; the rest fade in on their turn
    n=len(l.replace("&amp;","&"))
    fr_+=(f'<g opacity="{1 if i==0 else 0}"><animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.02;.23;.25;1" dur="16s" begin="{i*4}s" repeatCount="indefinite"/>'
          f'<text x="600" y="230" text-anchor="middle" font-family="{FONT}" font-size="18" fill="{A}">{l}</text>'
          f'<rect x="{600+n*5.4+6:.1f}" y="215" width="9" height="18" fill="{A}"><animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/></rect></g>')
chips=[("2× FINALIST",Y,"trophy"),("6 MISSIONS",A,"rocket"),("WEB + MOBILE",A,"phone"),("ML CURIOUS",A,"nodes")]
x=600-(4*190+3*14)/2
for t,c,k in chips:
    fr_+=pill(x,258,190,c,t,lambda cx,cy,k=k,c=c:f'<g transform="translate({cx:.1f} {cy})">{chip_glyph(k,tx(c))}</g>')
    x+=204
out("header.svg",panel(HW,HH,back,fr_,d))

# ---- marquee (2 counter-scrolling rows, fixed-width cells, labelled over the edge fade)
def row(y,items,cell,col,dur,rev):
    total=cell*len(items); g=""
    for k in range(3):
        for i,t in enumerate(items):
            g+=pill(k*total+i*cell+8,y,cell-16,col,t,lambda cx,cy:f'<circle cx="{cx:.1f}" cy="{cy}" r="3.5" fill="{col}"/>')
    fr,to=("-%d 0"%total,"0 0") if rev else ("0 0","-%d 0"%total)
    return f'<g>{g}<animateTransform attributeName="transform" type="translate" from="{fr}" to="{to}" dur="{dur}s" repeatCount="indefinite"/></g>'
P=("Bench","Forge","HarvestPro","TrackIt","Transit","Galaxy")
T=("React","TypeScript","Python","Flutter","Node.js","Docker","MongoDB","PostgreSQL","Java","Firebase")
fade=f'<linearGradient id="f" x1="0" x2="1"><stop offset="0" stop-color="{N}"/><stop offset=".12" stop-color="{N}"/><stop offset=".2" stop-color="{N}" stop-opacity="0"/><stop offset=".93" stop-color="{N}" stop-opacity="0"/><stop offset="1" stop-color="{N}"/></linearGradient>'
back=f'{row(14,P,200,A,24,False)}{row(58,T,170,A,34,True)}<rect width="1200" height="108" fill="url(#f)"/>'
front="".join(f'<text x="28" y="{y}" font-family="{FONT}" font-size="11" font-weight="700" letter-spacing="3" fill="{A}">{t}</text>' for y,t in ((36,"MISSIONS"),(80,"STACK")))
out("marquee.svg",panel(1200,108,back,front,fade))

# ---- divider (gradient in userSpace so the line renders)
b=f'<line x1="0" y1="15" x2="1200" y2="15" stroke="url(#g)" stroke-opacity=".5" stroke-width="2"/><circle cx="600" cy="15" r="5" fill="{AC_L}"><animate attributeName="r" values="3;7;3" dur="3s" repeatCount="indefinite"/></circle><circle cy="15" r="3" fill="{TEXT}"><animate attributeName="cx" values="0;1200" dur="5s" repeatCount="indefinite"/></circle>'
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
    tx0=26+len(label)*11.5
    b=(f'<circle cx="5" cy="27" r="4" fill="{A}"><animate attributeName="opacity" values="1;.25;1" dur="2s" repeatCount="indefinite"/></circle>'
       f'<text x="20" y="31" font-family="{FONT}" font-size="11" font-weight="700" letter-spacing="4" fill="{A}">{label}</text>'
       f'<line x1="{tx0:.0f}" y1="27" x2="1200" y2="27" stroke="url(#g)" stroke-opacity=".4" stroke-width="2"/>')
    out(f"mission-row-{k}.svg",wrap(1200,42,b))

# ---- accessible buttons (shields.io always prints white text, which fails on cyan)
# 44px buttons with vector icons (no emoji: they render per platform).
_st = f'fill="none" stroke="{{c}}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
def _icon(kind, c):
    st = _st.format(c=c)
    return {
        "globe": f'<circle r="7" {st}/><ellipse rx="3" ry="7" {st}/><path d="M-7,0H7" {st}/>',
        "in": f'<path d="M-6,-1V6M-6,-5V-5M-1,6V-1M-1,2C-1,-2 6,-2 6,2V6" {st}/>',
        "mail": f'<rect x="-8" y="-5.5" width="16" height="11" rx="2" {st}/><path d="M-7,-4L0,2L7,-4" {st}/>',
        "pin": f'<path d="M0,8C-6,1 -6,-7 0,-7C6,-7 6,1 0,8Z" {st}/><circle cy="-2" r="2" {st}/>',
    }[kind]
def btn(name, label, icon, kind, w):
    """kind: primary (filled), secondary (outlined), status (gold, pulsing dot), info (outlined, no chevron)."""
    c = {"primary": N, "secondary": A, "status": Y, "info": A}[kind]
    defs = f'<linearGradient id="p" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AC_L}"/><stop offset="1" stop-color="{A}"/></linearGradient>'
    if kind == "primary":
        body = f'<rect x="1" y="1" width="{w-2}" height="42" rx="12" fill="url(#p)"/><rect x="2" y="2" width="{w-4}" height="40" rx="11" fill="none" stroke="{AC_L}" stroke-opacity=".35"/>'
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
btn("btn-portfolio.svg", "PORTFOLIO · GALAXY", "globe", "primary", 288)
btn("btn-linkedin.svg", "LINKEDIN", "in", "secondary", 168)
btn("btn-email.svg", "EMAIL", "mail", "secondary", 184)

# ---- comms console (header): one status strip plus three stitched link bays
TX = lambda x, y, t, size, c, extra="": f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{c}" {extra}>{t}</text>'
sig = (f'<radialGradient id="r"><stop offset="0" stop-color="{Y}" stop-opacity=".16"/><stop offset="1" stop-color="{Y}" stop-opacity="0"/></radialGradient>')
rings = "".join(f'<circle cx="64" cy="48" r="8" fill="none" stroke="{Y}" stroke-width="2" stroke-opacity=".5"><animate attributeName="r" values="8;32" dur="3s" begin="{k}s" repeatCount="indefinite"/>'
                f'<animate attributeName="stroke-opacity" values=".6;0" dur="3s" begin="{k}s" repeatCount="indefinite"/></circle>' for k in (0, 1.5))
bars = "".join(f'<rect x="{566 + i * 14}" y="{70 - h}" width="8" height="{h}" rx="2" fill="{A}"><animate attributeName="opacity" values="1;.35;1" dur="2.4s" begin="{i * .25}s" repeatCount="indefinite"/></rect>'
               for i, h in enumerate((10, 18, 26, 34, 42)))
out("console-status.svg", panel(1200, 96, f'<circle cx="64" cy="48" r="150" fill="url(#r)"/>',
    rings + f'<circle cx="64" cy="48" r="6" fill="{Y}"/>'
    + TX(116, 46, "OPEN TO WORK", 24, Y, 'font-weight="800" letter-spacing="2"')
    + TX(116, 69, "Internships &amp; Full-time", 13, SOFT)
    + bars
    + TX(1160, 44, "SECTOR TAMIL NADU, IN", 13, A, 'text-anchor="end" letter-spacing="2"')
    + TX(1160, 67, "UTC+05:30", 12, MUTED, 'text-anchor="end" letter-spacing="2"'), sig))

def bay(name, ch, title, sub, scene, first=False, last=False, primary=False, W_=400, H_=132):
    r = 17
    x0, x1 = (1 if first else 0), (W_ - 1 if last else W_)
    left = f"M{x0 + r},1" if first else f"M{x0},1"
    d = (left + f"H{x1 - r if last else x1}" + (f"a{r},{r} 0 0 1 {r},{r}V{H_ - 1 - r}a{r},{r} 0 0 1 {-r},{r}" if last else f"V{H_ - 1}")
         + f"H{x0 + r if first else x0}" + (f"a{r},{r} 0 0 1 {-r},{-r}V{1 + r}a{r},{r} 0 0 1 {r},{-r}" if first else "") + "Z")
    c, sub_c = (N, N) if primary else (A, SOFT)
    d_p = (f'<linearGradient id="p" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AC_L}"/><stop offset="1" stop-color="{A}"/></linearGradient>'
           f'<radialGradient id="gl"><stop offset="0" stop-color="{B}" stop-opacity=".22"/><stop offset="1" stop-color="{B}" stop-opacity="0"/></radialGradient><clipPath id="bc"><path d="{d}"/></clipPath>')
    fill = f'<path d="{d}" fill="url(#p)"/>' if primary else f'<path d="{d}" fill="{N}"/><g clip-path="url(#bc)"><circle cx="{W_ - 80}" cy="{H_ / 2 + 10}" r="150" fill="url(#gl)"/></g>'
    ax = W_ - 22
    arrow = f'<path d="M{ax - 14},34L{ax},20M{ax - 12},20H{ax}V32" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    out(name, wrap(W_, H_ + PAD, fill + f'<path d="{d}" fill="none" stroke="{N if primary else "url(#g)"}" stroke-opacity=".5" stroke-width="2"/>' + scene(c) + arrow
        + TX(28, 34 if H_ > 120 else 28, ch, 12, c, 'letter-spacing="3"') + TX(28, H_ - 48, title, 26, N if primary else TEXT, 'font-weight="800"') + TX(28, H_ - 24, sub, 13, sub_c), d_p))

def planet(c):
    orbit = "M-34,0a34,11 0 1 0 68,0a34,11 0 1 0 -68,0"
    return (f'<circle cx="310" cy="76" r="20" fill="{c}" fill-opacity=".12" stroke="{c}" stroke-width="2"/>'
            f'<g transform="translate(310 76) rotate(-20)"><path d="{orbit}" fill="none" stroke="{c}" stroke-opacity=".6" stroke-width="2"/>'
            f'<circle r="4.5" fill="{c}"><animateMotion dur="6s" repeatCount="indefinite" path="{orbit}"/></circle></g>')
def network(c):
    hub, nodes = (316, 76), [(282, 58), (322, 40), (352, 78), (300, 108)]
    b = "".join(f'<line x1="{hub[0]}" y1="{hub[1]}" x2="{x}" y2="{y}" stroke="{c}" stroke-opacity=".5" stroke-width="2"/>' for x, y in nodes)
    b += "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="{N}" stroke="{c}" stroke-width="2"/>' for x, y in nodes)
    b += f'<circle cx="{hub[0]}" cy="{hub[1]}" r="8" fill="{N}" stroke="{c}" stroke-width="2"/>'
    return b + "".join(f'<circle r="3" fill="{AC_L}"><animateMotion dur="3s" begin="{i * .75}s" repeatCount="indefinite" path="M{hub[0]},{hub[1]}L{x},{y}L{hub[0]},{hub[1]}"/></circle>' for i, (x, y) in enumerate(nodes))
def envelope(c):
    st = f'fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    arcs = "".join(f'<path d="M{342 + k * 9},{66 - k * 7}a{14 + k * 9},{14 + k * 9} 0 0 1 0,{20 + k * 14}" {st}><animate attributeName="opacity" values="1;.2;1" dur="2.4s" begin="{k * .4}s" repeatCount="indefinite"/></path>' for k in range(3))
    return f'<rect x="284" y="58" width="52" height="36" rx="5" {st}/><path d="M286,62L310,80L334,62" {st}/>' + arcs

bay("bay-portfolio.svg", "CH-01", "PORTFOLIO", "Galaxy live site", planet, first=True, primary=True)
bay("bay-linkedin.svg", "CH-02", "LINKEDIN", "in/rishivardhan-j", network)
bay("bay-email.svg", "CH-03", "EMAIL", "Direct line", envelope, last=True)

# ---- flagship launch bays: the same stitched frame, under the Flagship panel
def launch(c):
    st = f'fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    return (f'<circle cx="508" cy="62" r="22" fill="{c}" fill-opacity=".12" stroke="{c}" stroke-width="2"/><path d="M501,50L521,62L501,74Z" {st}/>'
            f'<circle cx="508" cy="62" r="22" fill="none" stroke="{c}"><animate attributeName="r" values="22;36" dur="2.4s" repeatCount="indefinite"/><animate attributeName="stroke-opacity" values=".6;0" dur="2.4s" repeatCount="indefinite"/></circle>')
def commits(c):
    st = f'fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    main, side = "M456,76H548", "M476,76C492,76 490,46 508,46H528"
    nodes = "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="{N}" stroke="{c}" stroke-width="2"/>' for x, y in ((456, 76), (496, 76), (548, 76), (528, 46)))
    return (f'<path d="{main}" {st}/><path d="{side}" {st}/><path d="M528,46C542,46 536,76 548,76" {st} stroke-opacity=".5"/>{nodes}'
            f'<circle r="3" fill="{AC_L}"><animateMotion dur="4s" repeatCount="indefinite" path="{main}"/></circle>')
bay("bay-demo.svg", "LAUNCH", "LIVE DEMO", "rishi-galaxy.vercel.app", launch, first=True, primary=True, W_=600, H_=112)
bay("bay-repo.svg", "SOURCE", "VIEW REPO", "Rishivardhan-J/Galaxy", commits, last=True, W_=600, H_=112)
