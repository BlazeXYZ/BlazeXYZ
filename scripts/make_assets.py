"""Generate every SVG panel used by the profile README.

The look follows blazexyz.com: a near-black violet background, a pink-violet
accent, dot-matrix art, liquid-glass panels and a black hole. GitHub shows these
files through <img>, so they can't load web fonts or scripts: lettering and icons
are drawn as dots, and animation is plain CSS that stops for visitors who prefer
reduced motion.

    python scripts/make_assets.py

Edit the content in the PROJECTS / BUILDING / ABOUT / STACK tables near the bottom.
"""

import math
import random
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

BG = "#0a070d"
BG2 = "#140d1a"
INK = "#f3ecf8"
MID = "#b9adc4"
LO = "#7d7088"
ACCENT = "#db94ed"
VIOLET = "#ee15ee"
MONO = "'DM Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
CHAR = 0.6          # monospace advance, as a fraction of font size

# 5x7 dot font, capitals only, like the site's {{dot}} text.
GLYPHS = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
}

STYLE = (
    f".t{{font-family:{MONO}}}"
    f".d{{fill:{INK};animation:glint 7s ease-in-out infinite}}"
    ".tw{animation:tw 4s ease-in-out infinite}"
    ".spin{transform-box:view-box;animation:spin linear infinite}"
    ".pulse{animation:pulse 4s ease-in-out infinite}"
    ".blink{animation:blink 1.2s steps(1) infinite}"
    ".sweep{transform-box:view-box;animation:spin 6s linear infinite}"
    ".travel{animation:travel 7s cubic-bezier(.45,0,.55,1) infinite}"
    ".scan{animation:scan 9s linear infinite}"
    f"@keyframes glint{{0%,84%,100%{{fill:{INK}}}90%{{fill:{ACCENT}}}}}"
    "@keyframes tw{0%,100%{opacity:.12}50%{opacity:.9}}"
    "@keyframes spin{to{transform:rotate(360deg)}}"
    "@keyframes pulse{0%,100%{opacity:.45}50%{opacity:1}}"
    "@keyframes blink{0%{opacity:1}50%{opacity:0}}"
    "@keyframes travel{0%{transform:translateX(0);opacity:0}6%{opacity:1}94%{opacity:1}"
    "100%{transform:translateX(var(--dx));opacity:0}}"
    "@keyframes scan{0%{transform:translateY(-40px)}100%{transform:translateY(360px)}}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
)

DEFS = (
    f'<radialGradient id="glow"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".38"/>'
    f'<stop offset=".45" stop-color="{ACCENT}" stop-opacity=".13"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/>'
    '</radialGradient>'
    f'<radialGradient id="neb1" cx=".2" cy=".1" r=".7"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".16"/>'
    f'<stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>'
    f'<radialGradient id="neb2" cx=".9" cy="1" r=".6"><stop offset="0" stop-color="{ACCENT}" stop-opacity=".12"/>'
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
    f'<linearGradient id="scanline" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/>'
    f'<stop offset=".5" stop-color="{ACCENT}" stop-opacity=".07"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>'
    '</linearGradient>'
    '<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>'
    '<filter id="bloom" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.2" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
)


# --------------------------------------------------------------------------- primitives

def svg(w, h, body, title):
    label = f"<title>{escape(title)}</title>" if title else ""
    role = 'role="img"' if title else 'aria-hidden="true"'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" {role}>'
            f"{label}<defs><style>{STYLE}</style>{DEFS}</defs>{body}</svg>\n")


def text(x, y, s, size, fill, anchor="start", weight=None, spacing=None, opacity=None, cls="t"):
    extra = (f' font-weight="{weight}"' if weight else "") + (f' letter-spacing="{spacing}"' if spacing else "") \
        + (f' opacity="{opacity}"' if opacity is not None else "")
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}"{extra}>{escape(s)}</text>')


