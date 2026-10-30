"""Builds stack.svg (CI): a single-colour toolkit panel, with real evidence of use read from the owner's repos.

usage: build_stack.py <out-dir>      (needs GH_TOKEN; fetches icons from skillicons.dev / simpleicons.org and embeds them)
"""
import base64, html, json, math, os, re, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(__file__))
from palette import AC, AC_L, BG, TRACK, SOFT, MUTED, FONT, GRAD_STOPS
from ghdata import SCAFFOLD, USER, rest

DIST = sys.argv[1]
esc = html.escape
LANES = [
    ("LANGUAGES", [("js", "JavaScript"), ("ts", "TypeScript"), ("py", "Python"), ("java", "Java"), ("cpp", "C++"), ("c", "C"), ("dart", "Dart"), ("html", "HTML"), ("css", "CSS")]),
    ("FRAMEWORKS", [("react", "React"), ("nodejs", "Node.js"), ("express", "Express"), ("django", "Django"), ("flask", "Flask"), ("fastapi", "FastAPI"), ("spring", "Spring"), ("flutter", "Flutter"), ("tailwind", "Tailwind"), ("vite", "Vite"), ("jquery", "jQuery")]),
    ("DATA", [("postgres", "PostgreSQL"), ("mysql", "MySQL"), ("mongodb", "MongoDB"), ("firebase", "Firebase"), ("sqlite", "SQLite"), ("numpy", "NumPy"), ("pandas", "Pandas")]),
    ("TOOLS", [("git", "Git"), ("github", "GitHub"), ("vscode", "VS Code"), ("linux", "Linux"), ("docker", "Docker"), ("kubernetes", "K8s"), ("vercel", "Vercel"), ("netlify", "Netlify"), ("postman", "Postman"), ("figma", "Figma")]),
]
SIMPLE = {"numpy": "4DABCF", "pandas": "E70488"}  # not in skillicons -> Simple Icons

# ------------------------------------------------------------------ evidence of use
LANGKEY = {"JavaScript": "js", "TypeScript": "ts", "Python": "py", "Java": "java", "C++": "cpp", "C": "c", "Dart": "dart", "HTML": "html", "CSS": "css", "Dockerfile": "docker"}
PKG = {"react": "react", "react-dom": "react", "vite": "vite", "tailwindcss": "tailwind", "express": "express", "jquery": "jquery", "typescript": "ts",
       "firebase": "firebase", "firebase-admin": "firebase", "firebase_core": "firebase", "firebase_auth": "firebase", "cloud_firestore": "firebase",
       "mongoose": "mongodb", "mongodb": "mongodb", "pymongo": "mongodb", "pg": "postgres", "postgres": "postgres", "psycopg2": "postgres",
       "psycopg2-binary": "postgres", "psycopg": "postgres", "asyncpg": "postgres", "mysql": "mysql", "mysql2": "mysql", "mysql-connector-python": "mysql",
       "pymysql": "mysql", "sqlite3": "sqlite", "better-sqlite3": "sqlite", "sqflite": "sqlite", "numpy": "numpy", "pandas": "pandas",
       "flask": "flask", "django": "django", "fastapi": "fastapi", "node": "nodejs", "flutter": "flutter"}
FILES = {"Dockerfile": "docker", "docker-compose.yml": "docker", "vercel.json": "vercel", "netlify.toml": "netlify"}
MANIFESTS = {"package.json", "pubspec.yaml", "requirements.txt", "pyproject.toml", "pom.xml"} | set(FILES)
SKIP_DIRS = {"node_modules", ".git", "build", "android", "ios", "macos", "windows", "linux", ".dart_tool", "venv", ".venv"}


def packages(base, text):
    out = set()
    if base == "package.json":
        j = json.loads(text)
        out |= set(j.get("dependencies", {})) | set(j.get("devDependencies", {})) | {"node"}
    elif base == "pubspec.yaml":
        sect = False
        for ln in text.splitlines():
            if re.match(r"^(dependencies|dev_dependencies):", ln):
                sect = True
            elif re.match(r"^\S", ln):
                sect = False
            elif sect and (m := re.match(r"^\s{2}([a-z0-9_]+):", ln)):
                out.add(m.group(1))
    elif base == "requirements.txt":
        out |= {re.split(r"[=<>~\[; ]", ln.strip())[0].lower() for ln in text.splitlines() if ln.strip() and not ln.startswith("#")}
    elif base == "pyproject.toml":
        out |= {m.lower() for m in re.findall(r'"([A-Za-z0-9_.-]+)(?:[<>=~\[ ;][^"]*)?"', text)}
    elif base == "pom.xml":
        out |= set(re.findall(r"<artifactId>([^<]+)</artifactId>", text))
        if any(a.startswith("spring-boot") for a in out):
            out.add("spring")
    return out


