"""Builds the management walkthrough as ONE offline HTML slide deck (screenshots embedded).

    python3 tools/deck/build_deck.py [--proto]      -> docs/deck/EDS-Portal-Walkthrough.html

Each screen slide: app screenshot with numbered hotspots. Click a dot (or press Next) and the matching
control is spotlighted and its "Click -> What happens" text lights up. Arrow keys / buttons move on.
"""
import base64
import io
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
P1 = os.path.join(ROOT, "tools", "out", "p1png")
ALL = os.path.join(ROOT, "tools", "out", "png")
OUT = os.path.join(ROOT, "docs", "deck", "EDS-Portal-Walkthrough.html")
FONT = os.environ.get("DECK_FONT_DIR", "")


def png_uri(path, box, width):
    src = Image.open(path).convert("RGB")
    box = (box[0], box[1], min(box[2], src.width), min(box[3], src.height))
    im = src.crop(box)
    h = round(im.height * width / im.width)
    im = im.resize((width, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=86, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(), im.size


def font_css():
    if not FONT:
        return ""
    out = []
    for w in (600, 700, 800):
        p = os.path.join(FONT, "barlow-condensed-latin-%d-normal.woff2" % w)
        if os.path.exists(p):
            out.append("@font-face{font-family:'Deck Head';font-weight:%d;src:url(data:font/woff2;base64,%s)}"
                       % (w, base64.b64encode(open(p, "rb").read()).decode()))
    return "".join(out)


def screen(title, kicker, img, box, spots, result, notes, step=None):
    """spots: list of (x, y, (bx, by, bw, bh), heading, text) in screenshot pixels."""
    return {"kind": "screen", "title": title, "kicker": kicker, "img": img, "box": box, "spots": spots,
            "result": result, "notes": notes, "step": step}


SLIDES_PROTO = [
    {"kind": "title", "title": "EDS Lab Material Portal", "sub": "Phase 1 walkthrough · Engineer to Lab Admin",
     "who": "Gaurav Shelke · EDS Lab, Pune", "when": "October 2026",
     "notes": "Today I will show every page of the new portal and exactly what happens on each click, using real lab data."},
    {"kind": "flow", "title": "Phase 1 at a glance", "lead": "Engineer to Lab Admin in about 2 minutes, on live lab stock.",
     "steps": [("Log In", "02-login-engineer.png", "Username and password"),
               ("Check Stock", "04-check-stock.png", "Live on hand for every part"),
               ("BOM Compare", "05-bom-compare.png", "Paste the Excel BOM, see the gaps"),
               ("Raise Request", "06-new-request-filled.png", "Project details and BOM lines"),
               ("My Requests", "07-my-requests.png", "Track status any time"),
               ("Lab Admin", "10-lab-admin-queue.png", "Store sees it instantly")],
     "banner": "Tested end to end on the lab's real data before every release: login, stock search, BOM paste, "
               "request saved, Lab Admin sees it.",
     "notes": "This is the flow management asked for. The next slides walk through each step."},
    screen("BOM Compare", "Step 3 of 6 · Engineer", "05-bom-compare.png", (224, 80, 1366, 1100), [
        (286, 250, (266, 237, 1058, 120), "Paste the BOM",
         "Copy the rows straight from the Excel BOM: Sr, part number, description, qty. Units like NOS are fine."),
        (280, 389, (266, 371, 220, 36), "Compare Against Stock",
         "The app re-reads the latest stock and checks every line of the BOM."),
        (1312, 382, (826, 365, 500, 48), "Summary line",
         "How many lines were read, parts compared, found in stock and new parts."),
        (445, 452, (250, 441, 1090, 100), "Result tiles",
         "Available today, short, new parts and the estimated material value."),
        (1318, 652, (1150, 606, 170, 160), "Status per line",
         "Available · Shortage · Out of Stock · New Part, with on hand, reserved and short."),
        (1150, 580, (1144, 566, 180, 28), "Raise Part Request ›",
         "Opens New Request with these lines already filled in.")],
        "In seconds the engineer knows what the store can supply and what must be bought.",
        "Copy straight from the harness BOM in Excel. New Part means the lab has never stocked it; "
        "that is different from out of stock.", step=3),
    {"kind": "grid", "title": "Other pages (1 of 2)", "foot": "Lab Admin pages · already built",
     "items": [("Component Inventory", "scrInventory.png", "Full catalogue with store locations; Lab Admin edits locations."),
               ("Material Inward", "scrInward.png", "Book goods received (PO, FOC, return, scrap); stock updates at once."),
               ("Stock Transactions", "scrLedger.png", "Every movement with date, reference and who issued it."),
               ("High Demand Parts", "scrDemand.png", "Most-issued parts for the chosen period, to plan buying."),
               ("Brand New Purchase Part", "scrNewPart.png", "Engineer asks the lab to buy a part it has never stocked."),
               ("New Purchase Parts", "scrNewPartQ.png", "Lab Admin and Manager approve or reject those requests.")],
     "notes": "These pages are built and tested; they roll out after Phase 1."},
]


CSS = r"""
:root{--ui:'Segoe UI',Arial,'Liberation Sans',sans-serif;--y:#FCB026;--y2:#F39C12;--ink:#111;--ink2:#333;--mute:#6b6b6b;--line:#e6e4df;--bg:#fff;--soft:#f6f5f2}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:#2a2a2a;font-family:var(--ui);color:var(--ink)}
.stage{position:fixed;inset:0;display:flex;align-items:center;justify-content:center}
.deck{position:relative;width:1280px;height:720px;transform-origin:center;background:var(--bg);overflow:hidden;
 box-shadow:0 20px 60px rgba(0,0,0,.45)}
.slide{position:absolute;inset:0;padding:34px 48px 0;display:none}
.slide.on{display:block;animation:in .35s ease}
@keyframes in{from{opacity:0;transform:translateX(18px)}to{opacity:1;transform:none}}
.hd{font:800 40px/1 'Deck Head','Arial Narrow',Arial;text-transform:uppercase;letter-spacing:.3px}
.kick{font:600 13px/1 var(--ui),Arial;color:var(--mute);letter-spacing:1.2px;text-transform:uppercase;margin-bottom:8px}
.rule{width:84px;height:6px;background:var(--y);margin:12px 0 0}
.foot{position:absolute;left:48px;right:48px;bottom:0;height:46px;display:flex;align-items:center;gap:14px;
 border-top:1px solid var(--line);font:600 12px var(--ui);color:var(--mute)}
.foot .sp{flex:1}
.logo{display:inline-flex;align-items:center;justify-content:center;background:#111;color:#fff;border-radius:5px;
 font:800 22px/1 'Deck Head','Arial Narrow',Arial;padding:4px 10px 4px 18px;position:relative;box-shadow:inset 0 0 0 2px #fff}
.logo:before{content:'';position:absolute;left:5px;top:5px;width:7px;height:7px;background:var(--y);border:1px solid #fff}
.progress{position:absolute;left:0;top:0;height:5px;background:var(--y);transition:width .3s}
/* title */
.title-s{background:var(--y);padding:0}
.title-s .tx{position:absolute;inset:0;opacity:.06;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='104'%3E%3Cpath d='M30 2L58 18V50L30 66L2 50V18Z M90 54L118 70V102L90 118L62 102V70Z' fill='none' stroke='%23000' stroke-width='2'/%3E%3C/svg%3E")}
.title-s h1{position:absolute;left:84px;top:262px;font:800 96px/0.95 'Deck Head','Arial Narrow',Arial;text-transform:uppercase}
.title-s h2{position:absolute;left:88px;top:370px;font:700 28px 'Deck Head','Arial Narrow',Arial;text-transform:uppercase;letter-spacing:.5px}
.title-s .meta{position:absolute;left:88px;bottom:58px;display:flex;gap:70px;font:20px var(--ui),Arial}
.title-s .logo{position:absolute;right:70px;bottom:44px;font-size:56px;padding:10px 26px 8px 44px;border-radius:8px;box-shadow:inset 0 0 0 4px #fff}
.title-s .logo:before{left:10px;top:10px;width:16px;height:16px;border-width:2px}
/* flow */
.lead{font:19px var(--ui);color:var(--ink2);margin-top:18px}
.flow{display:grid;grid-template-columns:repeat(6,1fr);gap:18px;margin-top:40px}
.fs .no{display:inline-block;background:var(--y);font:800 14px 'Deck Head','Arial Narrow';padding:3px 10px;border-radius:12px;letter-spacing:.5px}
.fs h3{font:800 24px 'Deck Head','Arial Narrow';text-transform:uppercase;margin:8px 0 8px}
.fs img{width:100%;height:150px;object-fit:cover;object-position:left top;border-radius:6px;border:1px solid #ccc;box-shadow:0 6px 16px rgba(0,0,0,.18);transition:transform .2s}
.fs:hover img{transform:translateY(-4px)}
.fs p{font:14px/1.35 var(--ui);color:var(--ink2);margin-top:8px}
.banner{margin-top:56px;background:var(--soft);border-left:8px solid var(--y);padding:14px 18px;font:16px/1.4 var(--ui);color:var(--ink)}
/* screen */
.scr{display:grid;grid-template-columns:690px 1fr;gap:28px;margin-top:22px}
.shot{position:relative;width:690px;height:520px;overflow:hidden;border-radius:8px;border:1px solid #cfcfcf;
 box-shadow:0 10px 26px rgba(0,0,0,.22);background:#111}
.shot img{position:absolute;left:0;top:0;width:690px}
.dim{position:absolute;inset:0;pointer-events:none;transition:opacity .25s}
.ring{position:absolute;border:3px solid var(--y);border-radius:6px;box-shadow:0 0 0 2000px rgba(0,0,0,.45),0 0 18px var(--y);
 transition:all .3s ease;pointer-events:none;opacity:0}
.ring.on{opacity:1}
.dot{position:absolute;width:30px;height:30px;margin:-15px 0 0 -15px;border-radius:50%;background:var(--y);border:3px solid #111;
 font:800 16px/24px 'Deck Head','Arial Narrow';text-align:center;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.5);transition:transform .15s;z-index:3}
.dot:hover,.dot.on{transform:scale(1.18)}
.dot.on{background:#111;color:var(--y);border-color:var(--y)}
.side h4{font:800 20px 'Deck Head','Arial Narrow';text-transform:uppercase;letter-spacing:.4px;margin:2px 0 12px}
.it{display:flex;gap:12px;padding:6px 10px;border-radius:8px;cursor:pointer;transition:background .2s;margin-bottom:2px}
.it b{flex:0 0 26px;height:26px;border-radius:50%;background:var(--y);border:2px solid #111;font:800 14px/22px 'Deck Head','Arial Narrow';text-align:center}
.it .t{font:13.5px/1.32 var(--ui);color:var(--ink2)} .it .t i{font-style:normal;font-weight:700;color:var(--ink);display:block}
.it:hover{background:var(--soft)} .it.on{background:#fff6e0;box-shadow:inset 4px 0 0 var(--y)}
.res{margin-top:8px;border-left:8px solid var(--y);background:var(--soft);padding:12px 14px;font:15px/1.4 var(--ui)}
.res b{display:block;font:800 15px 'Deck Head','Arial Narrow';letter-spacing:.6px;text-transform:uppercase}
/* grid */
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px 26px;margin-top:24px}
.gc img{width:100%;height:170px;object-fit:cover;object-position:top;border-radius:6px;border:1px solid #ccc;box-shadow:0 6px 16px rgba(0,0,0,.16)}
.gc h3{font:800 21px 'Deck Head','Arial Narrow';text-transform:uppercase;margin-top:8px}
.gc p{font:13.5px/1.35 var(--ui);color:var(--ink2)}
/* controls + notes */
.nav{transition:opacity .4s;opacity:0;position:fixed;bottom:18px;left:50%;transform:translateX(-50%);display:flex;gap:10px;align-items:center;z-index:9}
.nav button{background:#111;color:#fff;border:0;border-radius:20px;padding:9px 18px;font:600 13px var(--ui);cursor:pointer}
.nav button:hover{background:var(--y);color:#111}
.nav span{color:#ddd;font:600 13px var(--ui);min-width:70px;text-align:center}
.notes{position:fixed;right:16px;top:16px;width:300px;background:#fffdf5;border-left:6px solid var(--y);padding:12px 14px;
 font:14px/1.45 var(--ui);display:none;z-index:9;box-shadow:0 8px 24px rgba(0,0,0,.35)} .notes.on{display:block}
.notes b{display:block;font:800 13px var(--ui);margin-bottom:4px;letter-spacing:.5px}
@media print{.nav,.notes,.progress{display:none}html,body{background:#fff}.stage{position:static;display:block}
 .deck{transform:none!important;box-shadow:none;page-break-after:always;height:auto}.slide{position:relative;display:block;height:720px;page-break-after:always}}
.nav.show{opacity:1}"""

JS = r"""
const slides=[...document.querySelectorAll('.slide')];let cur=0,spot=-1;
function fit(){const d=document.querySelector('.deck');const s=Math.min(innerWidth/1300,innerHeight/770);d.style.transform='scale('+s+')'}
function show(i){cur=Math.max(0,Math.min(slides.length-1,i));spot=-1;slides.forEach((s,k)=>s.classList.toggle('on',k===cur));
 setSpot(-1);document.querySelector('.progress').style.width=((cur+1)/slides.length*100)+'%';
 document.getElementById('pg').textContent=(cur+1)+' / '+slides.length;
 document.getElementById('nt').innerHTML='<b>SPEAKER NOTES</b>'+(slides[cur].dataset.notes||'');location.hash=cur+1}
function setSpot(n){const s=slides[cur];spot=n;
 s.querySelectorAll('.dot').forEach((d,k)=>d.classList.toggle('on',k===n));
 s.querySelectorAll('.it').forEach((d,k)=>d.classList.toggle('on',k===n));
 const r=s.querySelector('.ring');if(!r)return;
 if(n<0){r.classList.remove('on');return}
 const d=s.querySelectorAll('.dot')[n];r.style.left=d.dataset.bx+'px';r.style.top=d.dataset.by+'px';
 r.style.width=d.dataset.bw+'px';r.style.height=d.dataset.bh+'px';r.classList.add('on')}
function next(){const n=slides[cur].querySelectorAll('.dot').length;if(spot<n-1&&n){setSpot(spot+1)}else show(cur+1)}
function prev(){if(spot>0)setSpot(spot-1);else if(spot===0)setSpot(-1);else show(cur-1)}
document.addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();next()}
 if(['ArrowLeft','PageUp'].includes(e.key))prev();if(e.key==='n')document.getElementById('nt').classList.toggle('on');
 if(e.key==='Escape')setSpot(-1)});
document.querySelectorAll('.dot').forEach(d=>d.addEventListener('click',e=>{e.stopPropagation();setSpot(+d.dataset.i)}));
document.querySelectorAll('.it').forEach(d=>d.addEventListener('click',()=>setSpot(+d.dataset.i)));
let ht;addEventListener('mousemove',()=>{const n=document.querySelector('.nav');n.classList.add('show');clearTimeout(ht);ht=setTimeout(()=>n.classList.remove('show'),2200)});addEventListener('resize',fit);fit();show((+location.hash.slice(1)||1)-1);
"""


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def foot(n, total, left):
    return ("<div class='foot'><span>%s</span><span class='sp'></span><span>%d</span><span class='logo'>JCB</span></div>"
            % (esc(left), n))


def render(slides):
    out = []
    total = len(slides)
    for n, s in enumerate(slides, 1):
        notes = esc(s.get("notes", ""))
        if s["kind"] == "title":
            out.append("<section class='slide title-s' data-notes=\"%s\"><div class='tx'></div><h1>%s</h1><h2>%s</h2>"
                       "<div class='meta'><span>%s</span><span>%s</span></div><span class='logo'>JCB</span></section>"
                       % (notes, esc(s["title"]), esc(s["sub"]), esc(s["who"]), esc(s["when"])))
        elif s["kind"] == "flow":
            cells = "".join("<div class='fs'><span class='no'>STEP %d</span><h3>%s</h3><img src='%s'><p>%s</p></div>"
                            % (i + 1, esc(t), png_uri(os.path.join(P1, f), (224, 56, 1366, 900), 380)[0], esc(d))
                            for i, (t, f, d) in enumerate(s["steps"]))
            out.append("<section class='slide' data-notes=\"%s\"><div class='hd'>%s</div><div class='rule'></div>"
                       "<p class='lead'>%s</p><div class='flow'>%s</div><div class='banner'>%s</div>%s</section>"
                       % (notes, esc(s["title"]), esc(s["lead"]), cells, esc(s["banner"]), foot(n, total, "EDS Lab Material Portal · Phase 1")))
        elif s["kind"] == "grid":
            cells = "".join("<div class='gc'><img src='%s'><h3>%s</h3><p>%s</p></div>"
                            % (png_uri(os.path.join(ALL, f), (224, 56, 1366, 640), 740)[0], esc(t), esc(d))
                            for t, f, d in s["items"])
            out.append("<section class='slide' data-notes=\"%s\"><div class='hd'>%s</div><div class='rule'></div>"
                       "<div class='grid'>%s</div>%s</section>" % (notes, esc(s["title"]), cells, foot(n, total, s["foot"])))
        else:
            x0, y0, x1, y1 = s["box"]
            uri, (w, h) = png_uri(os.path.join(P1, s["img"]), s["box"], 1380)
            k = 690 / (x1 - x0)
            dots, items = [], []
            for i, (x, y, (bx, by, bw, bh), head, text) in enumerate(s["spots"]):
                dots.append("<div class='dot' data-i='%d' style='left:%.0fpx;top:%.0fpx' data-bx='%.0f' data-by='%.0f' "
                            "data-bw='%.0f' data-bh='%.0f'>%d</div>"
                            % (i, (x - x0) * k, (y - y0) * k, (bx - x0) * k - 4, (by - y0) * k - 4, bw * k + 8, bh * k + 8, i + 1))
                items.append("<div class='it' data-i='%d'><b>%d</b><div class='t'><i>%s</i>%s</div></div>"
                             % (i, i + 1, esc(head), esc(text)))
            out.append("<section class='slide' data-notes=\"%s\"><div class='kick'>%s</div><div class='hd'>%s</div><div class='rule'></div>"
                       "<div class='scr'><div class='shot'><img src='%s'><div class='ring'></div>%s</div>"
                       "<div class='side'><h4>Click → What happens</h4>%s<div class='res'><b>Result</b>%s</div></div></div>%s</section>"
                       % (notes, esc(s["kicker"]), esc(s["title"]), uri, "".join(dots), "".join(items), esc(s["result"]),
                          foot(n, total, s["kicker"])))
    return ("<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>EDS Lab Material Portal · Walkthrough</title><style>%s%s</style></head><body><div class='stage'><div class='deck'>"
            "<div class='progress'></div>%s</div></div><div class='nav'><button onclick='prev()'>‹ Back</button><span id='pg'></span>"
            "<button onclick='next()'>Next ›</button><button onclick=\"document.getElementById('nt').classList.toggle('on')\">Notes (N)</button></div>"
            "<div class='notes' id='nt'></div><script>%s</script></body></html>" % (font_css(), CSS, "".join(out), JS))


if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    html = render(SLIDES_PROTO)
    open(OUT, "w").write(html)
    print("wrote", OUT, len(html) // 1024, "KB")