def space(w, h, rng, stars=120, radius=22):
    """Deep background: base, two nebula washes, and a starfield."""
    parts = [f'<rect width="{w}" height="{h}" rx="{radius}" fill="{BG}"/>',
             f'<rect width="{w}" height="{h}" rx="{radius}" fill="url(#neb1)"/>',
             f'<rect width="{w}" height="{h}" rx="{radius}" fill="url(#neb2)"/>']
    for _ in range(stars):
        x, y = rng.uniform(6, w - 6), rng.uniform(6, h - 6)
        r = rng.choice([0.5, 0.7, 0.9, 1.2])
        cls = ' class="tw"' if rng.random() < 0.22 else ""
        parts.append(f'<circle{cls} cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{INK}" '
                     f'opacity="{rng.uniform(.2, .75):.2f}" style="animation-delay:{rng.uniform(0, 6):.1f}s"/>')
    return "".join(parts)


def frame(w, h, radius=22, accent=False):
    stroke = ACCENT if accent else "#fff"
    return (f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="{radius}" fill="none" '
            f'stroke="{stroke}" stroke-opacity="{.35 if accent else .12}" stroke-width="1.5"/>')


def glass(x, y, w, h, r=20):
    """A liquid-glass island like the site's: tinted body, bright top rim, specular glint."""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#glass)"/>'
            f'<rect x="{x + .75}" y="{y + .75}" width="{w - 1.5}" height="{h - 1.5}" rx="{r}" fill="none" '
            f'stroke="url(#rim)" stroke-width="1.5"/>'
            f'<path d="M{x + r} {y + 1.6} H{x + w - r}" stroke="#fff" stroke-opacity=".5" stroke-width="1" '
            f'stroke-linecap="round"/>')


def dot_text(word, x, y, pitch, r):
    out = []
    for i, ch in enumerate(word):
        for row, bits in enumerate(GLYPHS[ch]):
            for col, bit in enumerate(bits):
                if bit == "1":
                    out.append(f'<circle class="d" cx="{x + (i * 6 + col) * pitch:.1f}" cy="{y + row * pitch:.1f}" '
                               f'r="{r}" style="animation-delay:{(i * 6 + col) * .07:.2f}s"/>')
    return f'<g filter="url(#bloom)">{"".join(out)}</g>'


def chip(x, y, label, size=12, fill=ACCENT):
    w = CHAR * size * len(label) + 20
    return (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="{size + 12}" rx="{(size + 12) / 2}" fill="{fill}" '
            f'fill-opacity=".10" stroke="{fill}" stroke-opacity=".45"/>'
            + text(f"{x + 10:.0f}", y + size + 3.5, label, size, fill)), w


# --------------------------------------------------------------------------- dot-art pieces

