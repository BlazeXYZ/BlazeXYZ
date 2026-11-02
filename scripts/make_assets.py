"""Generate the SVG art for the profile README: banner, project cards, divider.

The look follows blazexyz.com: near-black violet background, a pink-violet
accent, dot-matrix lettering and a black hole. GitHub shows these as <img>, so
they can't load web fonts or scripts: letters are drawn as dots, and animation
is plain CSS that stops for visitors who prefer reduced motion.

    python scripts/make_assets.py
"""

import math
import random
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

BG = "#0a070d"
INK = "#f3ecf8"
MID = "#b9adc4"
LO = "#7d7088"
ACCENT = "#db94ed"
VIOLET = "#ee15ee"
MONO = "'DM Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# 5x7 dot font, capitals only (same idea as the site's {{dot}} text).
GLYPHS = {
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
}

REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def dot_text(word, x, y, pitch, r, cls="d"):
    """Draw a word as circles; each letter is 5 dots wide with one blank column between."""
    out = []
    for i, ch in enumerate(word):
        for row, bits in enumerate(GLYPHS[ch]):
            for col, bit in enumerate(bits):
                if bit == "1":
                    cx = x + (i * 6 + col) * pitch
                    cy = y + row * pitch
                    delay = (i * 6 + col) * 0.06
                    out.append(f'<circle class="{cls}" cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" '
                               f'style="animation-delay:{delay:.2f}s"/>')
    return "".join(out)


def stars(rng, n, w, h, avoid=None):
    out = []
    for _ in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        if avoid and avoid(x, y):
            continue
        r = rng.choice([0.6, 0.8, 1.0, 1.3])
        o = rng.uniform(0.25, 0.8)
        cls = ' class="tw"' if rng.random() < 0.25 else ""
        delay = rng.uniform(0, 6)
        out.append(f'<circle{cls} cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{INK}" opacity="{o:.2f}" '
                   f'style="animation-delay:{delay:.2f}s"/>')
    return "".join(out)


def black_hole(cx, cy, scale, rng):
    """Accretion disk as rings of dots on a tilted ellipse, with a lensed glow and a shadow."""
    parts = [
        f'<circle cx="{cx}" cy="{cy}" r="{150 * scale}" fill="url(#glow)"/>',
        f'<g transform="translate({cx} {cy}) rotate(-14) scale(1 0.32)">',
    ]
    for ring, (radius, count, size, color, speed) in enumerate([
            (95, 64, 2.4, ACCENT, 40), (118, 80, 2.0, VIOLET, 55),
            (140, 96, 1.6, ACCENT, 70), (162, 110, 1.2, INK, 90)]):
        dots = []
        for k in range(count):
            a = 2 * math.pi * k / count
            o = 0.35 + 0.65 * (0.5 + 0.5 * math.cos(a)) * rng.uniform(0.7, 1.0)
            dots.append(f'<circle cx="{radius * scale * math.cos(a):.1f}" cy="{radius * scale * math.sin(a):.1f}" '
                        f'r="{size * scale:.2f}" fill="{color}" opacity="{o:.2f}"/>')
        direction = "spin" if ring % 2 == 0 else "spinr"
        parts.append(f'<g class="{direction}" style="animation-duration:{speed}s">{"".join(dots)}</g>')
    parts.append("</g>")
    # Photon ring and event horizon drawn over the disk's back half.
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{58 * scale}" fill="none" stroke="{ACCENT}" '
                 f'stroke-width="{2.2 * scale}" opacity="0.85" class="pulse"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{52 * scale}" fill="{BG}"/>')
    # The near side of the disk passes in front of the shadow.
    front = []
    for k in range(48):
        a = math.pi * k / 47
        x, y = 128 * scale * math.cos(a), 128 * scale * math.sin(a)
        front.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.9 * scale:.2f}" fill="{ACCENT}" '
                     f'opacity="{0.4 + 0.5 * math.sin(a):.2f}"/>')
    parts.append(f'<g transform="translate({cx} {cy}) rotate(-14) scale(1 0.32)">{"".join(front)}</g>')
    return "".join(parts)


def banner():
    w, h = 1200, 320
    rng = random.Random(7)
    hole_x, hole_y = 930, 160
    body = [
        f'<rect width="{w}" height="{h}" rx="22" fill="{BG}"/>',
        stars(rng, 260, w, h, avoid=lambda x, y: (x - hole_x) ** 2 + ((y - hole_y) * 2.2) ** 2 < 120 ** 2),
        black_hole(hole_x, hole_y, 1.15, rng),
        dot_text("BLAZE", 86, 62, 14, 4.6),
        f'<text x="86" y="204" class="t" font-size="25" fill="{ACCENT}">QA · bug hunting · security tooling</text>',
        f'<text x="86" y="240" class="t" font-size="19" fill="{MID}">I test things until they break, then help fix them.</text>',
        f'<text x="86" y="280" class="t" font-size="16" fill="{LO}">blazexyz.com  ·  she / her  ·  America/Chicago</text>',
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="22" fill="none" stroke="{INK}" stroke-opacity="0.12"/>',
    ]
    return svg(w, h, "".join(body), "Blaze: QA, bug hunting and security tooling",
               extra_defs=f'<radialGradient id="glow"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0.35"/>'
                          f'<stop offset="0.45" stop-color="{ACCENT}" stop-opacity="0.12"/>'
                          f'<stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>')


