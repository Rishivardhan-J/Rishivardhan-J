"""Builds flagship.svg and the five mission cards from live GitHub data (run by CI).

usage: build_missions.py <out-dir>      (needs GH_TOKEN)
"""
import datetime as dt, html, json, math, os, random, sys, textwrap, urllib.error, urllib.request, zlib

sys.path.insert(0, os.path.dirname(__file__))
from palette import AC, AC_D, AC_L, SIG, BG, PANEL, TRACK, TEXT, SOFT, DIM, MUTED, FONT, GRAD_STOPS, RAMP
from ghdata import SCAFFOLD

DIST = sys.argv[1]
USER = os.environ.get("PROFILE_USER", "Rishivardhan-J")
TOKEN = os.environ["GH_TOKEN"]
esc = html.escape

FLAGSHIP = dict(name="Galaxy", url=os.environ.get("FLAGSHIP_URL", "https://rishi-galaxy.vercel.app"), stack="React · Vite · TypeScript",
                desc="A no-scroll, space-themed portfolio where you travel between projects, skills and contact through warp transitions.")
STAGES = ["DESIGN", "BUILD", "ACTIVE", "LIVE"]
MISSIONS = [  # editorial: pitch, stack and stage (1-4) are written by hand; everything else comes from GitHub
    dict(key="trackit", name="TrackIt", stage=3, status="ACTIVE", w=580, stack="React · TypeScript",
         desc="Deadline-driven tracker for internship & hackathon applications, with an admin pipeline to post and moderate listings."),
    dict(key="bench", name="Bench", stage=3, status="ACTIVE", w=580, stack="React · TypeScript",
         desc="Intelligent, high-performance freelancer discovery by skills, availability and project needs."),
    dict(key="forge", name="Forge", stage=2, status="BUILDING", w=380, stack="Flutter · Dart",
         desc="Habit-formation app built on the framework from Atomic Habits."),
    dict(key="harvestpro", name="HarvestPro", stage=2, status="BUILDING", w=380, stack="Flutter · AI",
         desc="Turns AI crop predictions into advice Indian farmers can trust and act on, in their own language."),
    dict(key="transit", name="Transit", stage=2, status="BUILDING", w=380, stack="Python · ML · VRP",
         desc="Real-time logistics optimization: ML delivery-time prediction and Hybrid Genetic Search routing."),
]


# ------------------------------------------------------------------ data
def fetch():
    frag = ('{ pushedAt stargazerCount defaultBranchRef{target{... on Commit{history{totalCount}}}} '
            'languages(first:12,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}} }')
    names = [FLAGSHIP["name"]] + [m["name"] for m in MISSIONS]
    fields = " ".join(f'r{i}: repository(name:"{n}") {frag}' for i, n in enumerate(names))
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": "query($l:String!){user(login:$l){" + fields + "}}", "variables": {"l": USER}}).encode(),
                                 headers={"Authorization": f"bearer {TOKEN}", "User-Agent": "profile-stats"})
    res = json.load(urllib.request.urlopen(req, timeout=30))
    if not res.get("data") or not res["data"].get("user"):
        sys.exit(f"graphql failed: {res.get('errors')}")
    bad = [e for e in res.get("errors", []) if e.get("type") != "NOT_FOUND"]   # a missing repo just renders as dashes
    if bad:
        sys.exit(f"graphql errors: {bad}")
    return dict(zip(names, (res["data"]["user"][f"r{i}"] for i in range(len(names)))))


def lang_mix(repo):
    if not repo:
        return []
    edges = [(e["node"]["name"], e["size"]) for e in repo["languages"]["edges"]]
    if edges and edges[0][0] == "Dart":
        edges = [e for e in edges if e[0] not in SCAFFOLD]
    tot = sum(s for _, s in edges) or 1
    top = edges[:3]
    rest = tot - sum(s for _, s in top)
    return [(n, s / tot) for n, s in top] + ([("Other", rest / tot)] if rest / tot > .005 else [])


def ago(iso):
    days = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))).days
    return "TODAY" if days < 1 else f"{days}D AGO" if days < 60 else f"{days // 30}MO AGO"


