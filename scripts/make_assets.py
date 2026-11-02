"""Generate every SVG panel used by the profile README.

The look follows blazexyz.com: everything is drawn in dots on a near-black violet ground,
lettering uses the site's Exypnos dot font with its pale-pink-to-violet gradient, and each
panel wears the site's camera HUD (corner brackets, solid tags, pips, readouts, a barcode).
The three scenes from the site appear too: the black hole up top, the spiral galaxy behind
the about panel, and the night highway in the footer.

GitHub shows these files through <img>, so they can't load web fonts or scripts. Lettering
that matters is drawn as dots, and animation is plain CSS that stops for visitors who prefer
reduced motion. Dense dot fields are single paths of zero-length round-capped segments,
which keeps the files small.

    python scripts/make_assets.py

Edit the content in the tables near the bottom: ABOUT, PROJECTS, BUILDING, STACK and so on.
"""

import math
import random
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dotfont import GLYPHS as DOT, RADIUS as DOT_R, SPACE as DOT_SPACE  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "assets"

BG = "#0a070d"
BG2 = "#140d1a"
INK = "#f3ecf8"
MID = "#b9adc4"
LO = "#7d7088"
PALE = "#fbe6ff"
ACCENT = "#db94ed"
VIOLET = "#ee15ee"
MONO = "'DM Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
CHAR = 0.6          # monospace advance, as a fraction of font size

# Every panel is drawn on a 1200-unit-wide grid and shown at the README's full width, so
# one unit renders the same size everywhere and this one type scale holds across files.
# GitHub shows the README at roughly 0.65x, so nothing that needs reading goes below 14.
W = 1200
GAP = 16            # gutter between cards that share a row
RADIUS = 18         # panel corner radius, the site's --radius
LABEL = 14          # spaced uppercase labels
SMALL = 15
BODY = 17
LEAD = 20

STYLE = (
    f".t{{font-family:{MONO}}}"
    ".tw{animation:tw 4s ease-in-out infinite}"
    ".spin{transform-box:view-box;animation:spin linear infinite}"
    ".pulse{animation:pulse 4s ease-in-out infinite}"
    ".blink{animation:blink 1.2s steps(1) infinite}"
    ".sweep{transform-box:view-box;animation:spin 6s linear infinite}"
    ".travel{animation:travel 7s cubic-bezier(.45,0,.55,1) infinite}"
    ".orbit{animation:orbit linear infinite}"
    ".shine{animation:shine 9s ease-in-out infinite}"
    ".scan{animation:scan 9s linear infinite}"
    "@keyframes tw{0%,100%{opacity:.12}50%{opacity:.9}}"
    "@keyframes spin{to{transform:rotate(360deg)}}"
    "@keyframes pulse{0%,100%{opacity:.45}50%{opacity:1}}"
    "@keyframes blink{0%{opacity:1}50%{opacity:0}}"
    "@keyframes travel{0%{transform:translateX(0);opacity:0}6%{opacity:1}94%{opacity:1}"
    "100%{transform:translateX(var(--dx));opacity:0}}"
    "@keyframes orbit{to{stroke-dashoffset:-360}}"
    "@keyframes shine{0%{transform:translateX(0)}45%,100%{transform:translateX(var(--sw))}}"
    "@keyframes scan{0%{transform:translateY(-80px)}100%{transform:translateY(var(--sh,460px))}}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
)

DEFS = (
    f'<radialGradient id="glow"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".38"/>'
    f'<stop offset=".45" stop-color="{ACCENT}" stop-opacity=".13"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/>'
    '</radialGradient>'
    f'<radialGradient id="neb1" cx=".15" cy="0" r=".8"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".18"/>'
    f'<stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>'
    f'<radialGradient id="neb2" cx=".92" cy="1" r=".7"><stop offset="0" stop-color="{ACCENT}" stop-opacity=".13"/>'
    f'<stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>'
    '<linearGradient id="glass" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#fff" stop-opacity=".10"/><stop offset=".18" stop-color="#fff" stop-opacity=".045"/>'
    '<stop offset="1" stop-color="#fff" stop-opacity=".03"/></linearGradient>'
    '<linearGradient id="rim" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#fff" stop-opacity=".38"/><stop offset=".5" stop-color="#fff" stop-opacity=".10"/>'
    f'<stop offset="1" stop-color="{ACCENT}" stop-opacity=".30"/></linearGradient>'
    f'<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/>'
    f'<stop offset=".5" stop-color="{ACCENT}" stop-opacity=".9"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>'
    '</linearGradient>'
    '<linearGradient id="band" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
    '<stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
    f'<linearGradient id="scanline" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/>'
    f'<stop offset=".5" stop-color="{ACCENT}" stop-opacity=".08"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>'
    '</linearGradient>'
    '<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>'
    '<filter id="bloom" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.2" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
)


# --------------------------------------------------------------------------- primitives

def svg(w, h, body, title, defs=""):
    label = f"<title>{escape(title)}</title>" if title else ""
    role = 'role="img"' if title else 'aria-hidden="true"'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" {role}>'
            f"{label}<defs><style>{STYLE}</style>{DEFS}{defs}</defs>{body}</svg>\n")


def text(x, y, s, size, fill, anchor="start", weight=None, spacing=None, opacity=None, cls="t", extra=""):
    attrs = (f' font-weight="{weight}"' if weight else "") + (f' letter-spacing="{spacing}"' if spacing else "") \
        + (f' opacity="{opacity}"' if opacity is not None else "")
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}"{attrs}{extra}>{escape(s)}</text>')


def spans(x, y, parts, size, anchor="start", spacing=1.5):
    """One line of text in several colours: parts is [(string, colour), ...]."""
    inner = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in parts)
    return (f'<text x="{x}" y="{y}" class="t" font-size="{size}" text-anchor="{anchor}" '
            f'letter-spacing="{spacing}">{inner}</text>')


def dots(points, r, color, opacity=None, extra=""):
    """Many dots as one path: each is a zero-length segment drawn with a round cap."""
    if not points:
        return ""
    d = "".join(f"M{x:.1f} {y:.1f}h0" for x, y in points)
    op = f' opacity="{opacity:.2f}"' if opacity is not None else ""
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{2 * r:.2f}" '
            f'stroke-linecap="round"{op}{extra}/>')


def dotfield(points, r, color, levels=5):
    """Dots with their own opacities, (x, y, o), grouped into a few paths by brightness."""
    buckets = {}
    for x, y, o in points:
        buckets.setdefault(max(1, round(o * levels)), []).append((x, y))
    return "".join(dots(pts, r, color, k / levels) for k, pts in sorted(buckets.items()))


def dots_on(points, r, color=ACCENT, opacity=1.0):
    return dotfield([(x, y, o * opacity) for x, y, o in points], r, color)


def line_pts(x1, y1, x2, y2, step, o=1.0):
    n = max(1, int(math.hypot(x2 - x1, y2 - y1) / step))
    return [(x1 + (x2 - x1) * i / n, y1 + (y2 - y1) * i / n, o) for i in range(n + 1)]


