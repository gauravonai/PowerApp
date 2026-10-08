"""Builds the background picture: a JCB-style 3CX backhoe loader backlit by a low sun on a dusty site,
shot "on a long lens": the machine is a true-to-proportion silhouette (measured in metres, then scaled),
the sky shows through the cab glass, the beacon is lit, dust glows in the light, and the picture is
graded like a photograph (bloom, lens flare, depth of field, chromatic fringe, grain, vignette).

The machine stands on the RIGHT third so the login card (centre) never hides it.

    python3 tools/make_bg.py      -> app/media/bg-backhoe.jpg  (1600 x 900)
Needs node + playwright (build machine only). The JPEG is committed, so this rarely runs."""
import math
import os
import random
import subprocess

from PIL import Image, ImageChops, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "app", "media", "bg-backhoe.jpg")
W, H = 1600, 900
HORIZON = 652
S, X0, G = 76, 905, 784    # px per metre, x of the loader bucket tip, ground line
SUN = (int(X0 + 2.0 * S), int(G - 1.98 * S))   # just above the bonnet: the machine half-hides the sun


def p(x, y):
    """Machine coordinates (metres; x from the front bucket tip to the rear, y up from the ground) -> image px."""
    return "%.1f %.1f" % (X0 + x * S, G - y * S)


def poly(pts):
    return "M" + " L".join(p(x, y) for x, y in pts) + " Z"


def circ(x, y, r, **kw):
    a = " ".join("%s='%s'" % (k.replace("_", "-"), v) for k, v in kw.items())
    return "<circle cx='%.1f' cy='%.1f' r='%.1f' %s/>" % (X0 + x * S, G - y * S, r * S, a)


def stroke(pts, w, col, extra=""):
    d = "M" + " ".join(("C" if i % 3 == 1 else "") + p(x, y) for i, (x, y) in enumerate(pts))
    return "<path d='%s' fill='none' stroke='%s' stroke-width='%.1f' stroke-linecap='round' stroke-linejoin='round' %s/>" % (
        d, col, w * S, extra)


def wheel(cx, cy, r):
    out = [circ(cx, cy, r, fill="#07050a")]
    # tread lugs: chevrons round the tyre
    n = int(r * 40)
    for i in range(n):
        a = 2 * math.pi * i / n
        x1, y1 = cx + r * math.cos(a), cy + r * math.sin(a)
        x2, y2 = cx + (r + 0.035) * math.cos(a + 0.03), cy + (r + 0.035) * math.sin(a + 0.03)
        out.append("<line x1='%.1f' y1='%.1f' x2='%.1f' y2='%.1f' stroke='#07050a' stroke-width='%.1f'/>" % (
            X0 + x1 * S, G - y1 * S, X0 + x2 * S, G - y2 * S, 0.06 * S))
    out.append(circ(cx, cy, r * 0.62, fill="#120d0b"))
    out.append(circ(cx, cy, r * 0.56, fill="url(#rim)"))
    for i in range(8):
        a = 2 * math.pi * i / 8
        out.append(circ(cx + r * 0.38 * math.cos(a), cy + r * 0.38 * math.sin(a), r * 0.045, fill="#0a0708"))
    out.append(circ(cx, cy, r * 0.2, fill="#0b0809"))
    return "".join(out)


