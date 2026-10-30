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

# ---- footer: planet horizon finale
import math
from palette import AC_L, PANEL, MUTED, TRACK
stars(1200,100,30)  # burn the old footer's draws so the seeded mission-card output below stays unchanged
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
