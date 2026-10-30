"""Builds assets/stack.svg: themed tech-stack panel with embedded skillicons.dev icons."""
import base64, urllib.request

CY, VI, PK, AM, BG = "#22D3EE", "#8B5CF6", "#F472B6", "#FBBF24", "#070A1A"
FONT = "Fira Code, Consolas, monospace"
LANES = [
    ("LANGUAGES", CY, [("js", "JavaScript"), ("ts", "TypeScript"), ("py", "Python"), ("java", "Java"), ("cpp", "C++"), ("c", "C"), ("dart", "Dart"), ("html", "HTML"), ("css", "CSS")]),
    ("FRAMEWORKS", VI, [("react", "React"), ("nodejs", "Node.js"), ("express", "Express"), ("django", "Django"), ("flask", "Flask"), ("fastapi", "FastAPI"), ("spring", "Spring"), ("flutter", "Flutter"), ("tailwind", "Tailwind"), ("vite", "Vite"), ("jquery", "jQuery")]),
    ("DATA", PK, [("postgres", "PostgreSQL"), ("mysql", "MySQL"), ("mongodb", "MongoDB"), ("firebase", "Firebase"), ("sqlite", "SQLite"), ("numpy", "NumPy"), ("pandas", "Pandas")]),
    ("TOOLS", AM, [("git", "Git"), ("github", "GitHub"), ("vscode", "VS Code"), ("linux", "Linux"), ("docker", "Docker"), ("kubernetes", "K8s"), ("vercel", "Vercel"), ("netlify", "Netlify"), ("postman", "Postman"), ("figma", "Figma")]),
]


SIMPLE = {"numpy": "4DABCF", "pandas": "E70488"}  # not in skillicons -> Simple Icons, tinted for dark tiles


def icon(i):
    url = f"https://cdn.simpleicons.org/{i}/{SIMPLE[i]}" if i in SIMPLE else f"https://skillicons.dev/icons?i={i}&theme=dark"
    req = urllib.request.Request(url, headers={"User-Agent": "stack-build"})
    return base64.b64encode(urllib.request.urlopen(req).read()).decode()


W, LH, GAP, TOP = 1200, 118, 14, 16
H = TOP * 2 + len(LANES) * LH + (len(LANES) - 1) * GAP
o = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">',
     f'<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0"><stop offset="0" stop-color="{CY}"/><stop offset=".55" stop-color="{VI}"/><stop offset="1" stop-color="{PK}"/></linearGradient></defs>',
     f'<rect width="{W}" height="{H}" rx="18" fill="{BG}"/><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="17" fill="none" stroke="url(#g)" stroke-opacity=".45" stroke-width="2"/>']
n = 0
for li, (name, col, items) in enumerate(LANES):
    y = TOP + li * (LH + GAP)
    o.append(f'<rect x="16" y="{y}" width="{W-32}" height="{LH}" rx="14" fill="{col}" fill-opacity=".05" stroke="{col}" stroke-opacity=".35"/>')
    o.append(f'<rect x="16" y="{y+18}" width="4" height="{LH-36}" rx="2" fill="{col}"/>')
    o.append(f'<text x="38" y="{y+54}" font-family="{FONT}" font-size="15" font-weight="800" letter-spacing="3" fill="{col}">{name}</text>'
             f'<text x="38" y="{y+76}" font-family="{FONT}" font-size="12" fill="#64748B">{len(items):02d} systems</text>')
    for i, (key, label) in enumerate(items):
        cx = 232 + i * 82 + 41
        dur, begin = 3 + (n % 5) * 0.4, (n % 7) * 0.35
        n += 1
        o.append(f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -5;0 0" dur="{dur:.1f}s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
                 f'<rect x="{cx-30}" y="{y+17}" width="60" height="60" rx="16" fill="{col}" fill-opacity=".12"/>'
                 f'<image x="{cx-(18 if key in SIMPLE else 26)}" y="{y+(29 if key in SIMPLE else 21)}" width="{36 if key in SIMPLE else 52}" height="{36 if key in SIMPLE else 52}" xlink:href="data:image/svg+xml;base64,{icon(key)}"/></g>'
                 f'<text x="{cx}" y="{y+98}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="#CBD5E1">{label}</text>')
o.append('</svg>')
open("assets/stack.svg", "w").write("".join(o))
print("wrote assets/stack.svg", len("".join(o)) // 1024, "KB")
