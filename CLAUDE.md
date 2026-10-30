# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

The GitHub profile repo (`Rishivardhan-J/Rishivardhan-J`). `README.md` is the profile page; almost every visual in it is a generated SVG. There is no build system, test suite or linter. The only code is the Python generators in `scripts/` (stdlib only) and one GitHub Actions workflow.

## Two kinds of generated SVGs (this is the key thing to know)

1. **Static assets, committed to `main` under `assets/`.** Regenerate locally and commit the output (run from the repo root, since paths are relative):
   - `python3 scripts/build_assets.py`: header, marquee, divider, footer, `mission-*.svg` cards, `btn-*.svg` / `pill-*.svg` buttons. Seeded RNG, so output is deterministic.
   - `python3 scripts/build_panels.py`: `briefing.svg` (terminal + about card) and `milestones.svg`.
   - `python3 scripts/build_stack.py`: `stack.svg`. Needs network: it fetches icons from skillicons.dev / cdn.simpleicons.org and embeds them as base64.
2. **Live data SVGs, built by CI and published to the `output` branch, never committed to `main`.** `scripts/build_stats.py <stats.svg> <flight.svg>` calls the GitHub GraphQL API (needs `GH_TOKEN`; locally use `GH_TOKEN=$(gh auth token)`) and writes the stats dashboard and the flight-deck HUD. The README references them via `raw.githubusercontent.com/.../output/github-stats.svg` and `github-flight.svg`, so they will not show up in a local render of the README.

`.github/workflows/profile-visuals.yml` runs daily (00:00 UTC), on manual dispatch, and on pushes to `main` that touch `.github/workflows/**` or `scripts/**`. It generates the contribution-snake SVGs (Platane/snk, colours set in the `outputs:` query strings), runs `build_stats.py`, then publishes the whole `dist/` folder to `output` in one step with `crazy-max/ghaction-github-pages`. That step replaces the branch contents, so every file the README needs from `output` must be written into `dist/` in the same job. Changes to assets under `assets/` don't need CI; they're served straight from `main`.

`METRICS_TOKEN` (a repo secret) lets `build_stats.py` count private contributions; without it the job falls back to `GITHUB_TOKEN` and the numbers are lower.

## Design system

`scripts/palette.py` is the single source of truth for colours (the Starlight palette: one ice-blue accent plus muted gold on `#0B0F19`), the shared font, `GRAD_STOPS`, the `HEAT` and `RAMP` ramps and a WCAG `contrast()` helper. `python3 scripts/palette.py` exits non-zero if any colour pair drops below its threshold; run it after changing colours. The generators import from it by inserting their own directory in `sys.path`. Don't hardcode hex in the generators. The snake colours in the workflow and the typing-SVG and badge colours in `README.md` can't import it, so keep them in sync by hand.

Rules:
- One accent only. `AC` is for links, labels, key numbers and primary buttons; don't give sections or chips their own hues.
- `AC_D` is for fills and strokes only. Small text must use `tx(colour)`, which maps it to `AC`.
- `SIG` (gold) is reserved for achievements and availability: FINALIST, OPEN TO WORK, LIVE, best day.
- Muted text is `MUTED`.
- Keep one filled primary button per group; the others are outlined.
- Don't use shields.io badges for coloured buttons: they always print white text. Use the SVG buttons from `build_assets.py`.
- The tag `pre-starlight` (and `pre-starlight-output`) holds the previous multi-colour design.

## Stats panel (`github-stats.svg`)

Built by the first half of `build_stats.py` as a star chart plus a language solar system (the Flight Deck above it is the radar/gauge panel; keep the two visually distinct).
- Rank comes from all-time contributions via the `RANKS` ladder (CADET 0, PILOT 100, NAVIGATOR 300, COMMANDER 1000, ADMIRAL 3000).
- Star chart: `x` is the real date; height within the band is decorative (a smooth wave plus a hash of the date), and the on-image caption says so. Lines join active days less than a week apart. Don't present the height as data.
- Solar system: planets rotate (SMIL), so they can't carry labels. Static ring numbers `01-06` match the legend. Planet size is share of code; legend bars are relative to the top language.
- Numbers use size steps by digit count (tiles and hero) so six-figure counts don't overflow. Test layout changes against other accounts with `PROFILE_USER=torvalds` (huge) and `PROFILE_USER=octocat` (zero activity), not just this profile.
- Rollback tags: `pre-starlight`, `pre-stats-redesign`.

## SVG gotchas hit in this repo

- Gradients on zero-height shapes (horizontal lines) don't render with the default `objectBoundingBox` units; use `gradientUnits="userSpaceOnUse"` (see `GRAD` / `#g`).
- Don't rely on SMIL fade-ins that start at `opacity="0"`: content must be visible by default. Animations here only loop (pulse, drift, rotate).
- SVGs are rendered via `<img>`, so they can't load external resources; embed images as `data:` URIs.
- Text width is not known at generation time (font fallback varies). Use fixed-width cells / `text-anchor` instead of measuring, and keep long strings well inside their boxes.
- Text colours/sizes in `build_panels.py`'s code block come from a small hand-written tokenizer (`colorize`), not a real highlighter.

## Previewing

Headless Chrome is available (`google-chrome --headless --no-sandbox --screenshot=out.png file://...`) and works for checking SVGs, including SMIL. To preview the whole README, render it with `gh api markdown -f text="$(cat README.md)" -f mode=markdown` (use `mode=markdown`, not `gfm`, which turns newlines into `<br>` and misrepresents inline image rows) inside a dark-background HTML page with `<base href="file://$PWD/">`.

## README conventions

- Section order and visuals are described by the `assets/` files; the README itself is mostly `<img>` tags with `alt` text, so keep alt text meaningful when swapping an image.
- Project links are `github.com/Rishivardhan-J/<Repo>`; the portfolio is `rishi-galaxy.vercel.app` (the old `rishi-j-portfolio.vercel.app` is no longer linked).
- Competition results are worded "Finalist", not "Runner-up".
- Commit messages end with the `Co-Authored-By` line given in the session's attribution reminder.
