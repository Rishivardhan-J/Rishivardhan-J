"""Single source of truth for the aurora palette + a WCAG contrast helper.

Roles: cyan = primary/interactive, violet = structure, pink = highlight,
amber = status/achievement only, green = online/live only, blue = tools/secondary.
"""
CY, VI, PK, AM = "#22D3EE", "#8B5CF6", "#F472B6", "#FBBF24"
GR, BL = "#34D399", "#60A5FA"
BG = "#070A1A"
VI_T = "#A78BFA"      # violet for SMALL text (plain #8B5CF6 is only 4.1:1 on its tint)
TEXT, SOFT, DIM, MUTED = "#E2E8F0", "#CBD5E1", "#94A3B8", "#8B9BB4"
HEAT = ["#121A33", "#0e5a70", "#0e7490", CY, "#A5F3FC"]   # monotonic: each step lighter
FONT = "Fira Code, Consolas, monospace"


def tx(c):
    """Text-safe version of an accent colour."""
    return VI_T if c == VI else c


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
    for n, c in [("cyan", CY), ("violet-text", VI_T), ("pink", PK), ("amber", AM), ("green", GR), ("blue", BL), ("text", TEXT), ("soft", SOFT), ("dim", DIM), ("muted", MUTED)]:
        check(f"{n} on bg", c, BG, 4.5)
    for n, c in [("cyan", CY), ("violet-text", VI_T), ("pink", PK), ("amber", AM), ("blue", BL)]:
        check(f"{n} on its 14% tint", c, mix(c, BG, .14), 4.5)
    check("muted on violet 6% card", MUTED, mix(VI, BG, .06), 4.5)
    check("violet stroke/large text on bg", VI, BG, 3)
    prev = None
    for i, h in enumerate(HEAT):
        if prev: check(f"heat step {i-1}->{i} lightness", h, prev, 1.3)
        prev = h
    check("white on badge violet 7C3AED", "#ffffff", "#7C3AED", 4.5)
    check("light snake pink on white", "#DB2777", "#ffffff", 4.5)
    raise SystemExit(1 if bad else 0)