def scan(r):
    """keys found in one repo, or None if it can't be read (empty repos answer 409)."""
    keys, name = {"git", "github"}, r["name"]
    try:
        langs = rest(f"repos/{USER}/{name}/languages")
        top = max(langs, key=langs.get) if langs else None
        for lang in langs:
            if not (top == "Dart" and lang in SCAFFOLD) and lang in LANGKEY:
                keys.add(LANGKEY[lang])
        if "vercel.app" in (r.get("homepage") or ""):
            keys.add("vercel")
        tree = rest(f"repos/{USER}/{name}/git/trees/HEAD?recursive=1").get("tree", [])
        found = [t["path"] for t in tree if t["type"] == "blob" and t["path"].rsplit("/", 1)[-1] in MANIFESTS
                 and t["path"].count("/") <= 2 and not (set(t["path"].split("/")[:-1]) & SKIP_DIRS)]
        for path in found[:8]:
            base = path.rsplit("/", 1)[-1]
            if base in FILES:
                keys.add(FILES[base])
                continue
            try:
                text = base64.b64decode(rest(f"repos/{USER}/{name}/contents/{path}")["content"]).decode("utf8", "replace")
                keys |= {PKG[p] for p in packages(base, text) if p in PKG}
            except Exception as e:
                print(f"  skip {name}/{path}: {e}")
        return keys
    except urllib.error.HTTPError as e:
        if e.code != 409:
            print(f"  skip repo {name}: {e}")
    except Exception as e:
        print(f"  skip repo {name}: {e}")
    return None


def evidence():
    """key -> number of owned, non-fork repos where it was found; and how many repos could be read."""
    repos = [r for r in rest(f"users/{USER}/repos?per_page=100&type=owner") if not r["fork"]]
    with ThreadPoolExecutor(8) as ex:
        results = [k for k in ex.map(scan, repos) if k is not None]
    counts = {}
    for keys in results:
        for k in keys:
            counts[k] = counts.get(k, 0) + 1
    return counts, len(results)


# ------------------------------------------------------------------ icons
def icon(i):
    url = f"https://cdn.simpleicons.org/{i}/{SIMPLE[i]}" if i in SIMPLE else f"https://skillicons.dev/icons?i={i}&theme=dark"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "stack-build"})
            return base64.b64encode(urllib.request.urlopen(req, timeout=20).read()).decode()
        except Exception as e:
            print(f"  icon {i} attempt {attempt + 1} failed: {e}")
            time.sleep(1.5)
    return None


def rgb(h):
    return [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]


lo, hi = rgb(TRACK), rgb(AC_L)
mid = [a + (b - a) * .78 for a, b in zip(lo, hi)]   # lifted midpoint: dark glyphs stay readable
MODE = os.environ.get("ICON_MODE", "duo")
if MODE == "duo":   # luminance -> palette ramp, so every logo shares one colour family
    FILTER = (f'<filter id="duo" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
              f'<feColorMatrix type="matrix" values=".34 .33 .33 0 0 .34 .33 .33 0 0 .34 .33 .33 0 0 0 0 0 1 0"/>'
              f'<feComponentTransfer><feFuncR type="table" tableValues="{lo[0]:.3f} {mid[0]:.3f} {hi[0]:.3f}"/><feFuncG type="table" tableValues="{lo[1]:.3f} {mid[1]:.3f} {hi[1]:.3f}"/>'
              f'<feFuncB type="table" tableValues="{lo[2]:.3f} {mid[2]:.3f} {hi[2]:.3f}"/></feComponentTransfer></filter>')
else:               # softer: keep some of the original hue
    FILTER = '<filter id="duo" color-interpolation-filters="sRGB"><feColorMatrix type="saturate" values=".22"/></filter>'

# ------------------------------------------------------------------ layout
counts, scanned = evidence()
with ThreadPoolExecutor(8) as ex:
    ICONS = dict(zip([k for _, items in LANES for k, _ in items], ex.map(icon, [k for _, items in LANES for k, _ in items])))
total = sum(len(items) for _, items in LANES)
used_total = sum(1 for _, items in LANES for k, _ in items if counts.get(k))
W, HEAD, LH, GAP, TOP = 1200, 76, 124, 12, 16
H = HEAD + len(LANES) * LH + (len(LANES) - 1) * GAP + TOP
o = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">'
     f'<title>Toolkit</title><desc>{total} technologies, {used_total} found in the owner\'s repositories.</desc>',
     f'<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0">{GRAD_STOPS}</linearGradient>{FILTER}</defs>',
     f'<rect width="{W}" height="{H}" rx="18" fill="{BG}"/><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="17" fill="none" stroke="url(#g)" stroke-opacity=".45" stroke-width="2"/>']