def machine_body():
    """Every solid part of the machine, drawn in one dark colour (the caller sets the fill)."""
    parts = [
        # chassis rail from the loader tower to the backhoe kingpost
        poly([(1.05, 0.62), (4.85, 0.62), (4.95, 0.95), (4.9, 1.42), (4.4, 1.5), (1.05, 1.0)]),
        # bonnet: grille at the front, rising towards the cab
        poly([(1.02, 0.66), (1.02, 1.22), (1.12, 1.32), (2.70, 1.66), (2.80, 1.64), (2.80, 0.8)]),
        # cab frame (glass is cut in later)
        poly([(2.76, 1.20), (2.80, 1.66), (2.93, 2.80), (2.86, 2.84), (2.86, 2.93), (4.44, 2.93), (4.44, 2.84),
              (4.36, 2.80), (4.42, 1.52), (4.40, 1.20)]),
        # rear mudguard (big arc over the rear wheel)
        "M%s A%.1f %.1f 0 0 1 %s L%s A%.1f %.1f 0 0 0 %s Z" % (
            p(2.86, 0.95), 0.92 * S, 0.92 * S, p(4.58, 0.95), p(4.46, 0.95), 0.80 * S, 0.80 * S, p(2.98, 0.95)),
        # front mudguard
        "M%s A%.1f %.1f 0 0 1 %s L%s A%.1f %.1f 0 0 0 %s Z" % (
            p(0.98, 0.62), 0.6 * S, 0.6 * S, p(2.12, 0.62), p(2.04, 0.62), 0.52 * S, 0.52 * S, p(1.06, 0.62)),
        # exhaust stack with rain cap
        poly([(2.36, 1.58), (2.36, 2.36), (2.31, 2.40), (2.31, 2.45), (2.50, 2.45), (2.50, 2.40), (2.45, 2.36), (2.45, 1.6)]),
        # air intake pre-cleaner
        poly([(2.05, 1.52), (2.05, 1.86), (2.18, 1.88), (2.18, 1.55)]),
        # loader bucket (side plate), resting flat on the ground
        poly([(0.0, 0.03), (0.06, 0.0), (0.86, 0.02), (0.96, 0.14), (0.99, 0.86), (0.84, 1.0), (0.46, 1.0),
              (0.22, 0.80), (0.10, 0.48)]),
        # kingpost + swing casting
        poly([(4.86, 0.55), (5.30, 0.55), (5.36, 1.62), (5.12, 1.78), (4.90, 1.62)]),
        # stabiliser legs and pads (down, working)
        poly([(4.70, 1.25), (4.86, 1.30), (5.22, 0.12), (5.10, 0.08)]),
        poly([(4.98, 0.06), (5.42, 0.06), (5.42, 0.0), (4.98, 0.0)]),
        poly([(5.02, 1.18), (5.16, 1.26), (5.58, 0.12), (5.46, 0.08)]),
        poly([(5.34, 0.06), (5.78, 0.06), (5.78, 0.0), (5.34, 0.0)]),
        # backhoe bucket (curled under, teeth biting into the heap)
        poly([(7.10, 0.95), (7.48, 0.98), (7.66, 0.70), (7.60, 0.36), (7.40, 0.16), (7.30, 0.04), (7.24, 0.16),
              (7.16, 0.06), (7.10, 0.20), (7.02, 0.12), (6.98, 0.30), (7.12, 0.55)]),
        # beacon + work lights on the roof
        poly([(3.56, 2.93), (3.58, 3.02), (3.70, 3.02), (3.72, 2.93)]),
        poly([(2.90, 2.86), (2.88, 2.94), (3.02, 2.94), (3.02, 2.86)]),
        poly([(4.30, 2.86), (4.30, 2.94), (4.44, 2.94), (4.44, 2.86)]),
        # mirror arm
        poly([(2.80, 2.30), (2.62, 2.48), (2.58, 2.70), (2.66, 2.70), (2.70, 2.50), (2.84, 2.38)]),
    ]
    out = ["<path d='%s'/>" % d for d in parts]
    # loader arm: tower pivot by the cab, down past the bonnet to the bucket
    out.append(stroke([(2.62, 1.98), (2.1, 1.86), (1.6, 1.62), (1.30, 1.32)], 0.22, "currentColor"))
    out.append(stroke([(1.30, 1.32), (1.12, 1.05), (0.98, 0.80), (0.90, 0.58)], 0.20, "currentColor"))
    out.append(stroke([(2.58, 1.36), (2.2, 1.30), (1.8, 1.10), (1.40, 0.92)], 0.08, "currentColor"))   # lift ram
    # backhoe boom (the "banana"), dipper and their rams
    out.append(stroke([(5.14, 1.40), (5.40, 2.70), (5.90, 3.55), (6.62, 3.42)], 0.30, "currentColor"))
    out.append(stroke([(6.62, 3.42), (6.70, 3.40), (6.80, 3.35), (6.86, 3.30)], 0.26, "currentColor"))
    out.append(stroke([(6.84, 3.36), (7.0, 2.6), (7.2, 1.6), (7.30, 0.92)], 0.22, "currentColor"))
    out.append(stroke([(5.30, 1.30), (5.50, 1.90), (5.70, 2.40), (5.86, 2.80)], 0.10, "currentColor"))   # boom ram
    out.append(stroke([(5.80, 3.62), (6.20, 3.75), (6.60, 3.75), (6.96, 3.56)], 0.09, "currentColor"))  # dipper ram
    out.append(stroke([(6.95, 1.5), (7.05, 1.25), (7.15, 1.05), (7.24, 0.92)], 0.07, "currentColor"))   # bucket ram
    return "".join(out)


