"""Layout helpers that reproduce the HTA's building blocks: page head, cards, tiles, tables."""
from pa import (tc, tq, Ctl, box, lbl, rect, btn, overlay, inp, dd, date, gallery, img, icon, pill, q, MONO, UI)

W = 1090          # usable content width (1142 content column - 2 x 26 padding)


def sec(name, h, kids, visible=None, fill="RGBA(0,0,0,0)", border="RGBA(0,0,0,0)", thick=0):
    """A fixed-height block inside the scrolling content column."""
    c = box(name, None, None, None, h, kids, fill=fill, border=border, thick=thick, visible=visible,
            extra={"FillPortions": 0, "LayoutMinHeight": h})
    return c


def head(key, title, sub, right=None, visible=None):
    """Page title (Title Case, white), one-line subtitle, gold-to-orange underline."""
    kids = [lbl("hdT" + key, tq(title), 0, 2, 820, 40, size=22, bold=True, color="cInk"),
            lbl("hdS" + key, sub, 0, 42, 1000, 22, size=12, color="cInk2"),
            img("hdL" + key, 0, 68, 260, 3, "imgLine", extra={"ImagePosition": "ImagePosition.Stretch"})]
    if right:
        kids += right
    return sec("hd" + key, 76, kids, visible=visible)


def card(name, title, h, kids, right=None, visible=None, title_is_formula=False):
    """Glass card: rounded, translucent dark panel, orange Title Case heading, thin divider."""
    t = title if title_is_formula else q(tc(title))
    base = [rect(name + "Tl", 16, 46, "Parent.Width - 32", 1, "cLine"),
            rect(name + "Ta", 16, 14, 4, 18, "cOrange"),
            lbl(name + "Tt", t, 28, 0, "Parent.Width - 240", 46, size=13, bold=True, color="cOrange")]
    c = box(name, None, None, None, h, base + (right or []) + list(kids), fill="cPanel", border="cLine",
            visible=visible, radius=14, extra={"FillPortions": 0, "LayoutMinHeight": h})
    return c


def tiles(name, specs, visible=None, h=100):
    """specs: list of (tone, title, value_formula, sub_formula). tone: a/g/r/w/b/m/'' -> accent colour."""
    tone = {"a": "cJcb", "g": "cOk", "r": "cStop", "w": "cWarn", "b": "cSteel", "m": "cLine2", "": "cLine2"}
    kids = []
    for i, (t, title, val, sub) in enumerate(specs):
        n = "%s%d" % (name, i)
        col = tone.get(t, t)
        kids.append(box(n, None, None, None, None, [
            rect(n + "Bar", 0, 0, 4, "Parent.Height", col),
            lbl(n + "T", q(tc(title)), 18, 12, "Parent.Width - 26", 18, size=10, color="cInk2", semibold=True),
            lbl(n + "V", val, 18, 30, "Parent.Width - 26", 36, size=24, bold=True, color="cInk"),
            lbl(n + "S", sub, 18, 66, "Parent.Width - 26", 30, size=9, color="cInk3", valign="Top", wrap=True),
        ], fill="cPanel", border="cLine", radius=12, extra={"FillPortions": 1, "LayoutMinWidth": 120}))
    row = box(name, None, None, None, h, kids, fill="RGBA(0,0,0,0)", border="RGBA(0,0,0,0)", thick=0,
              auto=True, direction="Horizontal", gap=14, visible=visible,
              extra={"FillPortions": 0, "LayoutMinHeight": h})
    return row


class Col:
    def __init__(self, title, w, expr=None, kind="text", align="Left", color="cInk", size=11, make=None,
                 bold=False, sub=None):
        self.title, self.w, self.expr, self.kind, self.align = title, w, expr, kind, align
        self.color, self.size, self.make, self.bold, self.sub = color, size, make, bold, sub


def table(pfx, items, cols, x=0, y=46, w=W, h=400, row_h=40, onrow=None, empty="Nothing here yet",
          empty_sub="", header_h=30, visible=None, row_fill=None):
    """HTA-style table: mono uppercase header strip + gallery rows with 1 px separators."""
    kids = []
    widths = [c.w for c in cols]
    fixed = sum(v for v in widths if v)
    flex = max(60, (w - 32 - fixed))
    xs, cx = [], 16
    for c in cols:
        cw = c.w or flex
        xs.append((cx, cw))
        cx += cw
    kids.append(rect(pfx + "Hb", x, y, w, header_h, "RGBA(255,255,255,0.06)"))
    kids.append(rect(pfx + "Hl", x, y + header_h - 1, w, 1, "cLine2"))
    for i, (c, (cx, cw)) in enumerate(zip(cols, xs)):
        if c.title:
            kids.append(lbl("%sH%d" % (pfx, i), q(tc(c.title)), x + cx, y, cw - 6, header_h, size=10,
                            color="cJcb", align=c.align if c.kind != "pill" else "Left", bold=True))
    row = []
    for i, (c, (cx, cw)) in enumerate(zip(cols, xs)):
        n = "%sC%d" % (pfx, i)
        sel = None
        if c.kind == "pill":
            row.append(pill(n, cx, int((row_h - 22) / 2), min(cw - 8, 150), c.expr))
        elif c.kind == "custom":
            row += c.make(n, cx, cw, row_h)
        else:
            font = MONO if c.kind == "mono" else UI
            size = 10 if c.kind in ("mono", "muted") else c.size
            color = "cInk3" if c.kind == "muted" else c.color
            if c.sub:
                row.append(lbl(n, c.expr, cx, 4, cw - 8, row_h / 2 - 2, size=size, color=color, font=font,
                               align=c.align, bold=c.bold, onselect=sel, valign="Bottom"))
                row.append(lbl(n + "s", c.sub, cx, row_h / 2 + 1, cw - 8, row_h / 2 - 5, size=10, color="cInk3",
                               align=c.align, onselect=sel, valign="Top"))
            else:
                row.append(lbl(n, c.expr, cx, 0, cw - 8, row_h, size=size, color=color, font=font,
                               align=c.align, bold=c.bold, onselect=sel))
    row.append(rect(pfx + "Sep", 0, row_h - 1, "Parent.TemplateWidth", 1, "cLine"))
    if onrow:   # on top of the row: the hand pointer, a hover highlight, and one click opens it
        row.append(overlay(pfx + "Go", 0, 0, "Parent.TemplateWidth", row_h, "Select(Parent)",
                           tooltip="Open this record"))
    g = gallery(pfx + "Gal", x, y + header_h, w, h - header_h, items, row_h, row, onselect=onrow,
                selected_fill=row_fill)
    kids.append(g)
    kids.append(lbl(pfx + "Emp", q(empty), x, y + header_h + 30, w, 28, size=14, bold=True,
                    color="cInk2", align="Center", visible="CountRows(%sGal.AllItems) = 0" % pfx))
    if empty_sub:
        kids.append(lbl(pfx + "Emp2", q(empty_sub), x, y + header_h + 60, w, 22, size=12, color="cInk3",
                        align="Center", visible="CountRows(%sGal.AllItems) = 0" % pfx))
    return kids