def commits(repo):
    try:
        return repo["defaultBranchRef"]["target"]["history"]["totalCount"]
    except (TypeError, KeyError):
        return None


def site_online(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "profile-stats"}), timeout=15) as r:
            return r.status < 400
    except urllib.error.HTTPError as e:
        return e.code < 400
    except Exception:
        return False


def short(n, k=10):
    return n if len(n) <= k else n[:k - 1] + "…"


def col(i, n):
    return RAMP[-1] if n == "Other" else RAMP[min(i, len(RAMP) - 2)]


# ------------------------------------------------------------------ shared drawing
def defs(w, h, extra=""):
    return (f'<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{w}" y2="0">{GRAD_STOPS}</linearGradient>'
            f'<radialGradient id="gl"><stop offset="0" stop-color="{AC_D}" stop-opacity=".22"/><stop offset="1" stop-color="{AC_D}" stop-opacity="0"/></radialGradient>{extra}</defs>')


def dust(rng, n, w, h):
    return "".join(f'<circle cx="{rng.uniform(8, w - 8):.1f}" cy="{rng.uniform(8, h - 8):.1f}" r="{rng.choice([.6, .9, 1.2]):.1f}" fill="{TEXT}" fill-opacity="{rng.uniform(.12, .32):.2f}"/>'
                   for _ in range(n))


def langbar(x, y, w, mix, legend_y, size=10):
    if not mix:
        return f'<text x="{x}" y="{legend_y}" font-family="{FONT}" font-size="{size}" fill="{MUTED}">NO LANGUAGE DATA</text>'
    s = f'<rect x="{x}" y="{y}" width="{w}" height="6" rx="3" fill="{TRACK}"/><g clip-path="url(#lb{x})">'
    s = f'<clipPath id="lb{x}"><rect x="{x}" y="{y}" width="{w}" height="6" rx="3"/></clipPath>' + s
    cx = float(x)
    for i, (n, f) in enumerate(mix):
        sw = w * f
        s += f'<rect x="{cx:.1f}" y="{y}" width="{max(sw - 2, 1):.1f}" height="6" fill="{col(i, n)}"/>'
        cx += sw
    s += "</g>"
    step = w / 3
    for i, (n, f) in enumerate([m for m in mix if m[0] != "Other"][:3]):
        s += (f'<circle cx="{x + i * step + 3:.1f}" cy="{legend_y - 3}" r="3" fill="{col(i, n)}"/>'
              f'<text x="{x + i * step + 11:.1f}" y="{legend_y}" font-family="{FONT}" font-size="{size}" fill="{DIM}">{esc(short(n))} {"&lt;1" if f < .01 else round(100 * f)}%</text>')
    return s


# unique mission patches: stroke glyphs drawn around (0,0), roughly +-16
def glyph(kind):
    st = f'fill="none" stroke="{AC_L}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "trackit":
        g = f'<rect x="-12" y="-15" width="24" height="30" rx="4" {st}/>'
        for y in (-7, 1, 9):
            g += f'<path d="M-7,{y}l2,2l4,-4M1,{y}h7" {st}/>'
    elif kind == "bench":
        g = (f'<circle cx="-2" cy="-2" r="11" {st}/><path d="M6,6L14,14" {st}/><circle cx="-2" cy="-6" r="3" {st}/>'
             f'<path d="M-8,4a6,5 0 0 1 12,0" {st}/>')
    elif kind == "forge":
        g = (f'<path d="M-15,-5H12L16,-9V-1H11C7,-1 6,3 6,6V10H10V14H-10V10H-6V6C-6,2 -9,-1 -15,-1Z" {st}/>'
             f'<path d="M-4,-10L-6,-15M2,-10V-16M8,-12L11,-16" {st}/>')
    elif kind == "harvestpro":
        g = f'<path d="M0,15V-12" {st}/><ellipse cx="0" cy="-15" rx="2" ry="4" {st}/>'
        for y in (-7, 0, 7):
            g += (f'<ellipse cx="-5" cy="{y}" rx="5" ry="2.4" transform="rotate(-35 -5 {y})" {st}/>'
                  f'<ellipse cx="5" cy="{y}" rx="5" ry="2.4" transform="rotate(35 5 {y})" {st}/>')
    elif kind == "transit":
        g = f'<path d="M-12,10L-4,-8L6,2L13,-10" {st} stroke-dasharray="3 3"/>'
        for x, y in ((-12, 10), (-4, -8), (6, 2)):
            g += f'<circle cx="{x}" cy="{y}" r="3" {st}/>'
        g += f'<circle cx="13" cy="-10" r="4" fill="{AC_L}"/>'
    else:  # galaxy
        g = (f'<ellipse rx="15" ry="6" transform="rotate(-25)" {st}/><ellipse rx="9" ry="3.5" transform="rotate(-25)" {st}/>'
             f'<circle r="2.5" fill="{AC_L}"/><circle cx="-12" cy="-9" r="1" fill="{AC_L}"/><circle cx="11" cy="9" r="1" fill="{AC_L}"/>')
    return g


