"""Builds the background picture: a backhoe loader backlit by a sunset on a dusty site.
Drawn as a detailed vector scene, rasterised in Chromium, then photo-graded with Pillow
(haze, bloom, dust, film grain, vignette) so it reads as a photograph, not clip-art.

    python3 tools/make_bg.py      -> app/media/bg-backhoe.jpg  (1600 x 900)
Needs node + playwright (build machine only). The JPEG is committed, so this rarely runs."""
import os
import random
import subprocess
import sys

from PIL import Image, ImageFilter, ImageChops, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "app", "media", "bg-backhoe.jpg")
W, H = 1600, 900
random.seed(7)


def clouds():
    out = []
    for _ in range(26):
        x, y = random.randint(-100, 1700), random.randint(60, 420)
        rx, ry = random.randint(120, 380), random.randint(10, 34)
        op = random.uniform(0.18, 0.5)
        col = random.choice(["#ff9a5a", "#e46a4a", "#ffb877", "#c2514a", "#ffcf8e"])
        out.append("<ellipse cx='%d' cy='%d' rx='%d' ry='%d' fill='%s' opacity='%.2f'/>" % (x, y, rx, ry, col, op))
    return "\n".join(out)


def ridge(y0, amp, step, seed):
    random.seed(seed)
    pts, x, y = ["M0 %d" % H], 0, y0
    while x <= W + step:
        y = max(y0 - amp, min(y0 + amp, y + random.randint(-amp // 3, amp // 3)))
        pts.append("L%d %d" % (x, y))
        x += step
    pts.append("L%d %d Z" % (W, H))
    return " ".join(pts)


def dust():
    out = []
    random.seed(11)
    for _ in range(60):
        x, y = random.randint(380, 1500), random.randint(640, 800)
        r = random.randint(30, 120)
        out.append("<circle cx='%d' cy='%d' r='%d' fill='#f0a060' opacity='%.3f'/>" % (x, y, r, random.uniform(0.03, 0.08)))
    return "\n".join(out)


MACHINE = """
<g id='machine' filter='url(#soft)'>
 <!-- backhoe (rear) : stabiliser legs -->
 <path d='M792 640 L812 640 L796 756 L812 770 L760 770 L776 756 Z' fill='url(#steel)'/>
 <path d='M846 640 L866 640 L858 756 L874 770 L824 770 L840 756 Z' fill='url(#steel)'/>
 <!-- swing frame -->
 <path d='M760 600 L880 590 L890 660 L770 668 Z' fill='url(#body)'/>
 <!-- boom (curved banana) -->
 <path d='M796 612 C786 560 770 500 742 452 C716 410 680 384 640 372 C618 366 600 376 600 394 C600 408 612 414 626 418
          C660 428 690 452 710 486 C730 520 744 566 752 624 Z' fill='url(#body)'/>
 <path d='M772 598 L716 470' stroke='#3a332b' stroke-width='8' stroke-linecap='round'/>
 <!-- dipper -->
 <path d='M598 392 L626 380 L566 640 L540 650 Z' fill='url(#body)'/>
 <path d='M612 420 L566 610' stroke='#2e2a25' stroke-width='6' stroke-linecap='round'/>
 <!-- backhoe bucket with teeth -->
 <path d='M538 640 C520 660 512 690 522 720 L586 712 C590 690 584 662 566 646 Z' fill='url(#body)'/>
 <path d='M522 720 L516 732 L530 728 L534 740 L546 726 L556 736 L562 722 L574 730 L586 712 Z' fill='#1b140d'/>
 <!-- rear counterweight / frame -->
 <path d='M860 600 L1010 596 L1012 676 L870 682 Z' fill='url(#body)'/>
 <!-- cab -->
 <path d='M872 470 L1032 470 L1040 476 L1036 488 L1022 488 L1018 600 L884 604 L882 488 L866 488 L864 476 Z' fill='url(#body)'/>
 <path d='M892 494 L1008 494 L1006 590 L896 594 Z' fill='url(#glass)'/>
 <path d='M948 494 L952 494 L952 592 L948 592 Z' fill='#1b140d'/>
 <path d='M900 500 L940 500 L938 540 Z' fill='#ffe2b0' opacity='0.18'/>
 <!-- operator seat silhouette -->
 <path d='M960 548 L986 548 L990 586 L958 588 Z' fill='#140d08' opacity='0.85'/>
 <!-- engine hood -->
 <path d='M1010 560 L1210 566 C1250 568 1282 586 1290 618 L1296 668 L1010 676 Z' fill='url(#body)'/>
 <path d='M1030 580 L1260 588' stroke='#f2c04a' stroke-width='1.5' opacity='0.18'/>
 <path d='M1040 600 L1270 608 M1040 616 L1272 624 M1040 632 L1274 640' stroke='#0d0906' stroke-width='3' opacity='0.5'/>
 <!-- exhaust -->
 <rect x='1100' y='512' width='12' height='56' rx='3' fill='url(#steel)'/>
 <!-- loader arms -->
 <path d='M1000 560 L1050 548 L1340 640 L1336 668 L1300 662 Z' fill='url(#body)'/>
 <path d='M1060 600 L1300 660' stroke='#2e2a25' stroke-width='7' stroke-linecap='round'/>
 <!-- loader bucket -->
 <path d='M1318 616 L1404 626 C1426 650 1440 700 1444 748 L1336 756 C1328 716 1320 676 1318 616 Z' fill='url(#body)'/>
 <path d='M1336 756 L1444 748 L1450 760 L1334 768 Z' fill='#120c08'/>
 <!-- axles / fenders -->
 <path d='M846 640 C850 600 1010 600 1016 640 L1016 660 L846 664 Z' fill='url(#body)'/>
 <path d='M1186 664 C1190 636 1306 636 1312 664 Z' fill='url(#body)'/>
 <!-- rear wheel -->
 <circle cx='930' cy='690' r='84' fill='#0e0a08'/>
 <circle cx='930' cy='690' r='84' fill='none' stroke='#2a221b' stroke-width='14' stroke-dasharray='10 9'/>
 <circle cx='930' cy='690' r='46' fill='url(#rim)'/>
 <circle cx='930' cy='690' r='14' fill='#1b140d'/>
 <!-- front wheel -->
 <circle cx='1250' cy='714' r='56' fill='#0e0a08'/>
 <circle cx='1250' cy='714' r='56' fill='none' stroke='#2a221b' stroke-width='10' stroke-dasharray='8 8'/>
 <circle cx='1250' cy='714' r='30' fill='url(#rim)'/>
 <circle cx='1250' cy='714' r='9' fill='#1b140d'/>
 <!-- rim light from the sun (top edges) -->
 <path d='M866 476 L1040 476 M1010 560 L1210 566 C1250 568 1282 586 1290 618 M600 390 C604 370 620 366 640 372 C680 384 716 410 742 452 C770 500 786 560 796 612
          M1318 616 L1404 626 C1426 650 1440 700 1444 748' fill='none' stroke='#ffb648' stroke-width='3' opacity='0.85'/>
 <path d='M846 640 C850 600 1010 600 1016 640 M1186 664 C1190 636 1306 636 1312 664' fill='none' stroke='#ffb648' stroke-width='2.5' opacity='0.7'/>
 <circle cx='930' cy='690' r='84' fill='none' stroke='#ff9d3c' stroke-width='2' opacity='0.45' stroke-dasharray='120 400' transform='rotate(-120 930 690)'/>
 <circle cx='1250' cy='714' r='56' fill='none' stroke='#ff9d3c' stroke-width='2' opacity='0.45' stroke-dasharray='80 300' transform='rotate(-120 1250 714)'/>
</g>"""

SVG = """<svg xmlns='http://www.w3.org/2000/svg' width='%(W)d' height='%(H)d' viewBox='0 0 %(W)d %(H)d'>
<defs>
 <linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'>
  <stop offset='0' stop-color='#140d1c'/><stop offset='0.22' stop-color='#3b1a36'/><stop offset='0.42' stop-color='#8c2f38'/>
  <stop offset='0.58' stop-color='#d9612c'/><stop offset='0.68' stop-color='#f79a3c'/><stop offset='0.74' stop-color='#ffd38a'/></linearGradient>
 <radialGradient id='sun' cx='0.5' cy='0.5' r='0.5'><stop offset='0' stop-color='#fff8e0'/><stop offset='0.12' stop-color='#ffe7a8'/>
  <stop offset='0.35' stop-color='#ffb24a' stop-opacity='0.55'/><stop offset='1' stop-color='#ff7a2a' stop-opacity='0'/></radialGradient>
 <linearGradient id='body' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#2a1d0c'/><stop offset='0.3' stop-color='#160f08'/>
  <stop offset='1' stop-color='#060403'/></linearGradient>
 <linearGradient id='steel' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#15110d'/><stop offset='0.5' stop-color='#3a332b'/>
  <stop offset='1' stop-color='#15110d'/></linearGradient>
 <radialGradient id='rim' cx='0.4' cy='0.35' r='0.7'><stop offset='0' stop-color='#3a2c12'/><stop offset='1' stop-color='#110c06'/></radialGradient>
 <linearGradient id='glass' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#ff9f4a' stop-opacity='0.75'/>
  <stop offset='0.6' stop-color='#a8452c' stop-opacity='0.6'/><stop offset='1' stop-color='#2a1410' stop-opacity='0.9'/></linearGradient>
 <linearGradient id='ground' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#4a2a18'/><stop offset='0.25' stop-color='#2a1810'/>
  <stop offset='1' stop-color='#0c0807'/></linearGradient>
 <filter id='blur6' x='-50%%' y='-50%%' width='200%%' height='200%%'><feGaussianBlur stdDeviation='6'/></filter>
 <filter id='blur18' x='-50%%' y='-50%%' width='200%%' height='200%%'><feGaussianBlur stdDeviation='18'/></filter>
 <filter id='blur40' x='-50%%' y='-50%%' width='200%%' height='200%%'><feGaussianBlur stdDeviation='40'/></filter>
 <filter id='soft'><feGaussianBlur stdDeviation='1.1'/></filter>
 <filter id='terrain'><feTurbulence type='fractalNoise' baseFrequency='0.9 0.08' numOctaves='3' seed='4'/>
  <feColorMatrix values='0 0 0 0 0.10  0 0 0 0 0.06  0 0 0 0 0.03  0 0 0 0.55 0'/><feComposite in2='SourceGraphic' operator='in'/></filter>
</defs>
<rect width='%(W)d' height='%(H)d' fill='url(#sky)'/>
<g filter='url(#blur18)'>%(CLOUDS)s</g>
<circle cx='1150' cy='600' r='420' fill='url(#sun)'/>
<circle cx='1150' cy='600' r='54' fill='#fff4d2'/>
<g opacity='0.045' filter='url(#blur6)'>%(RAYS)s</g>
<path d='%(R1)s' fill='#5a2a35' opacity='0.55' filter='url(#blur6)'/>
<path d='%(R2)s' fill='#3a1a24' opacity='0.8' filter='url(#blur6)'/>
<!-- distant site: crane and a second machine in the haze -->
<g fill='#2a1420' opacity='0.75' filter='url(#blur6)'>
 <path d='M120 640 L150 600 L210 590 L236 612 L250 640 Z'/><path d='M236 612 L300 560 L330 566 L340 600 L322 604 L314 584 L256 626 Z'/>
 <circle cx='150' cy='646' r='12'/><circle cx='226' cy='646' r='12'/>
 <path d='M1460 640 L1520 600 L1560 606 L1566 640 Z'/><circle cx='1480' cy='650' r='14'/><circle cx='1545' cy='650' r='14'/>
</g>
<path d='%(R3)s' fill='url(#ground)'/>
<rect y='640' width='%(W)d' height='260' fill='#000' filter='url(#terrain)'/>
<ellipse cx='1000' cy='770' rx='560' ry='22' fill='#000' opacity='0.55' filter='url(#blur18)'/>
<g filter='url(#blur40)'>%(DUST)s</g>
%(MACHINE)s
<path d='M440 776 C470 720 520 700 560 712 C600 724 630 748 660 776 Z' fill='#140c08'/>
<path d='M470 744 C500 716 540 708 572 718' stroke='#ff9d3c' stroke-width='2' fill='none' opacity='0.45'/>
<g filter='url(#blur18)' opacity='0.55'><ellipse cx='560' cy='730' rx='120' ry='36' fill='#c7743a'/></g>
<g filter='url(#blur40)' opacity='0.28'><rect x='700' y='700' width='800' height='90' fill='#d98a48'/></g>
<g filter='url(#blur40)' opacity='0.30'><ellipse cx='540' cy='740' rx='200' ry='60' fill='#f0a060'/>
 <ellipse cx='1440' cy='760' rx='160' ry='40' fill='#f0a060'/></g>
<rect y='780' width='%(W)d' height='120' fill='#050304' opacity='0.55' filter='url(#blur18)'/>
</svg>"""


def rays():
    out = []
    for a in range(0, 360, 12):
        out.append("<path d='M1150 600 L%d %d L%d %d Z' fill='#ffd9a0'/>" % (
            1150 + 1400 * __import__("math").cos((a - 1.5) / 57.3), 600 + 1400 * __import__("math").sin((a - 1.5) / 57.3),
            1150 + 1400 * __import__("math").cos((a + 1.5) / 57.3), 600 + 1400 * __import__("math").sin((a + 1.5) / 57.3)))
    return "".join(out)


def grade(png):
    im = Image.open(png).convert("RGB")
    # bloom: bright areas glow
    bright = im.point(lambda v: max(0, v - 170) * 3)
    bloom = bright.filter(ImageFilter.GaussianBlur(28))
    im = ImageChops.screen(im, bloom)
    # slight lens softness, contrast and warmth
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    im = ImageEnhance.Contrast(im).enhance(1.08)
    r, g, b = im.split()
    im = Image.merge("RGB", (r.point(lambda v: min(255, v * 1.03)), g, b.point(lambda v: v * 0.94)))
    # vignette
    vig = Image.radial_gradient("L").resize((W, H)).point(lambda v: 255 - int(v * 0.75))
    im = Image.composite(im, Image.new("RGB", (W, H), (8, 5, 6)), vig)
    # film grain
    noise = Image.effect_noise((W, H), 22).convert("RGB")
    im = Image.blend(im, ImageChops.overlay(im, noise), 0.10)
    return im


def main():
    svg = SVG % {"W": W, "H": H, "CLOUDS": clouds(), "RAYS": rays(), "DUST": dust(), "MACHINE": MACHINE,
                 "R1": ridge(560, 40, 60, 1), "R2": ridge(610, 26, 45, 2), "R3": ridge(660, 12, 30, 3)}
    tmp = os.path.join(HERE, "out")
    os.makedirs(tmp, exist_ok=True)
    sp, pp = os.path.join(tmp, "bg.svg"), os.path.join(tmp, "bg.png")
    open(sp, "w").write(svg)
    js = ("const {chromium}=require('/opt/node22/lib/node_modules/playwright');(async()=>{const b=await chromium.launch();"
          "const p=await b.newPage({viewport:{width:%d,height:%d}});await p.goto('file://%s');"
          "await p.screenshot({path:'%s'});await b.close();})();" % (W, H, sp, pp))
    subprocess.run(["node", "-e", js], check=True)
    grade(pp).save(OUT, "JPEG", quality=80, optimize=True, progressive=True)
    print("wrote", OUT, os.path.getsize(OUT) // 1024, "KB")


if __name__ == "__main__":
    main()
