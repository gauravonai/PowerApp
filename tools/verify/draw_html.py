"""Draw lists (from fxsim render) -> static HTML pages that approximate how Power Apps lays the screen out.
Power Apps 'Size' is in points, so text uses pt here too. This is a layout preview, not Power Apps."""
import html
import json
import os
import sys

GLYPH = {"Icon.Save": "&#10003;", "Icon.Cancel": "&#10005;", "Icon.ChevronRight": "&#8250;", "Icon.Home": "&#8962;",
         "Icon.Search": "&#9906;", "Icon.ListScrollWatchlist": "&#9776;", "Icon.AddDocument": "&#10010;",
         "Icon.Note": "&#9998;", "Icon.Add": "&#10010;", "Icon.Check": "&#10004;", "Icon.DocumentWithContent": "&#9636;",
         "Icon.Devices": "&#9638;", "Icon.ArrowDown": "&#8595;", "Icon.Sort": "&#8645;", "Icon.TrendingHashtag": "&#8599;",
         "Icon.Draw": "&#9997;", "Icon.HalfFilledCircle": "&#9681;", "Icon.Waypoint": "&#10148;", "Icon.ArrowRight": "&#8594;",
         "Icon.Lock": "&#9919;", "Icon.People": "&#9787;", "Icon.Information": "&#8505;", "Icon.Person": "&#9786;",
         "Icon.Settings": "&#9881;", "Icon.Edit": "&#9998;"}


def css_align(a, v):
    j = {"Align.Center": "center", "Align.Right": "flex-end"}.get(a, "flex-start")
    al = {"VerticalAlign.Top": "flex-start", "VerticalAlign.Bottom": "flex-end"}.get(v, "center")
    ta = {"Align.Center": "center", "Align.Right": "right"}.get(a, "left")
    return j, al, ta


def item(d):
    x, y, w, h = d["x"], d["y"], d["w"], d["h"]
    st = "left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;" % (x, y, max(w, 0), max(h, 0))
    k = d["k"]
    fill = d.get("Fill") or "transparent"
    col = d.get("Color") or "#eae8e3"
    bc = d.get("BorderColor") or "transparent"
    bt = d.get("BorderThickness") or "0"
    size = float(d.get("Size") or 13)
    bold = "700" if "Bold" in (d.get("FontWeight") or "") else "600" if "Semibold" in (d.get("FontWeight") or "") else "400"
    font = d.get("Font") or "'Segoe UI', sans-serif"
    j, al, ta = css_align(d.get("Align"), d.get("VerticalAlign"))
    rad = float(d.get("RadiusTopLeft") or 0)
    if k in ("box", "rect"):
        return '<div class="pa" style="%sbackground:%s;border:%spx solid %s;box-sizing:border-box;border-radius:%spx;overflow:hidden"></div>' % (st, fill, bt if k == "box" else 0, bc, rad)
    if k == "label":
        txt = html.escape(d.get("Text") or "")
        wrap = "normal" if d.get("Wrap") == "true" else "nowrap"
        return ('<div class="pa" style="%sbackground:%s;color:%s;border:%spx solid %s;box-sizing:border-box;display:flex;justify-content:%s;'
                'align-items:%s;text-align:%s;font:%s %.1fpt %s;white-space:%s;overflow:hidden;padding:0 %spx">%s</div>'
                % (st, fill, col, bt, bc, j, al, ta, bold, size, font, wrap, d.get("PaddingLeft") or 0, txt))
    if k == "button":
        return ('<div class="pa" style="%sbackground:%s;color:%s;border:%spx solid %s;box-sizing:border-box;display:flex;justify-content:%s;'
                'align-items:center;font:%s %.1fpt %s;white-space:nowrap;overflow:hidden;border-radius:%spx;padding-left:%spx;cursor:pointer">%s</div>'
                % (st, fill, col, bt, bc, j if d.get("Align") else "center", bold, size, font, rad, d.get("PaddingLeft") or 0,
                   html.escape(d.get("Text") or "")))
    if k in ("input", "dropdown", "date"):
        val = d.get("Default") or "" if k == "input" else d.get("Text") or ""
        if k == "date":
            val = d.get("DefaultDate") or ""
            val = val[:11]
        hint = not val and k == "input"
        txt = html.escape(d.get("HintText") or "" if hint else val)
        multi = d.get("Mode") == "TextMode.MultiLine"
        extra = '<span style="position:absolute;right:8px;top:50%%;transform:translateY(-50%%);color:%s">%s</span>' % (
            "#a3a8b0", "&#8964;" if k == "dropdown" else "&#128197;") if k != "input" else ""
        return ('<div class="pa" style="%sbackground:%s;color:%s;border:1px solid %s;box-sizing:border-box;display:flex;align-items:%s;'
                'font:400 %.1fpt %s;white-space:%s;overflow:hidden;padding:%s 10px;border-radius:%spx">%s%s</div>'
                % (st, fill, "#8a8078" if hint else col, bc, "flex-start" if multi else "center", size, font,
                   "pre-wrap" if multi else "nowrap", "6px" if multi else "0", rad, txt, extra))
    if k == "image":
        src = d.get("Image") or ""
        if src.startswith("data:image"):
            fit = {"ImagePosition.Fill": "cover", "ImagePosition.Stretch": "fill"}.get(d.get("ImagePosition"), "contain")
            return '<img class="pa" style="position:absolute;%sobject-fit:%s;border-radius:%spx" src="%s">' % (st, fit, rad, html.escape(src))
        return '<div class="pa" style="%sbackground:#24272d;color:#71767e;font:9pt sans-serif;display:flex;align-items:center;justify-content:center">image</div>' % st
    if k == "icon":
        return '<div class="pa" style="%scolor:%s;display:flex;align-items:center;justify-content:center;font:700 13pt sans-serif">%s</div>' % (
            st, col, GLYPH.get(d.get("Icon"), "&#9679;"))
    if k == "html":
        return '<div class="pa" style="%soverflow:auto;color:#000">%s</div>' % (st, d.get("HtmlText") or "")
    if k == "media":
        return '<div class="pa" style="%sbackground:%s;border:1px dashed #71767e;color:#a3a8b0;display:flex;align-items:center;justify-content:center;font:10pt sans-serif">Tap or click to add a picture</div>' % (st, fill)
    return ""


def main(src, dst):
    os.makedirs(dst, exist_ok=True)
    for f in sorted(os.listdir(src)):
        items = json.load(open(os.path.join(src, f)))
        hmax = 768
        for d in items:
            if d["k"] == "grow":
                hmax = max(hmax, d["y"])
        body = "\n".join(item(d) for d in items if d["k"] != "grow")
        page = ('<!doctype html><html><head><meta charset="utf-8"><style>body{margin:0;background:#15161a}'
                'div.pa,img.pa{position:absolute;box-sizing:border-box}</style></head><body><div style="position:relative;width:1366px;height:%dpx">%s</div></body></html>'
                % (hmax, body))
        open(os.path.join(dst, f.replace(".json", ".html")), "w").write(page)
    print("html pages:", len(os.listdir(dst)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