def glass():
    """Cab windows: the sky shows straight through them (the giveaway of a real backlit photo)."""
    front = poly([(2.92, 1.74), (3.03, 2.72), (3.52, 2.72), (3.52, 1.74)])
    side = poly([(3.62, 1.74), (3.62, 2.72), (4.25, 2.72), (4.31, 1.62), (4.20, 1.58)])
    operator = ("<g opacity='0.55' filter='url(#b3)'><path d='M%s C%s %s %s C%s %s %s L%s L%s Z' fill='#2a1510'/>" % (
        p(3.78, 1.74), p(3.74, 2.02), p(3.80, 2.18), p(3.92, 2.22), p(4.06, 2.18), p(4.10, 2.02), p(4.06, 1.74),
        p(4.06, 1.74), p(3.78, 1.74)) +
        circ(3.93, 2.36, 0.12, fill="#2a1510") + "</g>" +
        stroke([(3.40, 1.90), (3.52, 1.98), (3.60, 2.0), (3.66, 1.96)], 0.05, "#1a0e0b"))
    return ("<g><path d='%s' fill='url(#glass)'/><path d='%s' fill='url(#glass2)'/>%s"
            "<path d='%s' fill='none' stroke='#fff0c8' stroke-width='1' opacity='0.35'/></g>" % (front, side, operator, front))


def clouds_filter():
    return ("<filter id='cloud' x='0' y='0' width='100%%' height='100%%'>"
            "<feTurbulence type='fractalNoise' baseFrequency='0.0016 0.0105' numOctaves='5' seed='23'/>"
            "<feColorMatrix type='matrix' values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 2.6 -1.25'/>"
            "<feGaussianBlur stdDeviation='1.2'/></filter>")