def patch(cx, cy, kind):
    return (f'<circle cx="{cx}" cy="{cy}" r="34" fill="{AC_D}" fill-opacity=".14" stroke="{AC}" stroke-opacity=".55" stroke-dasharray="3 5">'
            f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="22s" repeatCount="indefinite"/></circle>'
            f'<circle cx="{cx}" cy="{cy}" r="27" fill="{BG}" stroke="{AC}" stroke-opacity=".35"/><g transform="translate({cx} {cy})">{glyph(kind)}</g>')


# ------------------------------------------------------------------ mission card
def card(m, repo):
    w, h = m["w"], 282
    rng = random.Random(zlib.crc32(m["key"].encode()))
    o = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg"><title>{m["name"]}</title>'
         f'<desc>{esc(m["desc"])} {m["status"]}.</desc>', defs(w, h),
         f'<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="16" fill="{BG}" stroke="url(#g)" stroke-opacity=".5" stroke-width="2"/>',
         f'<circle cx="60" cy="56" r="150" fill="url(#gl)"/>{dust(rng, 12, w, h)}', patch(60, 58, m["key"]),
         f'<text x="108" y="54" font-family="{FONT}" font-size="24" font-weight="800" fill="url(#g)">{m["name"]}</text>'
         f'<text x="108" y="75" font-family="{FONT}" font-size="12" fill="{DIM}">{esc(m["stack"])}</text>']
    pw = 26 + len(m["status"]) * 8.2
    o.append(f'<rect x="{w - pw - 18:.1f}" y="22" width="{pw:.1f}" height="24" rx="12" fill="{AC}" fill-opacity=".12" stroke="{AC}" stroke-opacity=".6"/>'
             f'<circle cx="{w - pw - 6:.1f}" cy="34" r="3.5" fill="{AC}"><animate attributeName="opacity" values="1;.25;1" dur="2s" repeatCount="indefinite"/></circle>'
             f'<text x="{w - pw + 4:.1f}" y="38.5" font-family="{FONT}" font-size="10.5" font-weight="700" fill="{AC}">{m["status"]}</text>')
    lines = textwrap.wrap(m["desc"], int((w - 48) / (13 * .62)))
    if len(lines) > 3:   # cut at a word boundary
        lines = lines[:2] + [textwrap.shorten(" ".join(lines[2:]), width=int((w - 48) / (13 * .62)), placeholder="…")]
    for i, ln in enumerate(lines):
        o.append(f'<text x="24" y="{116 + i * 20}" font-family="{FONT}" font-size="13" fill="{TEXT}">{esc(ln)}</text>')
    sw = (w - 48 - 18) / 4                                       # four-stage track
    for i, name in enumerate(STAGES):
        x, lit, cur = 24 + i * (sw + 6), i < m["stage"], i == m["stage"] - 1
        o.append(f'<rect x="{x:.1f}" y="184" width="{sw:.1f}" height="5" rx="2.5" fill="{AC_L if cur else AC if lit else TRACK}"/>'
                 f'<text x="{x + sw / 2:.1f}" y="203" text-anchor="middle" font-family="{FONT}" font-size="9" letter-spacing="1" fill="{SOFT if lit else MUTED}">{name}</text>')
    o.append(langbar(24, 216, w - 48, lang_mix(repo), 240))
    n = commits(repo)
    tele = f'{n if n is not None else "—"} COMMITS · LAST LAUNCH {ago(repo["pushedAt"]) if repo else "—"}'
    if repo and repo["stargazerCount"]:
        tele += f' · ★ {repo["stargazerCount"]}'
    o.append(f'<line x1="24" y1="254" x2="{w - 24}" y2="254" stroke="{AC}" stroke-opacity=".18"/>'
             f'<text x="24" y="271" font-family="{FONT}" font-size="10" letter-spacing="1" fill="{MUTED}">{tele}</text>'
             f'<text x="{w - 24}" y="272" text-anchor="end" font-family="{FONT}" font-size="14" font-weight="700" fill="{AC}">↗</text></svg>')
    return "".join(o)


