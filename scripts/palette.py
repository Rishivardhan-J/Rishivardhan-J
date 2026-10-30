"""Single source of truth for the Starlight palette + a WCAG contrast helper.

Roles: AC = the one accent (links, labels, key numbers, primary buttons),
AC_D = fills and strokes only, AC_L = highlights,
SIG = achievements and availability only. Tech logos and emoji keep their own colours.
"""
AC, AC_D, AC_L, SIG = "#8FB8F0", "#5B82C2", "#C4DAF8", "#E6C07B"
BG, PANEL, TRACK = "#0B0F19", "#0F1522", "#182133"
TEXT, SOFT, DIM, MUTED = "#E6EAF2", "#C9D1DE", "#9AA5B8", "#8D99AD"
HEAT = [TRACK, "#2B4266", "#4A70A8", AC, "#D6E5FB"]   # monotonic: each step lighter
RAMP = [AC_L, AC, "#6F9BDD", AC_D, "#476A9F", "#3A5680", "#6B7485"]   # languages by rank; last is neutral "Other"
GRAD_STOPS = f'<stop offset="0" stop-color="{AC_L}"/><stop offset=".5" stop-color="{AC}"/><stop offset="1" stop-color="{AC_L}"/>'
STAR_PEAK = ".5"      # stars stay dim so they don't compete with text
FONT = "Fira Code, Consolas, monospace"


def tx(c):
    """Text-safe version of an accent colour."""
    return AC if c == AC_D else c


def _lum(h):
    h = h.lstrip("#")
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def contrast(a, b):
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + .05) / (lo + .05)


def mix(fg, bg, alpha):
    f = [int(fg[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(bg[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(alpha * x + (1 - alpha) * y) for x, y in zip(f, b))


if __name__ == "__main__":
    bad = 0
    def check(name, fg, bg, need):
        global bad
        r = contrast(fg, bg)
        ok = r >= need
        bad += not ok
        print(f"{'ok ' if ok else 'FAIL'} {r:5.2f} (need {need})  {name}")
    for n, c in [("accent", AC), ("light", AC_L), ("signal", SIG), ("text", TEXT), ("soft", SOFT), ("dim", DIM), ("muted", MUTED)]:
        check(f"{n} on bg", c, BG, 4.5)
    for n, c in [("accent", AC), ("signal", SIG)]:
        check(f"{n} on its 14% tint", c, mix(c, BG, .14), 4.5)
    check("bg on accent button", BG, AC, 4.5)
    check("muted on accent 6% card", MUTED, mix(AC, BG, .06), 4.5)
    check("muted on panel", MUTED, PANEL, 4.5)
    check("deep accent stroke on bg", AC_D, BG, 3)
    prev = None
    for i, h in enumerate(HEAT):
        if prev: check(f"heat step {i-1}->{i} lightness", h, prev, 1.3)
        prev = h
    for i in range(len(RAMP) - 1):
        check(f"language ramp {i}->{i+1} separation", RAMP[i], RAMP[i + 1], 1.2)
    for i, h in enumerate(RAMP):
        check(f"language {i} legend dot on bg", h, BG, 2.5)
    check("typing line on GitHub dark (large text)", AC_D, "#0d1117", 3)
    check("typing line on GitHub light (large text)", AC_D, "#ffffff", 3)
    check("white on badge blue 3F66A6", "#ffffff", "#3F66A6", 4.5)
    check("light snake gold on white", "#8A6116", "#ffffff", 4.5)
    check("dark snake gold on bg", SIG, BG, 4.5)
    raise SystemExit(1 if bad else 0)