def skyline():
    """A hazy industrial site on the horizon: sheds, a chimney, a tower crane, distant poles."""
    random.seed(5)
    out = []
    x = 0
    while x < 1600:
        w = random.randint(40, 170)
        h = random.randint(8, 46)
        if random.random() < 0.35:   # tree clump
            for k in range(random.randint(3, 7)):
                out.append("<circle cx='%d' cy='%d' r='%d'/>" % (x + random.randint(0, w), HORIZON - random.randint(4, 22),
                                                                 random.randint(8, 18)))
        else:
            out.append("<rect x='%d' y='%d' width='%d' height='%d'/>" % (x, HORIZON - h, w, h + 6))
        if random.random() < 0.45:
            out.append("<path d='M%d %d L%d %d L%d %d Z'/>" % (x, HORIZON - h, x + w // 2, HORIZON - h - 12, x + w, HORIZON - h))
        x += w + random.randint(0, 30)
    out.append("<rect x='300' y='%d' width='9' height='70'/>" % (HORIZON - 108))       # chimney
    out.append("<rect x='520' y='%d' width='5' height='160'/>" % (HORIZON - 196))      # tower crane mast
    out.append("<path d='M440 %d L700 %d L700 %d L440 %d Z'/>" % (HORIZON - 196, HORIZON - 196, HORIZON - 191, HORIZON - 193))
    out.append("<line x1='522' y1='%d' x2='660' y2='%d' stroke='#000' stroke-width='1'/>" % (HORIZON - 214, HORIZON - 196))
    out.append("<rect x='519' y='%d' width='8' height='18'/>" % (HORIZON - 214))
    for px in range(40, 1600, 190):
        out.append("<rect x='%d' y='%d' width='2' height='34'/>" % (px, HORIZON - 30))
    return "".join(out)


def dust_motes():
    random.seed(17)
    out = []
    for _ in range(110):
        x = random.gauss(SUN[0] - 120, 300)
        y = random.gauss(SUN[1] - 40, 110)
        if X0 + 0.0 * S < x < X0 + 8.0 * S and y > G - 3.0 * S:
            continue
        r = random.choice([0.8, 1.1, 1.4, 1.8, 2.2, 3, 5])
        d = math.hypot(x - SUN[0], y - SUN[1])
        op = max(0.04, 0.55 - d / 900) * (0.6 if r > 6 else 1)
        out.append("<circle cx='%.0f' cy='%.0f' r='%.1f' fill='#ffd8a0' opacity='%.2f'/>" % (x, y, r, op))
    return "".join(out)


def ruts():
    random.seed(29)
    out = []
    for _ in range(70):
        y = random.uniform(HORIZON + 6, 860)
        k = (y - HORIZON) / (900 - HORIZON)
        x = random.uniform(-100, 1600)
        out.append("<ellipse cx='%.0f' cy='%.0f' rx='%.0f' ry='%.1f' fill='%s' opacity='%.2f'/>" % (
            x, y, 40 + 260 * k, 1 + 6 * k, random.choice(["#000", "#140a06", "#2a160c"]), random.uniform(0.25, 0.55)))
    return "".join(out)


def grass():
    random.seed(41)
    out = []
    for _ in range(90):
        x = random.choice([random.uniform(-20, 420), random.uniform(1380, 1620)])
        h = random.uniform(30, 120)
        lean = random.uniform(-40, 40)
        out.append("<path d='M%.0f 905 Q%.0f %.0f %.0f %.0f' stroke-width='%.1f' opacity='0.9'/>" % (
            x, x + lean * 0.3, 905 - h * 0.6, x + lean, 905 - h, random.uniform(2, 5)))
    return "".join(out)


def mounds():
    random.seed(53)
    out = []
    for cx, w, h in ((80, 260, 34), (300, 340, 22), (560, 220, 30), (760, 300, 16), (1560, 200, 26)):
        y = HORIZON + 8
        out.append("<path d='M%d %d C%d %d %d %d %d %d C%d %d %d %d %d %d Z' fill='#1e110b'/>" % (
            cx - w // 2, y, cx - w // 4, y - h, cx - w // 8, y - h * 1.1, cx, y - h, cx + w // 6, y - h * 0.9, cx + w // 3, y - h * 0.5,
            cx + w // 2, y))
        out.append("<path d='M%d %d C%d %d %d %d %d %d' fill='none' stroke='#f0a060' stroke-width='1.6' opacity='0.55'/>" % (
            cx - w // 2 + 10, y - 2, cx - w // 4, y - h, cx - w // 8, y - h * 1.1, cx, y - h))
    return "".join(out)


def stones():
    random.seed(61)
    out = []
    for _ in range(160):
        y = random.uniform(HORIZON + 14, 830)
        k = (y - HORIZON) / (900 - HORIZON)
        x = random.uniform(0, 1600)
        r = 1 + 7 * k * random.random()
        out.append("<ellipse cx='%.0f' cy='%.0f' rx='%.1f' ry='%.1f' fill='#120a07'/>"
                   "<ellipse cx='%.0f' cy='%.1f' rx='%.1f' ry='%.1f' fill='#d9905a' opacity='0.35'/>" % (
                       x, y, r * 1.6, r * 0.7, x - r * 0.3, y - r * 0.45, r * 0.9, r * 0.22))
    return "".join(out)


def tracks():
    out = []
    for off, w in ((-30, 16), (30, 16), (-150, 10), (-100, 10)):
        out.append("<path d='M%d 900 C%d 840 %d 800 %d %d' fill='none' stroke='#000' stroke-opacity='0.35' "
                   "stroke-width='%d' stroke-dasharray='5 4'/>" % (420 + off * 3, 600 + off * 2, 820 + off, 960 + off, G + 4, w))
    return "".join(out)


SVG = """<svg xmlns='http://www.w3.org/2000/svg' width='%(W)d' height='%(H)d' viewBox='0 0 %(W)d %(H)d'>
<defs>
 <linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'>
  <stop offset='0' stop-color='#0d0b1c'/><stop offset='0.18' stop-color='#22163a'/><stop offset='0.36' stop-color='#55203f'/>
  <stop offset='0.52' stop-color='#a5373a'/><stop offset='0.62' stop-color='#de6430'/><stop offset='0.69' stop-color='#f6a24a'/>
  <stop offset='0.735' stop-color='#ffd796'/><stop offset='1' stop-color='#ffd796'/></linearGradient>
 <radialGradient id='sunglow' cx='%(SX)d' cy='%(SY)d' r='900' gradientUnits='userSpaceOnUse'>
  <stop offset='0' stop-color='#fffbe8'/><stop offset='0.04' stop-color='#ffeab0'/><stop offset='0.13' stop-color='#ffb85a' stop-opacity='0.75'/>
  <stop offset='0.35' stop-color='#ff7a32' stop-opacity='0.30'/><stop offset='1' stop-color='#ff5a20' stop-opacity='0'/></radialGradient>
 <linearGradient id='cloudcol' x1='0' y1='0' x2='0' y2='1'>
  <stop offset='0' stop-color='#3a2448'/><stop offset='0.45' stop-color='#b4485a'/><stop offset='0.8' stop-color='#ffad6a'/>
  <stop offset='1' stop-color='#ffd9a0'/></linearGradient>
 <linearGradient id='ground' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#6a3a22'/><stop offset='0.12' stop-color='#3c2216'/>
  <stop offset='0.5' stop-color='#1d120d'/><stop offset='1' stop-color='#0a0607'/></linearGradient>
 <linearGradient id='glass' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#ffcf86'/><stop offset='0.55' stop-color='#ff9a4c'/>
  <stop offset='1' stop-color='#c85a34'/></linearGradient>
 <linearGradient id='glass2' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#e2794a'/><stop offset='1' stop-color='#ffbe72'/></linearGradient>
 <radialGradient id='rim' cx='0.35' cy='0.3' r='0.8'><stop offset='0' stop-color='#3b2a14'/><stop offset='0.6' stop-color='#1d150b'/>
  <stop offset='1' stop-color='#0c0807'/></radialGradient>
 <radialGradient id='beacon' cx='0.5' cy='0.5' r='0.5'><stop offset='0' stop-color='#ffe0a0'/><stop offset='0.25' stop-color='#ffa030' stop-opacity='0.8'/>
  <stop offset='1' stop-color='#ff8000' stop-opacity='0'/></radialGradient>
 <filter id='b1'><feGaussianBlur stdDeviation='1.1'/></filter>
 <filter id='b3' x='-20%%' y='-20%%' width='140%%' height='140%%'><feGaussianBlur stdDeviation='3'/></filter>
 <filter id='b8' x='-50%%' y='-50%%' width='200%%' height='200%%'><feGaussianBlur stdDeviation='8'/></filter>
 <filter id='b20' x='-50%%' y='-50%%' width='200%%' height='200%%'><feGaussianBlur stdDeviation='20'/></filter>
 <filter id='b50' x='-50%%' y='-50%%' width='200%%' height='200%%'><feGaussianBlur stdDeviation='50'/></filter>
 %(CLOUDF)s
 <filter id='soil' x='0' y='0' width='100%%' height='100%%'><feTurbulence type='fractalNoise' baseFrequency='0.045 0.11' numOctaves='4' seed='9'/>
  <feColorMatrix values='0 0 0 0 0.62  0 0 0 0 0.38  0 0 0 0 0.24  0 0 0 1.4 -0.62'/></filter>
 <mask id='cloudmask'><rect width='%(W)d' height='%(H)d' fill='#fff' filter='url(#cloud)'/></mask>
</defs>

<!-- sky, sun glow, cloud streaks lit from below -->
<rect width='%(W)d' height='%(H)d' fill='url(#sky)'/>
<rect width='%(W)d' height='%(H)d' fill='url(#sunglow)'/>
<rect width='%(W)d' height='%(HZ)d' fill='url(#cloudcol)' mask='url(#cloudmask)' opacity='0.85'/>
<rect width='%(W)d' height='%(HZ)d' fill='url(#sunglow)' mask='url(#cloudmask)' opacity='0.55'/>
<circle cx='%(SX)d' cy='%(SY)d' r='46' fill='#fffdf2'/>
<circle cx='%(SX)d' cy='%(SY)d' r='120' fill='#fff2c8' opacity='0.35' filter='url(#b20)'/>

<!-- far hills and the site on the horizon, flattened by haze -->
<path d='M0 %(HZ)d L0 618 C180 600 300 612 460 606 C620 598 760 616 900 610 C1100 600 1300 616 1600 604 L1600 %(HZ)d Z'
      fill='#7a3a46' opacity='0.55' filter='url(#b3)'/>
<g fill='#5a2a36' opacity='0.62' filter='url(#b3)'>%(SKYLINE)s</g>
<rect y='%(HZm)d' width='%(W)d' height='40' fill='#f6a868' opacity='0.35' filter='url(#b8)'/>

<!-- ground: soil texture, tyre tracks, heap -->
<rect y='%(HZ)d' width='%(W)d' height='%(GH)d' fill='url(#ground)'/>
<g filter='url(#b1)'><rect y='%(HZ)d' width='%(W)d' height='%(GH)d' filter='url(#soil)' opacity='0.22'/></g>
<g filter='url(#b8)' opacity='0.5'>%(RUTS)s</g>
<rect y='%(HZ)d' width='%(W)d' height='26' fill='#e8925a' opacity='0.22' filter='url(#b8)'/>
<g filter='url(#b3)'>%(MOUNDS)s</g>
%(STONES)s
%(TRACKS)s
<ellipse cx='%(MX)d' cy='%(GY)d' rx='420' ry='14' fill='#000' opacity='0.65' filter='url(#b8)'/>
<path d='M%(HEAP)s' fill='#24140d'/>
<path d='M%(HEAPRIM)s' fill='none' stroke='#ffa75a' stroke-width='2' opacity='0.5' filter='url(#b1)'/>

<!-- the machine: warm rim light on every edge facing the sun, body in deep shadow -->
<g filter='url(#b1)'>
 <g fill='#ffb455' color='#ffb455' filter='url(#b3)' opacity='0.85'>%(BODY)s</g>
 <g fill='#ffc574' color='#ffc574'>%(BODY)s</g>
 <g fill='#120c0a' color='#120c0a' transform='translate(2.2 2.6)'>%(BODY)s</g>
 <g fill='#1a120d' color='#1a120d' transform='translate(3.2 3.6)' opacity='0.9'>%(BODY)s</g>
 %(GLASS)s
 %(WHEELS)s
</g>
<circle cx='%(BX)d' cy='%(BY)d' r='34' fill='url(#beacon)'/>
<circle cx='%(BX)d' cy='%(BY)d' r='3' fill='#fff2c0'/>

<!-- dust kicked up and lit by the sun, motes in the air -->
<g filter='url(#b50)' opacity='0.55'>
 <ellipse cx='%(DX)d' cy='%(DY)d' rx='260' ry='70' fill='#f2a764'/>
 <ellipse cx='1300' cy='%(GY)d' rx='420' ry='40' fill='#e9945a'/>
 <ellipse cx='700' cy='%(GY)d' rx='300' ry='30' fill='#c8743e'/>
</g>
<g filter='url(#b1)'>%(MOTES)s</g>

<!-- foreground out of focus -->
<rect y='826' width='%(W)d' height='110' fill='#070405' opacity='0.8' filter='url(#b20)'/>
<g filter='url(#b8)' fill='none' stroke='#0a0605' stroke-linecap='round'>%(GRASS)s</g>
</svg>"""


def flare(im):
    """Lens flare: anamorphic streak through the sun and soft ghosts on the line through the frame centre."""
    from PIL import ImageDraw
    fl = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(fl)
    d.ellipse([SUN[0] - 420, SUN[1] - 1.5, SUN[0] + 420, SUN[1] + 1.5], fill=(200, 140, 80))
    fl = fl.filter(ImageFilter.GaussianBlur(3))
    gh = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(gh)
    cx, cy = W / 2, H / 2
    for t, r, col in ((0.5, 16, (90, 50, 20)), (1.3, 38, (50, 40, 30)), (1.65, 10, (90, 60, 30)), (2.1, 70, (30, 22, 26))):
        x, y = SUN[0] + (cx - SUN[0]) * t, SUN[1] + (cy - SUN[1]) * t
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    gh = gh.filter(ImageFilter.GaussianBlur(6))
    return ImageChops.screen(ImageChops.screen(im, fl), ImageEnhance.Brightness(gh).enhance(0.35))


def grade(png):
    im = Image.open(png).convert("RGB")
    bright = im.point(lambda v: max(0, v - 175) * 3)
    im = ImageChops.screen(im, bright.filter(ImageFilter.GaussianBlur(24)))       # bloom
    im = ImageChops.screen(im, ImageEnhance.Brightness(bright.filter(ImageFilter.GaussianBlur(90))).enhance(0.6))
    im = flare(im)
    # depth of field: the far horizon slightly soft, the machine sharp, the bottom strip very soft
    soft = im.filter(ImageFilter.GaussianBlur(2.2))
    mask = Image.new("L", (W, H), 0)
    for y in range(H):
        v = 0
        if y < 560:
            v = 110
        elif y > 800:
            v = min(255, (y - 800) * 4)
        mask.paste(v, (0, y, W, y + 1))
    im = Image.composite(soft, im, mask)
    # chromatic fringe (1 px), contrast, warm highlights / cool shadows
    r, g, b = im.split()
    r = ImageChops.offset(r, 1, 0)
    b = ImageChops.offset(b, -1, 0)
    im = Image.merge("RGB", (r, g, b))
    im = ImageEnhance.Contrast(im).enhance(1.06)
    r, g, b = im.split()
    im = Image.merge("RGB", (r.point(lambda v: min(255, int(v * 1.02 + 2))), g, b.point(lambda v: int(v * 0.93 + 6))))
    vig = Image.radial_gradient("L").resize((W, H)).point(lambda v: 255 - int(v * 0.7))
    im = Image.composite(im, Image.new("RGB", (W, H), (6, 4, 6)), vig)
    noise = Image.effect_noise((W, H), 26).convert("RGB")
    im = Image.blend(im, ImageChops.overlay(im, noise), 0.12)                       # film grain
    return im


def main():
    heap_pts = [(6.3, 0.0), (6.6, 0.28), (6.95, 0.42), (7.3, 0.40), (7.7, 0.30), (8.2, 0.05), (8.3, 0.0)]
    heap = " L".join(p(x, y) for x, y in heap_pts) + " Z"
    heaprim = " L".join(p(x, y) for x, y in heap_pts[:4])
    wheels = wheel(1.55, 0.48, 0.48) + wheel(3.72, 0.75, 0.75)
    svg = SVG % {"W": W, "H": H, "SX": SUN[0], "SY": SUN[1], "HZ": HORIZON, "HZm": HORIZON - 20, "GH": H - HORIZON,
                 "CLOUDF": clouds_filter(), "SKYLINE": skyline(), "TRACKS": tracks(), "BODY": machine_body(),
                 "GLASS": glass(), "WHEELS": wheels, "MOTES": dust_motes(), "RUTS": ruts(), "MOUNDS": mounds(), "STONES": stones(), "GRASS": grass(), "HEAP": heap, "HEAPRIM": heaprim,
                 "MX": X0 + 4 * S, "GY": G, "BX": X0 + 3.64 * S, "BY": G - 3.0 * S,
                 "DX": X0 + 7.0 * S, "DY": G - 30}
    tmp = os.path.join(HERE, "out")
    os.makedirs(tmp, exist_ok=True)
    sp, pp = os.path.join(tmp, "bg.svg"), os.path.join(tmp, "bg.png")
    open(sp, "w").write(svg)
    js = ("const {chromium}=require('/opt/node22/lib/node_modules/playwright');(async()=>{const b=await chromium.launch();"
          "const p=await b.newPage({viewport:{width:%d,height:%d}});await p.goto('file://%s');"
          "await p.screenshot({path:'%s'});await b.close();})();" % (W, H, sp, pp))
    subprocess.run(["node", "-e", js], check=True)
    grade(pp).save(OUT, "JPEG", quality=84, optimize=True, progressive=True)
    print("wrote", OUT, os.path.getsize(OUT) // 1024, "KB")


if __name__ == "__main__":
    main()