def black_hole(cx, cy, s, rng, tilt=-14, spin=True):
    parts = [f'<circle cx="{cx}" cy="{cy}" r="{155 * s:.1f}" fill="url(#glow)"/>',
             f'<g transform="translate({cx} {cy}) rotate({tilt}) scale(1 .3)">']
    for ring, (radius, count, size, color, speed) in enumerate([
            (92, 66, 2.6, ACCENT, 38), (114, 84, 2.1, VIOLET, 52), (137, 100, 1.7, ACCENT, 68),
            (160, 116, 1.3, INK, 90)]):
        dots = []
        for k in range(count):
            a = 2 * math.pi * k / count
            o = .3 + .7 * (.5 + .5 * math.cos(a + .6)) * rng.uniform(.7, 1)
            dots.append(f'<circle cx="{radius * s * math.cos(a):.1f}" cy="{radius * s * math.sin(a):.1f}" '
                        f'r="{size * s:.2f}" fill="{color}" opacity="{o:.2f}"/>')
        cls = ' class="spin"' if spin else ""
        direction = "" if ring % 2 == 0 else "animation-direction:reverse;"
        parts.append(f'<g{cls} style="transform-origin:0 0;{direction}animation-duration:{speed}s">{"".join(dots)}</g>')
    parts.append("</g>")
    # Gravitational lensing: the far side of the disk bent up over the shadow.
    lens = []
    for k in range(40):
        a = math.pi + math.pi * k / 39
        lens.append(f'<circle cx="{cx + 76 * s * math.cos(a):.1f}" cy="{cy + 64 * s * math.sin(a):.1f}" '
                    f'r="{1.5 * s:.2f}" fill="{ACCENT}" opacity="{.25 + .45 * abs(math.sin(a)):.2f}"/>')
    parts.append("".join(lens))
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{57 * s:.1f}" fill="none" stroke="{ACCENT}" '
                 f'stroke-width="{2.4 * s:.2f}" class="pulse" filter="url(#bloom)"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{51 * s:.1f}" fill="#050307"/>')
    front = []
    for k in range(52):
        a = math.pi * k / 51
        front.append(f'<circle cx="{126 * s * math.cos(a):.1f}" cy="{126 * s * math.sin(a):.1f}" '
                     f'r="{2.1 * s:.2f}" fill="{ACCENT}" opacity="{.35 + .55 * math.sin(a):.2f}"/>')
    parts.append(f'<g transform="translate({cx} {cy}) rotate({tilt}) scale(1 .3)">{"".join(front)}</g>')
    return "".join(parts)


def dots_on(points, r, color=ACCENT, opacity=1.0):
    return "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" opacity="{o * opacity:.2f}"/>'
                   for x, y, o in points)


def line_pts(x1, y1, x2, y2, step, o=1.0):
    n = max(1, int(math.hypot(x2 - x1, y2 - y1) / step))
    return [(x1 + (x2 - x1) * i / n, y1 + (y2 - y1) * i / n, o) for i in range(n + 1)]


def icon_radar(cx, cy, s=1.0):
    """portscan: concentric rings, a rotating sweep, and blips on open ports."""
    pts = []
    for radius in (16, 32, 48):
        n = int(2 * math.pi * radius * s / 7)
        pts += [(cx + radius * s * math.cos(2 * math.pi * k / n), cy + radius * s * math.sin(2 * math.pi * k / n), .35)
                for k in range(n)]
    pts += line_pts(cx - 52 * s, cy, cx + 52 * s, cy, 7 * s, .2) + line_pts(cx, cy - 52 * s, cx, cy + 52 * s, 7 * s, .2)
    sweep = "".join(f'<circle cx="{cx + r * s * math.cos(a):.1f}" cy="{cy + r * s * math.sin(a):.1f}" r="{1.9 * s:.2f}" '
                    f'fill="{ACCENT}" opacity="{.9 - .25 * j:.2f}"/>'
                    for j, a in enumerate([0, -.18, -.36])
                    for r in range(6, 50, 6))
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
        pts = line_pts(cx - 46 * s, y, cx - 46 * s + w * s, y, 6 * s)
        g = dots_on(pts, r * s, color, o)
        out.append(f'<g class="pulse" filter="url(#bloom)">{g}</g>' if hit else g)
        if hit:
            out.append(f'<path d="M{cx - 58 * s} {y} l6 -5 v10 z" fill="{ACCENT}"/>')
    return "".join(out)


def icon_galaxy(cx, cy, s=1.0, rng=None):
    rng = rng or random.Random(5)
    pts = []
    for arm in range(2):
        for k in range(70):
            t = k / 69
            a = arm * math.pi + t * 3.6
            r = 6 + t * 52
            pts.append((cx + r * s * math.cos(a) + rng.uniform(-2, 2), cy + .55 * r * s * math.sin(a) + rng.uniform(-2, 2),
                        1 - .7 * t))
    core = f'<circle cx="{cx}" cy="{cy}" r="{9 * s}" fill="{INK}" opacity=".9" filter="url(#soft)"/>'
    return f'<g class="spin" style="transform-origin:{cx}px {cy}px;animation-duration:80s">{dots_on(pts, 1.6 * s)}</g>' + core