# ------------------------------------------------------------------ flagship
def flagship(repo, online):
    W, H = 1200, 390
    rng = random.Random(77)
    cx, cy = 300, 212
    clip = (f'<clipPath id="vp"><path d="M41,74H559V335a14,14 0 0 1 -14,14H55a14,14 0 0 1 -14,-14Z"/></clipPath>'
            f'<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>'
            f'<radialGradient id="warp"><stop offset="0" stop-color="{AC}" stop-opacity=".32"/><stop offset="1" stop-color="{AC}" stop-opacity="0"/></radialGradient>')
    o = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg"><title>Flagship: Galaxy</title>'
         f'<desc>{esc(FLAGSHIP["desc"])} Site is {"online" if online else "unreachable"}.</desc>', defs(W, H, clip),
         f'<rect width="{W}" height="{H}" rx="18" fill="{BG}"/><g clip-path="url(#card)"><circle cx="1000" cy="40" r="360" fill="url(#gl)"/>{dust(rng, 60, W, H)}</g>',
         f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="17" fill="none" stroke="url(#g)" stroke-opacity=".55" stroke-width="2"/>']
    # browser window
    o.append(f'<rect x="40" y="40" width="520" height="310" rx="14" fill="{PANEL}" stroke="{AC}" stroke-opacity=".35"/>'
             f'<path d="M40,54a14,14 0 0 1 14,-14H546a14,14 0 0 1 14,14V74H40Z" fill="{TRACK}"/>'
             + "".join(f'<circle cx="{62 + i * 18}" cy="57" r="5" fill="{MUTED}" fill-opacity=".45"/>' for i in range(3)) +
             f'<rect x="132" y="46" width="318" height="22" rx="11" fill="{BG}" stroke="{AC}" stroke-opacity=".25"/>'
             f'<rect x="146" y="55" width="7" height="6" rx="1.5" fill="none" stroke="{MUTED}"/><path d="M147.5,55v-2a2,2 0 0 1 4,0v2" fill="none" stroke="{MUTED}"/>'
             f'<text x="162" y="61" font-family="{FONT}" font-size="11" fill="{SOFT}">{FLAGSHIP["url"].split("//")[-1]}</text>'
             f'<circle cx="472" cy="57" r="4" fill="{SIG if online else MUTED}"><animate attributeName="opacity" values="1;.3;1" dur="1.8s" repeatCount="indefinite"/></circle>'
             f'<text x="482" y="61" font-family="{FONT}" font-size="9.5" font-weight="700" letter-spacing="1" fill="{SIG if online else MUTED}">{"ONLINE" if online else "OFFLINE"}</text>')
    # warp tunnel
    o.append(f'<g clip-path="url(#vp)"><circle cx="{cx}" cy="{cy}" r="150" fill="url(#warp)"/>')
    for k in range(64):
        th = 2 * math.pi * k / 64 + rng.uniform(-.03, .03)
        r0, r1 = rng.uniform(12, 46), 340
        L, dl = r1 - r0, rng.uniform(10, 30)
        o.append(f'<line x1="{cx + r0 * math.cos(th):.1f}" y1="{cy + r0 * math.sin(th):.1f}" x2="{cx + r1 * math.cos(th):.1f}" y2="{cy + r1 * math.sin(th):.1f}" stroke="{AC}" stroke-opacity=".08"/>')
        o.append(f'<line x1="{cx + r0 * math.cos(th):.1f}" y1="{cy + r0 * math.sin(th):.1f}" x2="{cx + r1 * math.cos(th):.1f}" y2="{cy + r1 * math.sin(th):.1f}" '
                 f'stroke="{AC_L if k % 4 == 0 else AC}" stroke-opacity="{rng.uniform(.3, .8):.2f}" stroke-width="{rng.choice([1, 1.2, 1.6]):.1f}" stroke-linecap="round" stroke-dasharray="{dl:.0f} {L:.0f}">'
                 f'<animate attributeName="stroke-dashoffset" values="0;{-(L + dl):.0f}" dur="{rng.uniform(1.4, 3.6):.1f}s" begin="{rng.uniform(0, 2.5):.1f}s" repeatCount="indefinite"/></line>')
    o.append(f'<text x="{cx}" y="{cy + 8}" text-anchor="middle" font-family="{FONT}" font-size="24" font-weight="800" letter-spacing="9" fill="{AC_L}" stroke="{BG}" stroke-width="5" paint-order="stroke">GALAXY</text>')
    for i, t in enumerate(("PROJECTS", "SKILLS", "CONTACT")):
        x = 160 + i * 98
        o.append(f'<rect x="{x}" y="312" width="88" height="22" rx="11" fill="{BG}" fill-opacity=".85" stroke="{AC}" stroke-opacity=".4"/>'
                 f'<text x="{x + 44}" y="327" text-anchor="middle" font-family="{FONT}" font-size="9" letter-spacing="2" fill="{AC}">{t}</text>')
    o.append("</g>")
    # dossier
    n = commits(repo)
    o.append(f'<text x="620" y="70" font-family="{FONT}" font-size="12" letter-spacing="5" fill="{AC}">FLAGSHIP MISSION</text>'
             f'<text x="618" y="132" font-family="{FONT}" font-size="58" font-weight="800" fill="url(#g)">Galaxy</text>'
             f'<text x="620" y="160" font-family="{FONT}" font-size="13" fill="{DIM}">{esc(FLAGSHIP["stack"])}</text>')
    for i, ln in enumerate(textwrap.wrap(FLAGSHIP["desc"], 56)[:3]):
        o.append(f'<text x="620" y="{198 + i * 24}" font-family="{FONT}" font-size="15" fill="{TEXT}">{esc(ln)}</text>')
    chips = [f'{n if n is not None else "—"} COMMITS', f'LAST LAUNCH {ago(repo["pushedAt"]) if repo else "—"}']
    x = 620
    for c in chips:
        cw = 26 + len(c) * 7
        o.append(f'<rect x="{x}" y="266" width="{cw:.0f}" height="26" rx="13" fill="{AC}" fill-opacity=".1" stroke="{AC}" stroke-opacity=".5"/>'
                 f'<text x="{x + cw / 2:.0f}" y="283" text-anchor="middle" font-family="{FONT}" font-size="10.5" font-weight="700" letter-spacing="1" fill="{AC}">{c}</text>')
        x += cw + 10
    o.append(langbar(620, 314, 520, lang_mix(repo), 340, 11))
    o.append(f'<text x="620" y="372" font-family="{FONT}" font-size="10" fill="{MUTED}">live data from the GitHub API · site status checked on every build</text></svg>')
    return "".join(o)


data = fetch()
online = site_online(FLAGSHIP["url"])
open(os.path.join(DIST, "flagship.svg"), "w", encoding="utf8").write(flagship(data[FLAGSHIP["name"]], online))
for m in MISSIONS:
    open(os.path.join(DIST, f"mission-{m['key']}.svg"), "w", encoding="utf8").write(card(m, data[m["name"]]))
print("wrote flagship + %d mission cards; site online: %s" % (len(MISSIONS), online))