def space(w, h, rng, stars=120, radius=RADIUS):
    """Deep background: base, two nebula washes, three depths of stars and a few flares."""
    parts = [f'<rect width="{w}" height="{h}" rx="{radius}" fill="{BG}"/>',
             f'<rect width="{w}" height="{h}" rx="{radius}" fill="url(#neb1)"/>',
             f'<rect width="{w}" height="{h}" rx="{radius}" fill="url(#neb2)"/>']
    far = [(rng.uniform(8, w - 8), rng.uniform(8, h - 8), rng.uniform(.15, .5)) for _ in range(stars)]
    near = [(rng.uniform(8, w - 8), rng.uniform(8, h - 8), rng.uniform(.4, .85)) for _ in range(stars // 4)]
    parts += [dotfield(far, .6, INK, 3), dotfield(near, 1.0, INK, 3)]
    for _ in range(max(1, stars // 12)):
        x, y = rng.uniform(10, w - 10), rng.uniform(10, h - 10)
        parts.append(f'<circle class="tw" cx="{x:.1f}" cy="{y:.1f}" r="1.2" fill="{PALE}" '
                     f'style="animation-delay:{rng.uniform(0, 6):.1f}s"/>')
    for _ in range(stars // 110):
        x, y, s = rng.uniform(40, w - 40), rng.uniform(20, h - 20), rng.uniform(3.5, 6)
        parts.append(f'<g class="tw" style="animation-delay:{rng.uniform(0, 4):.1f}s" stroke="{PALE}" '
                     f'stroke-linecap="round"><path d="M{x - s:.1f} {y:.1f}H{x + s:.1f}M{x:.1f} {y - s:.1f}V{y + s:.1f}" '
                     f'stroke-width=".9"/><circle cx="{x:.1f}" cy="{y:.1f}" r="1.4" fill="{PALE}" stroke="none"/></g>')
    return "".join(parts)


def frame(w, h, radius=RADIUS):
    return (f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="{radius}" fill="none" '
            f'stroke="#fff" stroke-opacity=".10" stroke-width="1.5"/>')


def glass(x, y, w, h, r=14):
    """A liquid-glass island like the site's: tinted body, bright top rim, specular glint."""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{BG2}" fill-opacity=".55"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#glass)"/>'
            f'<rect x="{x + .75}" y="{y + .75}" width="{w - 1.5}" height="{h - 1.5}" rx="{r}" fill="none" '
            f'stroke="url(#rim)" stroke-width="1.5"/>'
            f'<path d="M{x + r} {y + 1.6} H{x + w - r}" stroke="#fff" stroke-opacity=".5" stroke-width="1" '
            f'stroke-linecap="round"/>')


# --------------------------------------------------------------------------- the site's HUD

def corners(w, h, inset=12, size=20, x0=0, y0=0):
    """The four corner brackets that frame the site's camera view."""
    a, b, c, d = x0 + inset, y0 + inset, x0 + w - inset, y0 + h - inset
    s = size
    return (f'<path d="M{a} {b + s}V{b}H{a + s}M{c - s} {b}H{c}V{b + s}M{c} {d - s}V{d}H{c - s}M{a + s} {d}H{a}V{d - s}" '
            f'fill="none" stroke="{ACCENT}" stroke-opacity=".6" stroke-width="2"/>')


def tag(x, y, label, name=None, center=False):
    """A solid accent tag with dark lettering, optionally followed by a name in grey."""
    tw = len(label) * (LABEL * CHAR + 2) + 16
    nw = len(name) * (LABEL * CHAR + 3) + 12 if name else 0
    if center:
        x -= (tw + nw) / 2
    out = (f'<rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="22" fill="{ACCENT}"/>'
           + text(f"{x + 8:.1f}", y + 16, label, LABEL, BG, weight=600, spacing=2))
    if name:
        out += text(f"{x + tw + 12:.1f}", y + 16, name, LABEL, MID, spacing=3)
    return out, tw + nw


def pips(x, y, n=3, on=0):
    out = []
    for i in range(n):
        px = x + i * 15
        if i == on:
            out.append(f'<rect x="{px}" y="{y}" width="9" height="9" fill="{ACCENT}" filter="url(#bloom)"/>')
        else:
            out.append(f'<rect x="{px + .5}" y="{y + .5}" width="8" height="8" fill="none" stroke="{ACCENT}" '
                       f'stroke-opacity=".6"/>')
    return "".join(out)


def barcode(x, y, w=64, h=12):
    bars = [(0, 2), (4, 1), (9, 3)]
    out = []
    for p in range(0, int(w), 14):
        out += [f'<rect x="{x + p + a}" y="{y}" width="{min(b, w - p - a)}" height="{h}"/>' for a, b in bars if p + a < w]
    return f'<g fill="#fff" opacity=".45">{"".join(out)}</g>'


def chip(x, y, label, size=SMALL, fill=ACCENT):
    """A square-cornered tag, like the HUD pips."""
    w = CHAR * size * len(label) + 22
    return (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="{size + 14}" rx="4" fill="{fill}" '
            f'fill-opacity=".08" stroke="{fill}" stroke-opacity=".45"/>'
            + text(f"{x + 11:.0f}", y + size + 4.5, label, size, fill)), w


def readout(x, y, pairs, anchor="start"):
    """HUD readout: grey labels, bright values."""
    parts = []
    for i, (k, v) in enumerate(pairs):
        parts += [((" · " if i else "") + k + " ", LO), (v, INK)]
    return spans(x, y, parts, LABEL, anchor)


# --------------------------------------------------------------------------- dot lettering

def dot_word(word, x, y, pitch, uid, shine=True):
    """A word in the site's Exypnos dot font with its vertical gradient. Returns (svg, width)."""
    pts, cx = [], x
    for ch in word:
        if ch == " ":
            cx += DOT_SPACE * pitch
            continue
        rows = DOT[ch]
        pts += [(cx + col * pitch, y + row * pitch)
                for row, bits in enumerate(rows) for col, bit in enumerate(bits) if bit == "1"]
        cx += len(rows[0]) * pitch
    width = cx - x - 4 * pitch
    r = DOT_R * pitch
    out = (f'<linearGradient id="wg{uid}" gradientUnits="userSpaceOnUse" x1="0" y1="{y}" x2="0" y2="{y + 10 * pitch}">'
           f'<stop offset="0" stop-color="{PALE}"/><stop offset=".5" stop-color="{ACCENT}"/>'
           f'<stop offset="1" stop-color="{VIOLET}"/></linearGradient>'
           f'<g filter="url(#bloom)">{dots(pts, r, f"url(#wg{uid})")}</g>')
    if shine:
        band = 26 * pitch
        out += (f'<mask id="wm{uid}" maskUnits="userSpaceOnUse" x="{x - 2 * pitch}" y="{y - 2 * pitch}" '
                f'width="{width + 4 * pitch}" height="{14 * pitch}">'
                f'<rect class="shine" style="--sw:{width + 2 * band:.0f}px" x="{x - band:.0f}" y="{y - 2 * pitch}" '
                f'width="{band:.0f}" height="{14 * pitch}" fill="url(#band)"/></mask>'
                + dots(pts, r, "#fff", .8, f' mask="url(#wm{uid})"'))
    return out, width


# --------------------------------------------------------------------------- scenes

def ring(rx, ry, n, r, color, opacity, dur, reverse=False, d=None):
    """A ring of n dots that orbit: a dashed ellipse whose dash offset runs."""
    shape = f'<path d="{d}"' if d else f'<ellipse rx="{rx:.1f}" ry="{ry:.1f}"'
    direction = "animation-direction:reverse;" if reverse else ""
    return (f'{shape} pathLength="360" fill="none" stroke="{color}" stroke-width="{2 * r:.2f}" stroke-linecap="round" '
            f'stroke-dasharray="0 {360 / n:.4f}" opacity="{opacity:.2f}" class="orbit" '
            f'style="{direction}animation-duration:{dur:.0f}s"/>')


def black_hole(cx, cy, R, uid, tilt=-11):
    """The site's EVENT HORIZON: an accretion disk of orbiting dots, lensed over the shadow.

    The disk is split along its long axis; the far half is drawn before the shadow and the near
    half after it. A static mask brightens the side that turns toward us (Doppler beaming).
    """
    disk = []
    for k in range(13):
        t = k / 12
        rr = R * (1.3 + 2.1 * t)
        color = PALE if t < .2 else ACCENT if t < .65 else VIOLET
        disk.append(ring(rr, rr * .19, int(2 * math.pi * rr / (6 + 6 * t)), 2.3 - 1.1 * t, color,
                         1 - .62 * t, 22 * (1.3 + 2.1 * t) ** 1.5 / 1.5, reverse=True))
    disk = "".join(disk)
    ext = R * 3.6
    lens = []
    for k in range(8):
        a = R * (1.1 + .12 * k)
        b = a * (1.0 - .05 * k)
        lens.append(ring(0, 0, int(math.pi * a / 5.5), 2.1 - .17 * k, PALE if k < 3 else ACCENT, 1 - .1 * k,
                         16 + 5 * k, reverse=True, d=f"M{-a:.1f} 0A{a:.1f} {b:.1f} 0 0 1 {a:.1f} 0"))
    under = ring(0, 0, 40, 1.3, ACCENT, .55, 20, d=f"M{-R * 1.08:.1f} 0A{R * 1.08:.1f} {R * .62:.1f} 0 0 0 {R * 1.08:.1f} 0")
    defs = (f'<linearGradient id="dop{uid}" x1="0" x2="1"><stop offset="0" stop-color="#fff"/>'
            f'<stop offset="1" stop-color="#fff" stop-opacity=".3"/></linearGradient>'
            f'<mask id="dm{uid}" maskUnits="userSpaceOnUse" x="{-ext:.0f}" y="{-ext:.0f}" width="{2 * ext:.0f}" '
            f'height="{2 * ext:.0f}"><rect x="{-ext:.0f}" y="{-ext:.0f}" width="{2 * ext:.0f}" height="{2 * ext:.0f}" '
            f'fill="url(#dop{uid})"/></mask>'
            f'<clipPath id="back{uid}"><rect x="{-ext:.0f}" y="{-ext:.0f}" width="{2 * ext:.0f}" height="{ext:.0f}"/></clipPath>'
            f'<clipPath id="front{uid}"><rect x="{-ext:.0f}" y="0" width="{2 * ext:.0f}" height="{ext:.0f}"/></clipPath>')
    return (f'<circle cx="{cx}" cy="{cy}" r="{R * 3.6:.1f}" fill="url(#glow)"/>'
            f'<g transform="translate({cx} {cy})">{defs}'
            f'<g transform="rotate({tilt})"><g clip-path="url(#back{uid})" mask="url(#dm{uid})">{disk}</g></g>'
            f'<g transform="rotate({tilt / 2})" mask="url(#dm{uid})">{"".join(lens)}{under}</g>'
            f'<circle r="{R * 1.05:.1f}" fill="none" stroke="{PALE}" stroke-width="2.2" class="pulse" filter="url(#bloom)"/>'
            f'<circle r="{R:.1f}" fill="#050307"/>'
            f'<g transform="rotate({tilt})"><g clip-path="url(#front{uid})" mask="url(#dm{uid})">{disk}</g></g>'
            '</g>')


def galaxy(cx, cy, size, rng, opacity=1.0, dur=140):
    """The site's SPIRAL ARMS: a two-armed log spiral of dots around a bright bulge, tilted toward us."""
    pts = []
    for arm in range(2):
        for k in range(260):
            t = k / 259
            a = arm * math.pi + t * 4.4 + rng.gauss(0, .12)
            r = size * (.08 + .92 * t) + rng.gauss(0, size * .03)
            pts.append((cx + r * math.cos(a), cy + .5 * r * math.sin(a), (1 - .75 * t) * opacity))
    dust = [(cx + rng.gauss(0, size * .45), cy + rng.gauss(0, size * .2), .3 * opacity) for _ in range(160)]
    return (f'<circle cx="{cx}" cy="{cy}" r="{size * .9:.0f}" fill="url(#glow)" opacity="{opacity:.2f}"/>'
            f'<g class="spin" style="transform-origin:{cx}px {cy}px;animation-duration:{dur}s">'
            + dotfield(pts, 1.5, ACCENT) + dotfield(dust, 1, INK) + '</g>'
            + f'<ellipse cx="{cx}" cy="{cy}" rx="{size * .13:.0f}" ry="{size * .08:.0f}" fill="{PALE}" '
              f'opacity="{.8 * opacity:.2f}" filter="url(#soft)"/>')


def scope(cx, cy, r):
    """A HUD reticle: glass disc, a turning ring of dots, and tick marks every 30 degrees."""
    ticks = []
    for k in range(12):
        a = math.pi * k / 6
        major = k % 3 == 0
        r1, r2 = r + 14, r + (24 if major else 19)
        ticks.append(f'M{cx + r1 * math.cos(a):.1f} {cy + r1 * math.sin(a):.1f}L{cx + r2 * math.cos(a):.1f} '
                     f'{cy + r2 * math.sin(a):.1f}')
    return (f'<circle cx="{cx}" cy="{cy}" r="{r * 1.9:.0f}" fill="url(#glow)" opacity=".8"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{BG2}" fill-opacity=".8"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#glass)" stroke="url(#rim)" stroke-width="1.5"/>'
            f'<g transform="translate({cx} {cy})">{ring(r + 7, r + 7, int(2 * math.pi * (r + 7) / 9), 1.3, ACCENT, .7, 60)}</g>'
            f'<path d="{"".join(ticks)}" stroke="{ACCENT}" stroke-opacity=".55" stroke-width="1.5"/>')


# --------------------------------------------------------------------------- icons

def icon_radar(cx, cy, s=1.0):
    """portscan: concentric rings, a rotating sweep, and blips on open ports."""
    pts = []
    for radius in (16, 32, 48):
        n = int(2 * math.pi * radius * s / 7)
        pts += [(cx + radius * s * math.cos(2 * math.pi * k / n), cy + radius * s * math.sin(2 * math.pi * k / n), .35)
                for k in range(n)]
    pts += line_pts(cx - 52 * s, cy, cx + 52 * s, cy, 7 * s, .2) + line_pts(cx, cy - 52 * s, cx, cy + 52 * s, 7 * s, .2)
    sweep = "".join(dots([(cx + r * s * math.cos(a), cy + r * s * math.sin(a)) for r in range(6, 50, 6)],
                         1.9 * s, ACCENT, .9 - .25 * j) for j, a in enumerate([0, -.18, -.36]))
    blips = "".join(f'<circle cx="{cx + bx * s}" cy="{cy + by * s}" r="{3.4 * s:.1f}" fill="{VIOLET}" class="pulse" '
                    f'style="animation-delay:{d}s" filter="url(#bloom)"/>'
                    for bx, by, d in [(22, -28, 0), (-36, 14, 1.3), (30, 26, 2.6)])
    return (dots_on(pts, 1.5 * s) + blips
            + f'<g class="sweep" style="transform-origin:{cx}px {cy}px">{sweep}</g>')


def icon_mail(cx, cy, s=1.0):
    """MailSleuth: an envelope, with a warning mark on a lookalike sender."""
    w, h = 84 * s, 58 * s
    x0, y0 = cx - w / 2, cy - h / 2
    pts = (line_pts(x0, y0, x0 + w, y0, 6 * s) + line_pts(x0, y0 + h, x0 + w, y0 + h, 6 * s)
           + line_pts(x0, y0, x0, y0 + h, 6 * s) + line_pts(x0 + w, y0, x0 + w, y0 + h, 6 * s)
           + line_pts(x0, y0, cx, cy + 6 * s, 6 * s, .7) + line_pts(x0 + w, y0, cx, cy + 6 * s, 6 * s, .7))
    bx, by = x0 + w - 2 * s, y0 + 2 * s
    badge = (f'<circle cx="{bx}" cy="{by}" r="{15 * s}" fill="{BG}" stroke="{VIOLET}" stroke-width="{2 * s}" '
             f'class="pulse" filter="url(#bloom)"/>'
             + dots_on(line_pts(bx, by - 8 * s, bx, by + 2 * s, 3.4 * s), 1.6 * s, INK)
             + f'<circle cx="{bx}" cy="{by + 7 * s}" r="{1.8 * s}" fill="{INK}"/>')
    return dots_on(pts, 1.7 * s) + badge


def icon_key(cx, cy, s=1.0):
    """pwaudit: a key, with the hash prefix that is all that leaves the machine."""
    pts = []
    ox, oy = cx - 30 * s, cy - 6 * s
    n = 26
    pts += [(ox + 20 * s * math.cos(2 * math.pi * k / n), oy + 20 * s * math.sin(2 * math.pi * k / n), 1) for k in range(n)]
    pts += [(ox + 8 * s * math.cos(2 * math.pi * k / 10), oy + 8 * s * math.sin(2 * math.pi * k / 10), .5) for k in range(10)]
    pts += line_pts(ox + 20 * s, oy, cx + 46 * s, oy, 6 * s)
    for tx, th in [(cx + 22 * s, 14), (cx + 34 * s, 9), (cx + 46 * s, 14)]:
        pts += line_pts(tx, oy, tx, oy + th * s, 5 * s)
    return dots_on(pts, 1.8 * s) + text(f"{cx - 52 * s:.0f}", f"{cy + 44 * s:.0f}", "5BAA6·····", 13 * s, MID) \
        + f'<rect x="{cx - 52 * s + 5 * 13 * s * CHAR:.1f}" y="{cy + 33 * s:.1f}" width="{2 * s:.1f}" ' \
          f'height="{14 * s:.1f}" fill="{ACCENT}" class="blink"/>'


def icon_log(cx, cy, s=1.0):
    """authtrail: log lines of failures in dim dots, one bright line where a login succeeded."""
    out = []
    widths = [70, 54, 78, 46, 66, 74, 58]
    for i, w in enumerate(widths):
        y = cy - 39 * s + i * 13 * s
        hit = i == 4
        color, o, r = (VIOLET, 1, 2.2) if hit else (LO, .8, 1.5)
        g = dots_on(line_pts(cx - 46 * s, y, cx - 46 * s + w * s, y, 6 * s), r * s, color, o)
        out.append(f'<g class="pulse" filter="url(#bloom)">{g}</g>' if hit else g)
        if hit:
            out.append(f'<path d="M{cx - 58 * s} {y} l6 -5 v10 z" fill="{ACCENT}"/>')
    return "".join(out)


def icon_galaxy(cx, cy, s=1.0):
    return galaxy(cx, cy, 58 * s, random.Random(5), dur=80)


def icon_sword(cx, cy, s=1.0):
    """Dreamfall: a dot-art blade."""
    bitmap = ["00000000011", "00000000111", "00000001110", "00000011100", "00000111000", "00001110000",
              "10011100000", "01111000000", "00110000000", "01011000000", "10000100000"]
    blade, hilt = [], []
    for row, bits in enumerate(bitmap):
        for col, b in enumerate(bits):
            if b == "1":
                (hilt if row >= 6 else blade).append((cx + (col - 5) * 8 * s, cy + (row - 5) * 8 * s))
    return f'<g filter="url(#bloom)">{dots(blade, 2.6 * s, ACCENT)}{dots(hilt, 2.6 * s, VIOLET)}</g>'


def icon_timeline(cx, cy, s=1.0):
    """Secret Time Machine: exposure bars, one still live and pulsing to the right edge."""
    out = [dots_on(line_pts(cx - 56 * s, cy + 42 * s, cx + 56 * s, cy + 42 * s, 6 * s, .35), 1.3 * s, LO)]
    for i, (x0, x1, tail) in enumerate([(-50, -10, 18), (-34, 8, 0), (-20, 56, 0), (-4, 22, 26)]):
        y = cy - 30 * s + i * 20 * s
        live = x1 == 56
        g = dots_on(line_pts(cx + x0 * s, y, cx + x1 * s, y, 5 * s), (2.2 if live else 1.8) * s,
                    VIOLET if live else ACCENT)
        out.append(f'<g class="pulse" filter="url(#bloom)">{g}</g>' if live else g)
        if tail:
            out.append(dots_on(line_pts(cx + (x1 + 6) * s, y, cx + (x1 + tail) * s, y, 7 * s, .35), 1.3 * s))
    return "".join(out)


def icon_rings(cx, cy, s=1.0):
    """Blast Radius: dependency rings by depth, with a few risky packages glowing."""
    rng = random.Random(29)
    pts = []
    for radius, n in ((18, 6), (34, 11), (50, 16)):
        for k in range(n):
            a = 2 * math.pi * k / n + radius
            pts.append((cx + radius * s * math.cos(a), cy + radius * s * math.sin(a), rng.uniform(.4, .9)))
    rings = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r * s:.1f}" fill="none" stroke="{ACCENT}" stroke-opacity=".18" '
                    f'stroke-dasharray="2 5"/>' for r in (18, 34, 50))
    risky = "".join(f'<circle cx="{cx + bx * s:.1f}" cy="{cy + by * s:.1f}" r="{3.6 * s:.1f}" fill="{VIOLET}" class="pulse" '
                    f'style="animation-delay:{d}s" filter="url(#bloom)"/>'
                    for bx, by, d in [(30, -14, 0), (-44, 22, 1.1), (12, 47, 2.2)])
    core = f'<circle cx="{cx}" cy="{cy}" r="{5 * s:.1f}" fill="{INK}" filter="url(#bloom)"/>'
    return rings + dots_on(pts, 2 * s) + risky + core


def icon_print(cx, cy, s=1.0):
    """Fingerprint Mirror: dotted ridges of a fingerprint."""
    pts = []
    for i, r in enumerate(range(8, 56, 8)):
        n = int(math.pi * r * s / 6) + 2
        for k in range(n + 1):
            a = math.pi * (1.05 + .9 * k / n) if i % 2 else math.pi * (1.0 + 1.0 * k / n)
            pts.append((cx + r * s * math.cos(a), cy + 12 * s + 1.15 * r * s * math.sin(a), 1 - i * .1))
        pts += line_pts(cx - r * s, cy + 12 * s, cx - r * s * .9, cy + (30 + i * 3) * s, 6 * s, .6)
    return f'<g filter="url(#bloom)">{dots_on(pts, 1.7 * s)}</g>'


def icon_sawtooth(cx, cy, s=1.0):
    """Regex Replay: the timeline sawtooth that catastrophic backtracking draws."""
    pts, x = [], cx - 58 * s
    for tooth, height in enumerate([20, 28, 36, 44, 52]):
        n = 4 + tooth
        for k in range(n):
            pts.append((x + k * 4.2 * s, cy + 28 * s - height * s * k / (n - 1), .5 + .1 * tooth))
        x += n * 4.2 * s
        pts += line_pts(x - 4.2 * s, cy - (height - 28) * s, x - 4.2 * s, cy + 28 * s, 6 * s, .25)
    base = dots_on(line_pts(cx - 58 * s, cy + 36 * s, cx + 58 * s, cy + 36 * s, 6 * s, .3), 1.2 * s, LO)
    head = (f'<circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="{3.6 * s:.1f}" fill="{VIOLET}" class="pulse" '
            f'filter="url(#bloom)"/>')
    return base + dots_on(pts, 1.8 * s) + head


def icon_route(cx, cy, s=1.0):
    """Pathfinder: a street grid, the area a search explored, and the route through it."""
    grid = []
    for gx in range(-48, 49, 16):
        for gy in range(-40, 41, 16):
            d = math.hypot(gx + 32, gy - 24) / 90
            grid.append((cx + gx * s, cy + gy * s, max(.15, .9 - d)))
    route = (line_pts(cx - 32 * s, cy + 24 * s, cx - 32 * s, cy - 8 * s, 4 * s)
             + line_pts(cx - 32 * s, cy - 8 * s, cx + 16 * s, cy - 8 * s, 4 * s)
             + line_pts(cx + 16 * s, cy - 8 * s, cx + 32 * s, cy - 24 * s, 4 * s))
    pins = (f'<circle cx="{cx - 32 * s:.1f}" cy="{cy + 24 * s:.1f}" r="{4.5 * s:.1f}" fill="#3ddc84"/>'
            f'<circle cx="{cx + 32 * s:.1f}" cy="{cy - 24 * s:.1f}" r="{4.5 * s:.1f}" fill="{VIOLET}" class="pulse" '
            f'filter="url(#bloom)"/>')
    return dots_on(grid, 1.8 * s) + f'<g filter="url(#bloom)">{dots_on(route, 1.9 * s, INK)}</g>' + pins


def icon_terminal(cx, cy, s=1.0):
    """termreel: a terminal window with a prompt and a blinking cursor."""
    w, h = 104 * s, 72 * s
    x0, y0 = cx - w / 2, cy - h / 2
    pts = (line_pts(x0, y0, x0 + w, y0, 6 * s) + line_pts(x0, y0 + h, x0 + w, y0 + h, 6 * s)
           + line_pts(x0, y0, x0, y0 + h, 6 * s) + line_pts(x0 + w, y0, x0 + w, y0 + h, 6 * s)
           + line_pts(x0, y0 + 14 * s, x0 + w, y0 + 14 * s, 6 * s, .4))
    lights = "".join(f'<circle cx="{x0 + (10 + 9 * i) * s:.1f}" cy="{y0 + 7 * s:.1f}" r="{2.4 * s:.1f}" fill="{c}"/>'
                     for i, c in enumerate([VIOLET, ACCENT, INK]))
    lines = (text(f"{x0 + 9 * s:.0f}", f"{y0 + 34 * s:.0f}", "❯ reel", f"{13 * s:.1f}", ACCENT)
             + dots_on(line_pts(x0 + 9 * s, y0 + 46 * s, x0 + 70 * s, y0 + 46 * s, 5 * s, .5), 1.5 * s, MID)
             + text(f"{x0 + 9 * s:.0f}", f"{y0 + 64 * s:.0f}", "❯", f"{13 * s:.1f}", ACCENT)
             + f'<rect x="{x0 + 21 * s:.1f}" y="{y0 + 54 * s:.1f}" width="{7 * s:.1f}" height="{12 * s:.1f}" '
               f'fill="{INK}" class="blink"/>')
    return dots_on(pts, 1.5 * s) + lights + lines


ICONS = {"radar": icon_radar, "mail": icon_mail, "key": icon_key, "log": icon_log,
         "galaxy": icon_galaxy, "sword": icon_sword, "timeline": icon_timeline, "rings": icon_rings,
         "print": icon_print, "sawtooth": icon_sawtooth, "route": icon_route, "terminal": icon_terminal}


# --------------------------------------------------------------------------- panels

CARD_W = (W - GAP) / 2
LINK_W = (W - 2 * GAP) / 3


def in_row(inner_w, h, slot, n, body, title):
    """One of n images that share a README row with no space between them.

    Each file is W / n wide and holds a panel inner_w wide, shifted so the outer panels
    line up with the full-width ones and every gutter in the row comes out equal.
    """
    cell = W / n
    x = slot * (cell - inner_w) / (n - 1)
    return svg(f"{cell:g}", h, f'<g transform="translate({x:g} 0)">{body}</g>', title)


def banner():
    w, h = W, 420
    rng = random.Random(7)
    word, _ = dot_word("BLAZEXYZ", 72, 92, 5.6, "hero")
    t, _ = tag(72, 40, "BIO", "EVENT HORIZON")
    body = [space(w, h, rng, 320),
            f'<rect class="scan" style="--sh:{h + 80}px" x="0" y="0" width="{w}" height="80" fill="url(#scanline)"/>',
            black_hole(944, 206, 66, "hero"),
            t, word,
            text(72, 222, "QA · bug hunting · security tooling", 28, ACCENT),
            text(72, 260, "I test things until they break, then help fix them.", LEAD, MID),
            f'<circle cx="79" cy="306" r="5" fill="#3ddc84" class="pulse"/>',
            spans(94, 311, [("NOW ", LO), ("building authtrail", INK)], SMALL),
            pips(72, 368), text(124, 377, "SIGNAL", LABEL, LO, spacing=3),
            readout(1048, 377, [("TZ", "America/Chicago"), ("PRONOUNS", "she/her")], "end"),
            barcode(1064, 366),
            text(0, 0, "BLAZEXYZ // PROFILE // SIGNAL", 11, LO, "middle", spacing=5,
                 extra=f' transform="translate(34 {h / 2}) rotate(-90)"'),
            corners(w, h), frame(w, h)]
    return svg(w, h, "".join(body), "BLAZEXYZ: QA, bug hunting and security tooling. "
                                    "I test things until they break, then help fix them.")


def link_button(slot, label, sub, glyph):
    w, h = LINK_W, 80
    rng = random.Random(label)
    body = [space(w, h, rng, 30),
            f'<rect x="24" y="22" width="36" height="36" fill="{ACCENT}" fill-opacity=".12" stroke="{ACCENT}" '
            f'stroke-opacity=".6"/>',
            text(42, 46, glyph, 18, ACCENT, "middle"),
            text(76, 37, label, 19, INK), text(76, 59, sub, SMALL, LO),
            text(w - 30, 48, "↗", 22, ACCENT, "end"),
            corners(w, h, 8, 12), frame(w, h)]
    return in_row(w, h, slot, 3, "".join(body), f"{label}: {sub}")


def about(rows, numbers):
    w, h = W, 330
    rng = random.Random(11)
    t, _ = tag(48, 34, "BIO", "ABOUT")
    body = [space(w, h, rng, 110), galaxy(668, 190, 96, rng, .8), t]
    for i, (label, value) in enumerate(rows):
        y = 112 + i * 42
        body += [text(48, y, label.upper(), LABEL, ACCENT, spacing=3), text(190, y, value, 19, INK)]
    tw, th = 188, 104
    for i, (value, label) in enumerate(numbers):
        x, y = 776 + (i % 2) * (tw + GAP), 74 + (i // 2) * (th + GAP)
        body += [glass(x, y, tw, th, 4), corners(tw, th, 6, 10, x, y),
                 f'<g filter="url(#bloom)">{text(x + tw / 2, y + 58, value, 40, ACCENT, "middle")}</g>',
                 text(x + tw / 2, y + 85, label, SMALL, MID, "middle")]
    body += [corners(w, h), frame(w, h)]
    return svg(w, h, "".join(body), "About: " + "; ".join(f"{k}: {v}" for k, v in rows)
               + ". " + ", ".join(f"{v} {l}" for v, l in numbers))


def header(num, title, sub):
    """A section divider: number tag, the title in dot lettering, and a subtitle."""
    w, h = W, 96
    rng = random.Random(title)
    t, tw = tag(40, 37, num)
    word, ww = dot_word(title, 40 + tw + 22, 31, 3.4, title.replace(" ", "").lower())
    start = 40 + tw + 22 + ww + 30
    end = w - 44 - len(sub) * SMALL * CHAR - 26
    n = max(0, int((end - start) / 12))
    line = [(start + k * 12, 48.5, .15 + .6 * math.sin(math.pi * k / max(n - 1, 1))) for k in range(n)]
    body = [space(w, h, rng, 50), t, word, dotfield(line, 1.6, ACCENT),
            text(w - 44, 54, sub, SMALL, MID, "end"), corners(w, h, 10, 14), frame(w, h)]
    return svg(w, h, "".join(body), f"{num}. {title.title()}: {sub}")


def card_head(c, w, rng):
    """Shared top of every card: tag, name, description, and the icon in a HUD reticle."""
    kind, sep, area = c["layer"].partition(" · ")
    t, _ = tag(32, 30, kind, area or None)
    out = [space(w, c["h"], rng, 60), scope(w - 98, 96, 46), ICONS[c["icon"]](w - 98, 96, .68),
           t, text(32, 100, c["name"], 30, INK)]
    out += [text(32, 146 + i * 25, line, BODY, MID) for i, line in enumerate(c["lines"])]
    return out


def card_foot(c, w):
    h = c["h"]
    cta = c.get("cta", "")
    return [f'<path d="M32 {h - 50} H{w - 32}" stroke="#fff" stroke-opacity=".08"/>',
            readout(32, h - 23, c["footer"]),
            text(w - 32, h - 23, cta, LABEL, ACCENT, "end", spacing=2),
            corners(w, h, 8, 12), frame(w, h)]


def project_card(slot, p):
    w = CARD_W
    p = dict(p, h=356, cta="VIEW REPO ↗")
    body = card_head(p, w, random.Random(p["name"]))
    hy = 218
    hw = CHAR * SMALL * len(p["highlight"]) + 46
    body += [f'<rect x="32" y="{hy}" width="{hw:.0f}" height="34" rx="4" fill="{VIOLET}" fill-opacity=".10" '
             f'stroke="{VIOLET}" stroke-opacity=".5"/>',
             f'<rect x="45" y="{hy + 13}" width="8" height="8" fill="{VIOLET}" class="pulse"/>',
             text(62, hy + 22, p["highlight"], SMALL, INK)]
    x = 32
    for label in p["tags"]:
        c, cw = chip(x, 266, label)
        body.append(c)
        x += cw + 8
    body += card_foot(p, w)
    return in_row(w, p["h"], slot, 2, "".join(body), f"{p['name']}: {' '.join(p['lines'])}")


def small_card(slot, c):
    w = CARD_W
    c = dict(c, h=276)
    body = card_head(c, w, random.Random(c["name"])) + card_foot(c, w)
    return in_row(w, c["h"], slot, 2, "".join(body), f"{c['name']}: {' '.join(c['lines'])}")


def chain(steps):
    w, h = W, 330
    rng = random.Random(17)
    xs = [150 + i * 300 for i in range(len(steps))]
    cy = 150
    body = [space(w, h, rng, 120)]
    body.append(dots_on(line_pts(xs[0] + 92, cy, xs[-1] - 92, cy, 10, .45), 1.8))
    for i in range(len(steps) - 1):
        ax = (xs[i] + xs[i + 1]) / 2
        body.append(f'<path d="M{ax - 7} {cy - 8} l12 8 l-12 8" fill="none" stroke="{ACCENT}" stroke-width="2.4" '
                    f'stroke-linecap="round" stroke-linejoin="round"/>')
    dx = xs[-1] - xs[0] - 184
    body.append(f'<g class="travel" style="--dx:{dx}px"><circle cx="{xs[0] + 92}" cy="{cy}" r="7" fill="{VIOLET}" '
                f'filter="url(#bloom)"/><circle cx="{xs[0] + 92}" cy="{cy}" r="16" fill="{VIOLET}" opacity=".25" '
                f'filter="url(#soft)"/></g>')
    for x, (num, stage, icon, name, question) in zip(xs, steps):
        t, _ = tag(x, 30, f"{num} {stage}", center=True)
        body += [t, scope(x, cy, 62), ICONS[icon](x, cy, .85),
                 text(x, 268, name, 21, INK, "middle"),
                 text(x, 296, question, BODY, MID, "middle")]
    body += [corners(w, h), frame(w, h)]
    return svg(w, h, "".join(body), "Attack chain: " + "; then ".join(f"{s[3]} asks {s[4]}" for s in steps))


def stack(groups):
    w = W
    rng = random.Random(19)
    rows = []
    y = 38
    for label, items in groups:
        rows.append(text(48, y + 20, label.upper(), LABEL, LO, spacing=3))
        x = 260
        for item in items:
            c, cw = chip(x, y, item, 16)
            rows.append(c)
            x += cw + 10
        y += 50
    h = y - 50 + 30 + 38
    return svg(w, h, space(w, h, rng, 70) + "".join(rows) + corners(w, h) + frame(w, h),
               "Tools: " + "; ".join(f"{label}: {', '.join(items)}" for label, items in groups))


def footer():
    """The site's NIGHT HIGHWAY: a striped sun behind dotted mountains over a rolling grid."""
    w, h = W, 300
    rng = random.Random(23)
    hz = 214                                    # horizon
    word, ww = dot_word("THANKS FOR STOPPING BY", 0, 40, 2.4, "thanks")
    sun_r, sun_y = 64, hz - 26
    r = RADIUS
    ground = f"M0 {hz}H{w}V{h - r}a{r} {r} 0 0 1 -{r} {r}H{r}a{r} {r} 0 0 1 -{r} -{r}Z"
    stripes = "".join(f'<rect x="{600 - sun_r}" y="{sun_y + k:.0f}" width="{2 * sun_r}" height="{1.5 + i * .8:.1f}" '
                      f'fill="#000"/>' for i, k in enumerate(range(-44, sun_r, 9)))
    defs = (f'<linearGradient id="sun" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{PALE}"/>'
            f'<stop offset=".45" stop-color="{ACCENT}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>'
            f'<mask id="sunm"><rect width="{w}" height="{h}" fill="#fff"/>{stripes}</mask>'
            f'<clipPath id="floor"><path d="{ground}"/></clipPath>'
            f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="{VIOLET}" stop-opacity=".22"/></linearGradient>')
    # Mountains: two ridges, drawn as dark shapes with a dotted crest.
    ridges = []
    for layer, (base, amp, color, o) in enumerate([(hz - 26, 44, BG2, .55), (hz - 8, 30, "#0d0911", .8)]):
        pts = []
        for i in range(0, 121):
            x = i * 10
            centre = 1 - math.exp(-((x - 600) / 230) ** 2)
            y = base - amp * centre * (.55 + .45 * math.sin(x * .021 + layer * 2) * math.sin(x * .007 + 1))
            pts.append((x, y))
        poly = " ".join(f"{x:.0f},{y:.1f}" for x, y in pts)
        ridges.append(f'<polygon points="0,{hz} {poly} {w},{hz}" fill="{color}"/>')
        ridges.append(dots([(x, y) for x, y in pts[::1]], 1.3, ACCENT, o))
    # The floor: a grid of dots in perspective, brighter toward us, with a scan band rolling over it.
    floor = []
    for z in range(34, 9, -1):
        y = hz + 900 / z
        if y > h - 4:
            break
        near = (y - hz) / (h - hz)
        floor.append(dots([(600 + X * 340 / z, y) for X in range(-60, 61) if 8 < 600 + X * 340 / z < w - 8],
                          .6 + .9 * near, ACCENT, min(1, .15 + .9 * near)))
    body = [space(w, h, rng, 110),
            f'<rect width="{w}" height="{hz}" rx="{RADIUS}" fill="url(#sky)"/>',
            f'<circle cx="600" cy="{sun_y}" r="{sun_r * 2.4:.0f}" fill="url(#glow)"/>',
            f'<circle cx="600" cy="{sun_y}" r="{sun_r}" fill="url(#sun)" mask="url(#sunm)" filter="url(#bloom)"/>',
            "".join(ridges),
            f'<path d="{ground}" fill="{BG}"/>',
            f'<path d="M24 {hz}H{w - 24}" stroke="{ACCENT}" stroke-opacity=".7" stroke-width="1.5" filter="url(#bloom)"/>',
            f'<g clip-path="url(#floor)">{"".join(floor)}'
            f'<rect class="scan" style="--sh:{h - hz + 80}px" x="0" y="{hz}" width="{w}" height="50" fill="url(#scanline)"/></g>',
            f'<g transform="translate({(w - ww) / 2:.1f} 0)">{word}</g>',
            text(600, 94, "blazexyz.com", BODY, ACCENT, "middle", spacing=2),
            corners(w, h), frame(w, h)]
    return svg(w, h, "".join(body), "Thanks for stopping by. blazexyz.com", defs)


# --------------------------------------------------------------------------- content

ABOUT = [("role", "Board member, Exypnos One Corp."),
         ("focus", "QA · bug hunting · counsel"),
         ("building", "security tools for defenders"),
         ("likes", "dot art · black holes · shaders"),
         ("also", "web design · minecraft modding")]

STATS = [("10", "public projects"), ("7", "security & privacy"), ("221", "unit tests"), ("MIT", "licensed")]

PROJECTS = {
    "authtrail": dict(
        layer="HOST LOGS · DETECTION", icon="log", name="authtrail",
        lines=["Finds the one successful login hiding in", "thousands of failures, then rebuilds what",
               "the attacker did next as a timeline."],
        highlight="120 failures → 1 login → UID 0 backdoor",
        tags=["SSH", "incidents", "ATT&CK"], footer=[("PY", "3.11+"), ("DEPS", "0"), ("TESTS", "44")]),
    "mailsleuth": dict(
        layer="EMAIL · PHISHING", icon="mail", name="MailSleuth",
        lines=["Phishing triage for SOC analysts: SPF,", "DKIM, DMARC, lookalike domains and links.",
               "Verdicts an analyst can defend."],
        highlight="CEO fraud passes DMARC, still flagged",
        tags=["DMARC", "BEC", "IOCs", "web UI"], footer=[("PY", "3.11+"), ("DEPS", "0"), ("TESTS", "39")]),
    "portscan": dict(
        layer="NETWORK · EXPOSURE", icon="radar", name="portscan-fingerprint",
        lines=["Async scanner that names the software on", "each port, reads TLS certificates, and",
               "matches versions to CVEs by CPE name."],
        highlight="CPE: 39 real CVEs · keywords: 2",
        tags=["asyncio", "X.509", "NVD", "ATT&CK"], footer=[("PY", "3.10+"), ("DEPS", "0"), ("TESTS", "28")]),
    "pwaudit": dict(
        layer="CREDENTIALS · PRIVACY", icon="key", name="pwaudit",
        lines=["Prices passwords by what an attacker would", "really spend, and checks breaches while",
               "only 5 hash characters leave the machine."],
        highlight="P@ssw0rd2024: 78.8 bits raw, 10 real",
        tags=["k-anonymity", "HIBP", "entropy"], footer=[("PY", "3.10+"), ("DEPS", "0"), ("TESTS", "37")]),
}

# The newer six: three more security and privacy tools, three engineering projects.
MORE = {
    "secret-time-machine": dict(
        layer="SECRETS · GIT HISTORY", icon="timeline", name="Secret Time Machine",
        lines=["Finds every secret ever committed, on every", "branch and tag, and shows how long each",
               "one was exposed, as a timeline report."],
        highlight="deleted ≠ gone: 4 removed keys still in history",
        tags=["git", "DevSecOps", "CI"], footer=[("PY", "3.9+"), ("DEPS", "0"), ("TESTS", "12")]),
    "blast-radius": dict(
        layer="SUPPLY CHAIN · DEPENDENCIES", icon="rings", name="Blast Radius",
        lines=["Resolves your full npm or Python tree in", "the browser, scores every package's risk,",
               "and shows which choice pulled it in."],
        highlight="flags event-stream even though npm 404s",
        tags=["OSV", "PEP 440", "CVSS", "d3"], footer=[("RUNS", "browser"), ("BUILD", "none"), ("TESTS", "15")]),
    "fingerprint-mirror": dict(
        layer="PRIVACY · TRACKING", icon="print", name="Fingerprint Mirror",
        lines=["Everything a site can learn about your", "browser without a cookie, and how unique",
               "that makes you, in bits."],
        highlight="same ID in a private window",
        tags=["canvas", "WebGL", "entropy"], footer=[("RUNS", "browser"), ("DEPS", "0"), ("NETWORK", "none")]),
    "regex-replay": dict(
        layer="PARSERS · ReDoS", icon="sawtooth", name="Regex Replay",
        lines=["A from-scratch backtracking regex engine", "you can step through, to see exactly",
               "where catastrophic backtracking starts."],
        highlight="checked vs RegExp on 4,000 fuzz cases",
        tags=["regex", "ReDoS", "fuzzing"], footer=[("FILES", "1 HTML"), ("DEPS", "0"), ("CI", "node 22")]),
    "pathfinding-playground": dict(
        layer="ALGORITHMS · MAPS", icon="route", name="Pathfinder Playground",
        lines=["Races Dijkstra, A*, bidirectional search", "and more side by side on real",
               "OpenStreetMap streets."],
        highlight="all optimal on 100 random routes",
        tags=["graphs", "A*", "Leaflet"], footer=[("RUNS", "browser"), ("BUILD", "none"), ("TESTS", "9")]),
    "termreel": dict(
        layer="DEV TOOLS · TERMINAL", icon="terminal", name="termreel",
        lines=["Records terminal sessions and turns them", "into small animated SVGs that play",
               "right inside a GitHub README."],
        highlight="sample SVG: 53.8 KB → 26.8 KB",
        tags=["VT emulator", "SVG", "CSS"], footer=[("PY", "3.10+"), ("DEPS", "0"), ("TESTS", "37")]),
}

CHAIN = [("01", "INBOX", "mail", "MailSleuth", "is it phishing?"),
         ("02", "CREDS", "key", "pwaudit", "guessable? breached?"),
         ("03", "NETWORK", "radar", "portscan", "what's exposed?"),
         ("04", "HOST", "log", "authtrail", "did they get in?")]

BUILDING = {
    "site": dict(layer="WEB · GRAPHICS", icon="galaxy", name="blazexyz.com",
                 lines=["My site: a three.js black hole, galaxy and", "highway behind liquid-glass panels, with",
                        "dot-matrix type and live Discord presence."],
                 footer=[("BUILT WITH", "Next.js · R3F · GLSL")], cta="VISIT SITE ↗"),
    "dreamfall": dict(layer="GAME · MOD", icon="sword", name="Dreamfall",
                      lines=["A Fabric mod that brings the Shadow Slave", "novel to Minecraft: soul ranks, Aspects,",
                             "Flaws and cinematic Awakenings."],
                      footer=[("MC", "26.2"), ("LOADER", "Fabric"), ("JAVA", "25")], cta="IN PROGRESS"),
}

STACK = [("security", ["Python", "asyncio", "MITRE ATT&CK", "NVD / CPE", "OSV", "git internals"]),
         ("web & graphics", ["TypeScript", "Next.js", "three.js", "GLSL", "d3", "Leaflet"]),
         ("quality", ["unittest", "node:test", "Vitest", "fuzzing", "GitHub Actions"])]

LINKS = {"link-site": ("blazexyz.com", "website", "◎"),
         "link-discord": ("discord", "say hi", "@"),
         "link-exypnos": ("exypnos one", "board member", "✦")}

HEADERS = {"header-toolkit": ("01", "TOOLKIT", "four tools, four layers of defense"),
           "header-chain": ("02", "ONE ATTACK", "four tools follow one intrusion"),
           "header-more": ("03", "MORE", "secrets, supply chain, privacy, builder tools"),
           "header-building": ("04", "BUILDING", "graphics, the web, and games"),
           "header-stack": ("05", "STACK", "the tools I reach for")}


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    files = {"banner.svg": banner(), "about.svg": about(ABOUT, STATS),
             "chain.svg": chain(CHAIN), "stack.svg": stack(STACK), "footer.svg": footer()}
    files.update({f"{k}.svg": header(*v) for k, v in HEADERS.items()})
    files.update({f"card-{k}.svg": project_card(i % 2, v) for i, (k, v) in enumerate(PROJECTS.items())})
    files.update({f"card-{k}.svg": project_card(i % 2, v) for i, (k, v) in enumerate(MORE.items())})
    files.update({f"build-{k}.svg": small_card(i % 2, v) for i, (k, v) in enumerate(BUILDING.items())})
    files.update({f"{k}.svg": link_button(i, *v) for i, (k, v) in enumerate(LINKS.items())})
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
    for f in sorted(OUT.glob("*.svg")):
        print(f"wrote assets/{f.name}: {f.stat().st_size // 1024} KB")