def icon_sword(cx, cy, s=1.0):
    """Shadow Slave: a dot-art blade."""
    bitmap = ["00000000011", "00000000111", "00000001110", "00000011100", "00000111000", "00001110000",
              "10011100000", "01111000000", "00110000000", "01011000000", "10000100000"]
    out = []
    for row, bits in enumerate(bitmap):
        for col, b in enumerate(bits):
            if b == "1":
                color = VIOLET if row >= 6 else ACCENT
                out.append(f'<circle cx="{cx + (col - 5) * 8 * s:.1f}" cy="{cy + (row - 5) * 8 * s:.1f}" '
                           f'r="{2.6 * s:.1f}" fill="{color}"/>')
    return f'<g filter="url(#bloom)">{"".join(out)}</g>'


ICONS = {"radar": icon_radar, "mail": icon_mail, "key": icon_key, "log": icon_log,
         "galaxy": icon_galaxy, "sword": icon_sword}


# --------------------------------------------------------------------------- panels

def banner():
    w, h = 1200, 360
    rng = random.Random(7)
    hx, hy = 915, 175
    body = [space(w, h, rng, 300),
            f'<rect class="scan" x="0" y="0" width="{w}" height="80" fill="url(#scanline)"/>',
            black_hole(hx, hy, 1.25, rng),
            dot_text("BLAZE", 80, 70, 15, 5),
            text(80, 226, "QA · bug hunting · security tooling", 27, ACCENT),
            text(80, 262, "I test things until they break, then help fix them.", 19, MID),
            f'<circle cx="88" cy="304" r="5" fill="#3ddc84" class="pulse"/>',
            text(102, 309, "building authtrail · blazexyz.com · America/Chicago", 15, LO),
            frame(w, h)]
    return svg(w, h, "".join(body), "BLAZE: QA, bug hunting and security tooling. "
                                    "I test things until they break, then help fix them.")


def link_button(label, sub, glyph):
    w, h = 300, 64
    rng = random.Random(label)
    body = [space(w, h, rng, 18, 32), glass(4, 4, w - 8, h - 8, 28),
            f'<circle cx="38" cy="32" r="15" fill="{ACCENT}" fill-opacity=".14" stroke="{ACCENT}" stroke-opacity=".6"/>',
            text(38, 37, glyph, 15, ACCENT, "middle"),
            text(66, 30, label, 16, INK), text(66, 48, sub, 11, LO)]
    return svg(w, h, "".join(body), f"{label}: {sub}")


def about(rows):
    w, h = 1200, 300
    rng = random.Random(11)
    body = [space(w, h, rng, 120), glass(24, 24, w - 48, h - 48, 26),
            black_hole(165, 150, .62, rng, spin=True),
            text(165, 252, "BLAZE", 13, LO, "middle", spacing=4)]
    y = 66
    for label, value in rows:
        body.append(text(320, y, label.upper(), 12, ACCENT, spacing=3))
        body.append(text(460, y, value, 18, INK))
        y += 42
    body.append(f'<path d="M300 50 V250" stroke="#fff" stroke-opacity=".10"/>')
    body.append(frame(w, h))
    return svg(w, h, "".join(body), "About: " + "; ".join(f"{k}: {v}" for k, v in rows))


def stats(items):
    w, h = 1200, 150
    rng = random.Random(13)
    body = [space(w, h, rng, 60)]
    tw = (w - 48 - 3 * 16) / 4
    for i, (value, label) in enumerate(items):
        x = 24 + i * (tw + 16)
        body += [glass(x, 22, tw, h - 44, 20),
                 f'<g filter="url(#bloom)">{text(x + tw / 2, 82, value, 44, ACCENT, "middle")}</g>',
                 text(x + tw / 2, 108, label, 14, MID, "middle")]
    return svg(w, h, "".join(body), ", ".join(f"{v} {l}" for v, l in items))