def field(name, label, x, y, w, ctl, req=False):
    """Label above an input, like the HTA .fg block. ctl is a function(name, x, y, w, h) -> Ctl."""
    return [lbl(name + "Lb", q(tc(label) + (" *" if req else "")), x, y, w, 16, size=10, color="cInk2",
                semibold=True),
            ctl(name, x, y + 18, w, 34)]


def meter(n, x, y, w, onhand, ref):
    pct = "If(%s > 0, Min(1, Max(0, %s / %s)), If(%s > 0, 1, 0))" % (ref, onhand, ref, onhand)
    col = "With({p: %s}, If(p <= 0.2, cStop, p <= 0.4, cWarn, cOk))" % pct
    return [rect(n + "Mb", x, y, w, 4, "cLine2"),
            rect(n + "Mf", x, y, "%d * %s" % (w, pct), 4, col)]


def kv(name, rows, x, y, w, kw=170, row_h=30):
    """Definition list (HTA dl.kv): muted key column, value column."""
    kids = []
    for i, (k, v) in enumerate(rows):
        kids.append(lbl("%sK%d" % (name, i), q(tc(k)), x, y + i * row_h, kw, row_h, size=10, color="cInk3",
                        semibold=True))
        if isinstance(v, Ctl):
            kids.append(v)
        else:
            kids.append(lbl("%sV%d" % (name, i), v, x + kw, y + i * row_h, w - kw, row_h, size=12, color="cInk"))
    return kids


def num(x, d=0):
    return 'Text(%s, "%s")' % (x, "#,##0" if d == 0 else "#,##0." + "0" * d)


def inr(x):
    return '"₹" & Text(%s, "#,##0.00")' % x


def inrs(x):
    return ('With({v: %s}, If(v >= 10000000, "₹" & Text(v / 10000000, "0.00") & " Cr", '
            'v >= 100000, "₹" & Text(v / 100000, "0.00") & " L", "₹" & Text(v, "#,##0")))' % x)


def fdate(x):
    return 'If(IsBlank(%s), "—", Text(%s, "dd-mmm-yyyy"))' % (x, x)


def noon(d="Today()"):
    """Dates are written at 12:00 local time so the UTC conversion inside the Excel
    connector can never move them to the previous day (IST is UTC+5:30)."""
    return "DateAdd(%s, 12, TimeUnit.Hours)" % d


def hist(reqno_expr, action_expr):
    """Append one {t,by,a} event to a request's History JSON array - never overwrite."""
    return ('With({h: Trim(Text(LookUp(tblRequests, Text(RequestNo) = %s).History)), '
            'e: JSON({t: Text(Now(), "yyyy-mm-ddThh:mm:ss"), by: gMeName, a: %s}, JSONFormat.Compact)}, '
            'If(Left(h, 1) <> "[" || Right(h, 1) <> "]", "[" & e & "]", h = "[]", "[" & e & "]", '
            'Left(h, Len(h) - 1) & "," & e & "]"))' % (reqno_expr, action_expr))


def cost(circ, mat):
    """Finance-locked formula. Returns a With() record: hours, mach, man, elec, asm, mat, trn, tot."""
    return ('With({c: Coalesce(%s, 0)}, With({h: c / kCktPerHr}, '
            '{ckt: c, hours: h, mach: (kDepPA / kStdHrsPA) * h, man: kRateHr * h, elec: kKwhHr * h, '
            'asm: (kDepPA / kStdHrsPA) * h + kRateHr * h + kKwhHr * h, mat: Coalesce(%s, 0), trn: kTransport, '
            'tot: Coalesce(%s, 0) + (kDepPA / kStdHrsPA) * h + kRateHr * h + kKwhHr * h + kTransport}))'
            % (circ, mat, mat))


def prepend(first, table_expr):
    """A one-column (Value) table with an extra first option, e.g. "All categories" + the categories."""
    return ('With({T: %s}, ForAll(Sequence(CountRows(T) + 1) As I, If(I.Value = 1, %s, Index(T, I.Value - 1).Value)))'
            % (table_expr, first))