sub = (f"evidence read from {scanned} repositories: languages, package manifests, Dockerfiles" if used_total else "no repository evidence found yet")
o.append(f'<text x="40" y="38" font-family="{FONT}" font-size="13" letter-spacing="3" fill="{AC}">TOOLKIT · {total} SYSTEMS{f" · {used_total} IN ACTIVE USE" if used_total else ""}</text>'
         f'<text x="40" y="58" font-family="{FONT}" font-size="10" fill="{MUTED}">{sub}</text>'
         f'<rect x="936" y="26" width="24" height="24" rx="7" fill="{AC}" fill-opacity=".1" stroke="{AC}" stroke-opacity=".7" stroke-width="1.5"/>'
         f'<text x="970" y="42" font-family="{FONT}" font-size="10" fill="{SOFT}">FOUND IN MY REPOS</text>'
         f'<rect x="1086" y="27" width="28" height="15" rx="7.5" fill="{BG}" stroke="{AC}" stroke-opacity=".7"/>'
         f'<text x="1100" y="38" text-anchor="middle" font-family="{FONT}" font-size="9" font-weight="800" fill="{AC}">×N</text>'
         f'<text x="1122" y="42" font-family="{FONT}" font-size="10" fill="{SOFT}">REPOS</text>')
for li, (name, items) in enumerate(LANES):
    y = HEAD + li * (LH + GAP)
    used = sum(1 for k, _ in items if counts.get(k))
    o.append(f'<rect x="16" y="{y}" width="{W-32}" height="{LH}" rx="14" fill="{AC}" fill-opacity=".04" stroke="{AC}" stroke-opacity=".22"/>'
             f'<rect x="16" y="{y+18}" width="4" height="{LH-36}" rx="2" fill="{AC}"/>'
             f'<text x="38" y="{y+52}" font-family="{FONT}" font-size="15" font-weight="800" letter-spacing="3" fill="{AC}">{name}</text>'
             f'<text x="38" y="{y+73}" font-family="{FONT}" font-size="11" fill="{MUTED}">{used:02d}/{len(items):02d} IN USE</text>'
             f'<rect x="38" y="{y+84}" width="130" height="5" rx="2.5" fill="{TRACK}"/><rect x="38" y="{y+84}" width="{130 * used / len(items):.1f}" height="5" rx="2.5" fill="{AC}"/>')
    pts = [(232 + i * 82 + 41, y + 52 + 9 * math.sin(i * .85 + li * 1.3)) for i in range(len(items))]
    o.append(f'<polyline points="{" ".join(f"{x:.1f},{yy:.1f}" for x, yy in pts)}" fill="none" stroke="{AC}" stroke-opacity=".22" stroke-dasharray="2 5"/>')
    for i, ((key, label), (cx, cy)) in enumerate(zip(items, pts)):
        n = counts.get(key, 0)
        ring = f'stroke="{AC}" stroke-opacity=".75" stroke-width="1.5"' if n else f'stroke="{AC}" stroke-opacity=".15"'
        o.append(f'<rect x="{cx-30:.1f}" y="{cy-30:.1f}" width="60" height="60" rx="16" fill="{AC}" fill-opacity="{.14 if n else .08}" {ring}>'
                 + (f'<animate attributeName="stroke-opacity" values=".75;.3;.75" dur="{3 + (i % 4) * .5:.1f}s" repeatCount="indefinite"/>' if n else "") + '</rect>')
        b64 = ICONS[key]
        if b64:
            s = 34 if key in SIMPLE else 46
            o.append(f'<image x="{cx - s / 2:.1f}" y="{cy - s / 2:.1f}" width="{s}" height="{s}" filter="url(#duo)" xlink:href="data:image/svg+xml;base64,{b64}"/>')
        else:
            o.append(f'<text x="{cx:.1f}" y="{cy + 5:.1f}" text-anchor="middle" font-family="{FONT}" font-size="15" font-weight="800" fill="{AC}">{esc(label[:2])}</text>')
        if n:
            bw = 14 + len(str(n)) * 6
            o.append(f'<rect x="{cx + 30 - bw + 4:.1f}" y="{cy - 36:.1f}" width="{bw}" height="15" rx="7.5" fill="{BG}" stroke="{AC}" stroke-opacity=".7"/>'
                     f'<text x="{cx + 30 - bw / 2 + 4:.1f}" y="{cy - 25:.1f}" text-anchor="middle" font-family="{FONT}" font-size="9" font-weight="800" fill="{AC}">×{n}</text>')
        o.append(f'<text x="{cx:.1f}" y="{cy + 48:.1f}" text-anchor="middle" font-family="{FONT}" font-size="10.5" fill="{SOFT}">{esc(label)}</text>')
o.append("</svg>")
open(os.path.join(DIST, "stack.svg"), "w", encoding="utf8").write("".join(o))
print(f"wrote stack.svg {len(''.join(o)) // 1024} KB; {used_total}/{total} in use across {scanned} repos; icon mode {MODE}")
print("evidence:", ", ".join(f"{k}×{v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1])))