def header(title, sub):
    w, h = 1200, 92
    rng = random.Random(title)
    tx = 52
    width = CHAR * 22 * len(title) + 4 * len(title)
    body = [f'<circle cx="30" cy="40" r="6" fill="{ACCENT}" class="pulse" filter="url(#bloom)"/>',
            text(tx, 48, title, 22, INK, spacing=4),
            text(tx, 76, sub, 14, LO),
            f'<rect x="{tx + width + 24:.0f}" y="39" width="{w - tx - width - 50:.0f}" height="2" fill="url(#fade)" '
            f'opacity=".6"/>']
    dots = dots_on([(tx + width + 24 + k * 14, 40, .2 + .6 * rng.random()) for k in range(int((w - tx - width - 60) / 14))],
                   1.6)
    body.insert(3, dots)
    return svg(w, h, "".join(body), f"{title}: {sub}")


def project_card(p):
    w, h = 590, 320
    rng = random.Random(p["name"])
    body = [space(w, h, rng, 50, 20),
            f'<circle cx="490" cy="112" r="88" fill="url(#glow)"/>',
            ICONS[p["icon"]](490, 112, 1.0),
            text(30, 44, p["layer"], 12, ACCENT, spacing=3),
            text(30, 90, p["name"], 30, INK)]
    for i, line in enumerate(p["lines"]):
        body.append(text(30, 128 + i * 23, line, 15, MID))
    hy = 128 + len(p["lines"]) * 23 + 4
    hw = CHAR * 13 * len(p["highlight"]) + 40
    body += [f'<rect x="30" y="{hy}" width="{hw:.0f}" height="30" rx="8" fill="{VIOLET}" fill-opacity=".10" '
             f'stroke="{VIOLET}" stroke-opacity=".5"/>',
             f'<circle cx="46" cy="{hy + 15}" r="4" fill="{VIOLET}" class="pulse"/>',
             text(58, hy + 20, p["highlight"], 13, INK)]
    x = 30
    for tag in p["tags"]:
        c, cw = chip(x, h - 74, tag)
        body.append(c)
        x += cw + 8
    body += [f'<path d="M30 {h - 32} H{w - 30}" stroke="#fff" stroke-opacity=".08"/>',
             text(30, h - 13, p["footer"], 12, LO),
             text(w - 30, h - 13, "view repo →", 12, ACCENT, "end"),
             frame(w, h, 20, accent=True)]
    return svg(w, h, "".join(body), f"{p['name']}: {' '.join(p['lines'])}")


def chain(steps):
    w, h = 1200, 330
    rng = random.Random(17)
    xs = [150 + i * 300 for i in range(len(steps))]
    cy = 128
    body = [space(w, h, rng, 120)]
    body.append(dots_on(line_pts(xs[0] + 70, cy, xs[-1] - 70, cy, 10, .45), 1.8))
    for i in range(len(steps) - 1):
        ax = (xs[i] + xs[i + 1]) / 2
        body.append(f'<path d="M{ax - 7} {cy - 8} l12 8 l-12 8" fill="none" stroke="{ACCENT}" stroke-width="2.4" '
                    f'stroke-linecap="round" stroke-linejoin="round"/>')
    dx = xs[-1] - xs[0] - 140
    body.append(f'<g class="travel" style="--dx:{dx}px"><circle cx="{xs[0] + 70}" cy="{cy}" r="7" fill="{VIOLET}" '
                f'filter="url(#bloom)"/><circle cx="{xs[0] + 70}" cy="{cy}" r="16" fill="{VIOLET}" opacity=".25" '
                f'filter="url(#soft)"/></g>')
    for x, (num, stage, icon, name, question) in zip(xs, steps):
        body += [text(x, 34, f"{num} · {stage}", 12, ACCENT, "middle", spacing=3),
                 f'<circle cx="{x}" cy="{cy}" r="68" fill="{BG2}"/>',
                 f'<circle cx="{x}" cy="{cy}" r="68" fill="url(#glass)" stroke="url(#rim)" stroke-width="1.5"/>',
                 ICONS[icon](x, cy, .9),
                 text(x, 238, name, 19, INK, "middle"),
                 text(x, 266, question, 14, MID, "middle")]
    body.append(text(w / 2, 312, "one intrusion, start to finish: the email, the password, the open port, the login",
                     13, LO, "middle"))
    body.append(frame(w, h))
    return svg(w, h, "".join(body), "Attack chain: " + "; then ".join(f"{s[3]} asks {s[4]}" for s in steps))


