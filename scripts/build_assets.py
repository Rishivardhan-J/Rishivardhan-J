import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
random.seed(11)
from palette import AC as A, AC_D as B, SIG as Y, BG as N, FONT, GRAD_STOPS, STAR_PEAK, TEXT, DIM, tx

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

# ---- footer
import math
pts=" ".join(f"{x},{48+22*math.sin(x/38)*math.sin(x/260)}" for x in range(0,1201,10))
b=f'<rect width="1200" height="100" fill="{N}"/>'+stars(1200,100,30)+f'<polyline points="{pts}" fill="none" stroke="url(#g)" stroke-width="2.5"/><text x="600" y="92" text-anchor="middle" font-family="{FONT}" font-size="13" letter-spacing="5" fill="{tx(A)}" opacity=".85">END OF TRANSMISSION · THANKS FOR VISITING</text>'
out("footer.svg",wrap(1200,100,b))

# ---- mission cards 460x200 with description inside
M=[("trackit","TrackIt","📋","ACTIVE","React · TypeScript",["Deadline-driven tracker for internship &amp;","hackathon applications, with an admin","pipeline to post and moderate listings."]),
("bench","Bench","🧑‍💻","ACTIVE","React · TypeScript",["Intelligent, high-performance freelancer","discovery by skills, availability and","project needs."]),
("forge","Forge","⚒️","BUILDING","Flutter · Dart",["Habit-formation app built on the","framework from Atomic Habits."]),
("harvestpro","HarvestPro","🌾","BUILDING","Flutter · AI",["Turns AI crop predictions into advice","Indian farmers can trust and act on,","in their own language."]),
("transit","Transit","🚦","BUILDING","Python · ML · VRP",["Real-time logistics optimization: ML","delivery-time prediction + Hybrid Genetic","Search routing with explainability."]),
("galaxy","Galaxy","🌌","LIVE","React · Vite · TypeScript",["A no-scroll, space-themed portfolio where","you travel between projects, skills and","contact through warp transitions."])]
for k,n,e,st,stack,desc in M:
    b=f'<rect x="1.5" y="1.5" width="457" height="215" rx="16" fill="{N}" stroke="url(#g)" stroke-opacity=".55" stroke-width="2"/>'+stars(460,218,22)
    b+=f'<circle cx="52" cy="52" r="30" fill="{B}" fill-opacity=".15" stroke="{A}" stroke-opacity=".6" stroke-dasharray="3 5"><animateTransform attributeName="transform" type="rotate" from="0 52 52" to="360 52 52" dur="18s" repeatCount="indefinite"/></circle><text x="52" y="63" text-anchor="middle" font-size="28">{e}</text>'
    b+=f'<text x="98" y="48" font-family="{FONT}" font-size="26" font-weight="800" fill="url(#g)">{n}</text><text x="98" y="68" font-family="{FONT}" font-size="12" fill="{DIM}">{stack}</text>'
    pw=34+len(st)*9; sc=Y if st=="LIVE" else A
    b+=f'<rect x="{458-pw-16}" y="22" width="{pw}" height="24" rx="12" fill="{sc}" fill-opacity=".14" stroke="{sc}"/><circle cx="{458-pw-2}" cy="34" r="3.5" fill="{sc}"><animate attributeName="opacity" values="1;.2;1" dur="2s" repeatCount="indefinite"/></circle><text x="{458-pw+8}" y="39" font-family="{FONT}" font-size="11" font-weight="700" fill="{tx(sc)}">{st}</text>'
    b+=f'<line x1="24" y1="96" x2="436" y2="96" stroke="{A}" stroke-opacity=".25"/>'
    for i,l in enumerate(desc):
        b+=f'<text x="24" y="{124+i*24}" font-family="{FONT}" font-size="13.5" fill="{TEXT}">{l}</text>'
    b+=f'<text x="436" y="203" text-anchor="end" font-family="{FONT}" font-size="12" font-weight="700" letter-spacing="2" fill="{tx(A)}">{"VISIT SITE ↗" if k=="galaxy" else "VIEW REPO ↗"}</text>'
    out(f"mission-{k}.svg",wrap(460,218,b))

# ---- accessible buttons (shields.io always prints white text, which fails on cyan)
def btn(name, label, fill, text, stroke=None, w=None):
    w = w or int(len(label) * 10.6 + 44)
    st = stroke or fill
    out(name, wrap(w, 40, f'<rect x="1" y="1" width="{w-2}" height="38" rx="9" fill="{fill}" stroke="{st}" stroke-width="2"/>'
        f'<text x="{w/2}" y="25" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="800" letter-spacing="1.5" fill="{text}">{label}</text>'))
btn("btn-portfolio.svg", "🌌 PORTFOLIO · GALAXY", A, N)
btn("btn-linkedin.svg", "LINKEDIN", N, A, A)
btn("btn-email.svg", "✉ EMAIL", N, A, A)
btn("btn-demo.svg", "LIVE DEMO ↗", A, N)
btn("btn-repo.svg", "VIEW REPO ↗", N, A, A)
btn("pill-status.svg", "● OPEN TO INTERNSHIPS &amp; FULL-TIME", N, Y, Y, 330)
btn("pill-location.svg", "📍 TAMIL NADU, INDIA", N, tx(B), B, 232)