def card(name, layer, lines, tags, footer):
    w, h = 460, 230
    rng = random.Random(name)
    body = [
        f'<rect width="{w}" height="{h}" rx="18" fill="{BG}"/>',
        stars(rng, 40, w, h),
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="18" fill="none" stroke="{ACCENT}" stroke-opacity="0.35"/>',
        f'<circle cx="30" cy="34" r="4" fill="{ACCENT}" class="pulse"/>',
        f'<text x="44" y="39" class="t" font-size="12" letter-spacing="2" fill="{ACCENT}">{escape(layer)}</text>',
        f'<text x="26" y="80" class="t" font-size="25" fill="{INK}">{escape(name)}</text>',
    ]
    for i, text in enumerate(lines):
        body.append(f'<text x="26" y="{112 + i * 22}" class="t" font-size="14" fill="{MID}">{escape(text)}</text>')
    x = 26
    for tag in tags:
        tw = 8.4 * len(tag) + 18
        body.append(f'<rect x="{x}" y="166" width="{tw:.0f}" height="22" rx="11" fill="{ACCENT}" fill-opacity="0.12" '
                    f'stroke="{ACCENT}" stroke-opacity="0.45"/>')
        body.append(f'<text x="{x + 9}" y="181" class="t" font-size="12" fill="{ACCENT}">{escape(tag)}</text>')
        x += tw + 8
    body.append(f'<text x="26" y="212" class="t" font-size="12" fill="{LO}">{escape(footer)}</text>')
    return svg(w, h, "".join(body), f"{name}: {' '.join(lines)}")


def divider():
    w, h = 1200, 24
    dots = []
    for i in range(0, 120):
        x = 10 + i * 9.9
        o = 0.15 + 0.85 * math.exp(-((i - 60) / 28) ** 2)
        dots.append(f'<circle cx="{x:.1f}" cy="12" r="2" fill="{ACCENT}" opacity="{o:.2f}"/>')
    return svg(w, h, "".join(dots), "")


def svg(w, h, body, title, extra_defs=""):
    style = (f".t{{font-family:{MONO}}}"
             f".d{{fill:{INK};animation:glint 6s ease-in-out infinite}}"
             f".tw{{animation:tw 4s ease-in-out infinite}}"
             f".spin{{transform-origin:0 0;animation:spin linear infinite}}"
             f".spinr{{transform-origin:0 0;animation:spin linear infinite reverse}}"
             f".pulse{{animation:pulse 5s ease-in-out infinite}}"
             f"@keyframes glint{{0%,85%,100%{{fill:{INK}}}92%{{fill:{ACCENT}}}}}"
             f"@keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.9}}}}"
             f"@keyframes spin{{to{{transform:rotate(360deg)}}}}"
             f"@keyframes pulse{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}"
             + REDUCED)
    label = f'<title>{escape(title)}</title>' if title else ""
    role = 'role="img"' if title else 'aria-hidden="true"'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" {role}>'
            f'{label}<defs><style>{style}</style>{extra_defs}</defs>{body}</svg>\n')


CARDS = {
    "card-authtrail.svg": ("authtrail", "HOST LOGS · DETECTION", [
        "Finds the one successful login hiding in",
        "thousands of failures, and what came next."],
        ["SSH", "incidents", "ATT&CK"], "Python 3.11+  ·  0 deps  ·  44 tests"),
    "card-mailsleuth.svg": ("MailSleuth", "EMAIL · PHISHING TRIAGE", [
        "SPF/DKIM/DMARC, lookalike domains, deceptive",
        "links. Catches BEC that passes every check."],
        ["DMARC", "BEC", "IOCs", "web UI"], "Python 3.11+  ·  0 deps  ·  39 tests"),
    "card-portscan.svg": ("portscan-fingerprint", "NETWORK · EXPOSURE", [
        "Async scanner that fingerprints services,",
        "reads TLS certs and matches CVEs by CPE."],
        ["asyncio", "X.509", "NVD", "ATT&CK"], "Python 3.10+  ·  0 deps  ·  28 tests"),
    "card-pwaudit.svg": ("pwaudit", "CREDENTIALS · PRIVACY", [
        "Password strength by real guess cost, plus",
        "breach checks that send 5 hash characters."],
        ["k-anonymity", "HIBP", "entropy"], "Python 3.10+  ·  0 deps  ·  37 tests"),
}


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "banner.svg").write_text(banner(), encoding="utf-8")
    (OUT / "divider.svg").write_text(divider(), encoding="utf-8")
    for filename, args in CARDS.items():
        (OUT / filename).write_text(card(*args), encoding="utf-8")
    for f in sorted(OUT.glob("*.svg")):
        print(f"wrote assets/{f.name}: {f.stat().st_size // 1024} KB")