def small_card(c):
    w, h = 590, 230
    rng = random.Random(c["name"])
    body = [space(w, h, rng, 60, 20), f'<circle cx="490" cy="105" r="80" fill="url(#glow)"/>',
            ICONS[c["icon"]](490, 105, .9),
            text(30, 44, c["layer"], 12, ACCENT, spacing=3), text(30, 86, c["name"], 28, INK)]
    for i, line in enumerate(c["lines"]):
        body.append(text(30, 120 + i * 22, line, 15, MID))
    x = 30
    for tag in c["tags"]:
        cc, cw = chip(x, h - 48, tag)
        body.append(cc)
        x += cw + 8
    body.append(frame(w, h, 20, accent=True))
    return svg(w, h, "".join(body), f"{c['name']}: {' '.join(c['lines'])}")


def stack(groups):
    w = 1200
    rng = random.Random(19)
    rows = []
    y = 34
    for label, items in groups:
        rows.append(text(36, y + 17, label.upper(), 12, LO, spacing=3))
        x = 230
        for item in items:
            c, cw = chip(x, y, item, 14, ACCENT)
            rows.append(c)
            x += cw + 10
        y += 46
    h = y + 10
    return svg(w, h, space(w, h, rng, 70) + "".join(rows) + frame(w, h),
               "Tools: " + "; ".join(f"{label}: {', '.join(items)}" for label, items in groups))


def footer():
    w, h = 1200, 170
    rng = random.Random(23)
    body = [space(w, h, rng, 90)]
    # A planet's horizon in dots, lit from the top.
    for ring in range(9):
        r = 900 + ring * 14
        for k in range(150):
            a = math.pi * 1.5 + (k - 75) / 75 * .62
            x, y = 600 + r * math.cos(a), 1040 + r * math.sin(a)
            if 0 < x < w and 0 < y < h:
                o = (1 - ring / 9) * (1 - abs(k - 75) / 80)
                body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.5" fill="{ACCENT}" opacity="{o:.2f}"/>')
    body += [text(600, 70, "thanks for stopping by", 22, INK, "middle", spacing=2),
             text(600, 100, "blazexyz.com", 15, ACCENT, "middle"),
             frame(w, h)]
    return svg(w, h, "".join(body), "Thanks for stopping by. blazexyz.com")


# --------------------------------------------------------------------------- content

ABOUT = [("role", "Board member, Exypnos One Corp."),
         ("focus", "QA · bug hunting · counsel"),
         ("building", "security tools for defenders"),
         ("likes", "dot art · black holes · shaders · web design"),
         ("also", "minecraft modding · she / her")]

STATS = [("4", "security tools"), ("148", "tests in CI"), ("0", "dependencies"), ("MIT", "licensed")]

