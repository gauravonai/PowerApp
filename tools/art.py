"""Vector art for the theme (no image files: works with Paste code too).
Strings use single quotes only, so they sit inside Power Fx "..." text and go through EncodeUrl()."""

BG = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1366 768' preserveAspectRatio='xMidYMid slice'>
<defs>
<linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'>
<stop offset='0' stop-color='#120c1c'/><stop offset='0.30' stop-color='#3a1838'/><stop offset='0.50' stop-color='#8e2f3a'/>
<stop offset='0.63' stop-color='#e0662a'/><stop offset='0.71' stop-color='#ffb547'/><stop offset='0.75' stop-color='#ffd98a'/></linearGradient>
<radialGradient id='sun' cx='0.5' cy='0.5' r='0.5'><stop offset='0' stop-color='#fff4cc'/><stop offset='0.25' stop-color='#ffd36a' stop-opacity='0.85'/>
<stop offset='1' stop-color='#ff9a3c' stop-opacity='0'/></radialGradient>
<linearGradient id='shade' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#0b0b0e' stop-opacity='0.10'/>
<stop offset='0.62' stop-color='#0b0b0e' stop-opacity='0.30'/><stop offset='1' stop-color='#0b0b0e' stop-opacity='0.92'/></linearGradient>
</defs>
<rect width='1366' height='768' fill='url(#sky)'/>
<circle cx='1010' cy='520' r='230' fill='url(#sun)'/><circle cx='1010' cy='520' r='44' fill='#fff0bf'/>
<path d='M0 560 L120 520 L260 548 L380 505 L520 540 L640 512 L760 545 L900 515 L1040 548 L1180 520 L1366 552 L1366 768 L0 768 Z' fill='#2a1526' opacity='0.85'/>
<path d='M0 604 L200 590 L420 604 L640 588 L860 602 L1080 590 L1366 604 L1366 768 L0 768 Z' fill='#160d15'/>
<g fill='#0d080c'>
<rect x='760' y='520' width='250' height='42' rx='6'/>
<path d='M845 520 L845 448 L930 448 L948 520 Z'/>
<rect x='852' y='456' width='22' height='26' fill='#e0662a' opacity='0.55'/><rect x='880' y='456' width='40' height='26' fill='#e0662a' opacity='0.55'/>
<path d='M1010 528 L1070 488 L1120 500 L1132 540 L1108 548 L1098 522 L1066 516 L1022 548 Z'/>
<path d='M1112 540 L1158 556 L1150 580 L1110 572 Z'/>
<path d='M760 530 L690 470 L640 470 L600 520 L612 528 L646 488 L684 490 L748 552 Z'/>
<path d='M590 512 L640 512 L660 560 L578 560 Z'/><rect x='770' y='556' width='12' height='44' /><rect x='985' y='556' width='12' height='44'/>
<circle cx='820' cy='566' r='30'/><circle cx='960' cy='570' r='36'/>
</g>
<rect y='604' width='1366' height='164' fill='#120a10'/>
<rect width='1366' height='768' fill='url(#shade)'/>
</svg>"""

LOGO = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>
<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#ffd23f'/><stop offset='1' stop-color='#f57c1f'/></linearGradient></defs>
<path d='M32 2 L58 17 L58 47 L32 62 L6 47 L6 17 Z' fill='url(#g)'/>
<path d='M32 9 L52 20.5 L52 43.5 L32 55 L12 43.5 L12 20.5 Z' fill='#17120a'/>
<rect x='22' y='20' width='20' height='16' rx='3' fill='url(#g)'/>
<rect x='25' y='14' width='4' height='8' rx='1' fill='url(#g)'/><rect x='35' y='14' width='4' height='8' rx='1' fill='url(#g)'/>
<path d='M32 36 C32 44 24 44 24 50' stroke='url(#g)' stroke-width='3.5' fill='none' stroke-linecap='round'/>
</svg>"""

LINE = """<svg xmlns='http://www.w3.org/2000/svg' width='800' height='4' preserveAspectRatio='none' viewBox='0 0 800 4'>
<defs><linearGradient id='g' x1='0' x2='1'><stop offset='0' stop-color='#fdb913'/><stop offset='0.55' stop-color='#f7941d'/>
<stop offset='1' stop-color='#f7941d' stop-opacity='0'/></linearGradient></defs><rect width='800' height='4' fill='url(#g)'/></svg>"""

BAR = """<svg xmlns='http://www.w3.org/2000/svg' width='400' height='3' preserveAspectRatio='none' viewBox='0 0 400 3'>
<defs><linearGradient id='g' x1='0' x2='1'><stop offset='0' stop-color='COL'/><stop offset='1' stop-color='COL' stop-opacity='0.15'/></linearGradient></defs>
<rect width='400' height='3' fill='url(#g)'/></svg>"""


def one_line(s):
    return " ".join(x.strip() for x in s.strip().splitlines())


def uri(svg):
    """Power Fx expression for a data URI of this SVG."""
    return '"data:image/svg+xml;utf8," & EncodeUrl("%s")' % one_line(svg).replace('"', "'")


HEADER = BG.replace("viewBox='0 0 1366 768' preserveAspectRatio='xMidYMid slice'", "viewBox='0 360 1366 150' preserveAspectRatio='none'")

AVATAR = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'>
<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#ffd23f'/><stop offset='1' stop-color='#f57c1f'/></linearGradient></defs>
<circle cx='20' cy='20' r='19' fill='url(#g)'/><circle cx='20' cy='20' r='19' fill='none' stroke='#fff3d0' stroke-opacity='0.5'/></svg>"""


def photo_uri():
    """The background photograph (app/media/bg-backhoe.jpg, made by tools/make_bg.py) as a data URI, so the
    picture travels inside the formulas and works for Paste code too. To use your own photo: replace the file
    (any 1600 x 900 JPEG) and rebuild, or upload it in Studio > Media and set imgBg = <its name>."""
    import base64
    import os
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "media", "bg-backhoe.jpg")
    return '"data:image/jpeg;base64,%s"' % base64.b64encode(open(p, "rb").read()).decode()