PROJECTS = {
    "authtrail": dict(
        layer="HOST LOGS · DETECTION", icon="log", name="authtrail",
        lines=["Finds the one successful login hiding in", "thousands of failures, then rebuilds what",
               "the attacker did next as a timeline."],
        highlight="120 failures → 1 login → UID 0 backdoor",
        tags=["SSH", "incidents", "ATT&CK"], footer="Python 3.11+ · 0 deps · 44 tests"),
    "mailsleuth": dict(
        layer="EMAIL · PHISHING TRIAGE", icon="mail", name="MailSleuth",
        lines=["Phishing triage for SOC analysts: SPF,", "DKIM, DMARC, lookalike domains and links.",
               "Verdicts an analyst can defend."],
        highlight="CEO fraud passes DMARC, still flagged",
        tags=["DMARC", "BEC", "IOCs", "web UI"], footer="Python 3.11+ · 0 deps · 39 tests"),
    "portscan": dict(
        layer="NETWORK · EXPOSURE", icon="radar", name="portscan-fingerprint",
        lines=["Async scanner that names the software on", "each port, reads TLS certificates, and",
               "matches versions to CVEs by CPE name."],
        highlight="CPE: 39 real CVEs · keywords: 2",
        tags=["asyncio", "X.509", "NVD", "ATT&CK"], footer="Python 3.10+ · 0 deps · 28 tests"),
    "pwaudit": dict(
        layer="CREDENTIALS · PRIVACY", icon="key", name="pwaudit",
        lines=["Prices passwords by what an attacker would", "really spend, and checks breaches while",
               "only 5 hash characters leave the machine."],
        highlight="P@ssw0rd2024: 78.8 bits raw, 10 real",
        tags=["k-anonymity", "HIBP", "entropy"], footer="Python 3.10+ · 0 deps · 37 tests"),
}

CHAIN = [("01", "INBOX", "mail", "MailSleuth", "is it phishing?"),
         ("02", "CREDENTIALS", "key", "pwaudit", "guessable? breached?"),
         ("03", "NETWORK", "radar", "portscan", "what's exposed?"),
         ("04", "HOST", "log", "authtrail", "did they get in?")]

BUILDING = {
    "site": dict(layer="WEB · GRAPHICS", icon="galaxy", name="blazexyz.com",
                 lines=["My site: a three.js black hole, galaxy and", "highway behind liquid-glass panels, with",
                        "dot-matrix type and live Discord presence."],
                 tags=["Next.js", "R3F", "GLSL"]),
    "shadowslave": dict(layer="GAME · MOD", icon="sword", name="Shadow Slave",
                        lines=["A Fabric mod for Minecraft."],
                        tags=["Fabric", "Minecraft"]),
}

STACK = [("security", ["Python", "asyncio", "MITRE ATT&CK", "NVD / CPE", "Linux logs"]),
         ("web & graphics", ["TypeScript", "Next.js", "React", "three.js", "GLSL"]),
         ("quality", ["unittest", "Vitest", "GitHub Actions", "mutation checks"])]

LINKS = {"link-site": ("blazexyz.com", "website", "◎"),
         "link-discord": ("discord", "say hi", "@"),
         "link-exypnos": ("exypnos one", "board member", "✦")}


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    files = {"banner.svg": banner(), "about.svg": about(ABOUT), "stats.svg": stats(STATS),
             "chain.svg": chain(CHAIN), "stack.svg": stack(STACK), "footer.svg": footer(),
             "header-toolkit.svg": header("SECURITY TOOLKIT", "four tools, each aimed at a different layer of defense"),
             "header-chain.svg": header("ONE ATTACK, FOUR TOOLS", "together they follow a single intrusion"),
             "header-building.svg": header("ALSO BUILDING", "graphics, the web, and games"),
             "header-stack.svg": header("TOOLS I REACH FOR", "what these projects are made of")}
    files.update({f"card-{k}.svg": project_card(v) for k, v in PROJECTS.items()})
    files.update({f"build-{k}.svg": small_card(v) for k, v in BUILDING.items()})
    files.update({f"{k}.svg": link_button(*v) for k, v in LINKS.items()})
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
    for f in sorted(OUT.glob("*.svg")):
        print(f"wrote assets/{f.name}: {f.stat().st_size // 1024} KB")
