"""
Tiny builder for Power Apps canvas source (.pa.yaml, schema v3).

Every screen of the portal is described in Python (screens.py) with the helpers
below, then emitted twice from the same objects:
  * app/Src/<Screen>.pa.yaml          -> packed into the .msapp  (Route A)
  * paste/<NN>-<Screen>.yaml          -> "Paste code" into Studio (Route B)

Control type ids
  Written WITHOUT a version: per Microsoft's pa.yaml docs, "If no version is specified,
  the most current version of the control is used". (Pinned versions from an older
  sample produced PA2105 "older than the current version" warnings in Studio.)
"""
import re

CONTAINER = "GroupContainer"
LABEL = "Label"
RECT = "Rectangle"
IMAGE = "Image"
ICON = "Classic/Icon"
GALLERY = "Gallery"
GALLERY_VARIANT = "BrowseLayout_Vertical_OneTextVariant_ver5.0"
BUTTON = "Classic/Button"
TEXTINPUT = "Classic/TextInput"
DROPDOWN = "Classic/DropDown"
COMBOBOX = "Classic/ComboBox"
DATEPICKER = "Classic/DatePicker"
TIMER = "Timer"
ADDMEDIA = "AddMedia"

MONO = "fMono"
UI = "fUI"

ALL_NAMES = {}


class Ctl:
    def __init__(self, name, ctype, props=None, children=None, variant=None):
        if not re.match(r"^[A-Za-z][A-Za-z0-9_]*$", name):
            raise ValueError("bad control name " + name)
        self.name, self.ctype, self.variant = name, ctype, variant
        self.props = dict(props or {})
        self.children = list(children or [])

    def add(self, *kids):
        for k in kids:
            if isinstance(k, (list, tuple)):
                self.children.extend(k)
            elif k is not None:
                self.children.append(k)
        return self

    def walk(self):
        yield self
        for c in self.children:
            yield from c.walk()


def _fmt(v):
    """Python value -> Power Fx formula text (without the leading '=')."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v) if isinstance(v, float) else str(v)
    return str(v)


ACRONYMS = {"BOM", "PR", "PO", "UOM", "HSN", "GRN", "PDF", "FOC", "IDC", "EDS", "JCB", "OK",
            "BU", "DC", "FY", "INR", "ID", "GST", "AMC", "KW", "PR/PO"}
SMALL = {"a", "an", "and", "as", "at", "by", "for", "in", "of", "on", "or", "the", "to", "vs", "per", "from", "with",
         "into"}


def tc(text):
    """Title Case for titles, buttons, headers and field labels (sentences stay sentence case).
    Acronyms (BOM, PR/PO, HSN...) stay capitals; small words stay lower unless first."""
    out = []
    shout = text.isupper()
    for i, w in enumerate(text.split(" ")):
        core = w.strip("()·,.:;!?‹›+*/-—'\"")
        up = core.upper()
        code = ("(" in w or ")" in w) and len(core) <= 3 and core.isupper()     # (A), (B×C)
        if shout and up not in ACRONYMS and core not in ("NO", "M", "KG") and not code:
            w, core = w.lower(), core.lower()
        if not core or any(ch.isdigit() for ch in core) or core in ("₹",):
            out.append(w)
        elif core.endswith("s") and core[:-1] in ACRONYMS:      # PRs, POs
            out.append(w)
        elif code:
            out.append(w)
        elif up in ACRONYMS or (core.isupper() and len(core) <= 3 and core.isalpha() and core not in ("ALL", "NEW", "ADD", "SET", "OUT", "LOW", "MY")):
            out.append(w.replace(core, up))
        elif "/" in core and all(x.upper() in ACRONYMS for x in core.split("/")):
            out.append(w.replace(core, up))
        elif i > 0 and core.lower() in SMALL and not out[-1].endswith(("·", "—", ":")) and \
                not (core.lower() in ("in", "out", "up") and out[-1].lower() in ("log", "sign", "set")):
            out.append(w.replace(core, core.lower()))
        else:
            lw = core.lower() if core.isupper() else core
            out.append(w.replace(core, lw[:1].upper() + lw[1:]))
    return " ".join(out)


def tq(formula):
    """Title-case a Power Fx text literal ("...") and leave real formulas alone."""
    f = str(formula)
    if len(f) >= 2 and f[0] == '"' and f[-1] == '"' and '"' not in f[1:-1].replace('""', ''):
        return '"' + tc(f[1:-1]) + '"'
    return f


def q(s):
    """Python string -> Power Fx text literal."""
    return '"' + str(s).replace('"', '""') + '"'


# ---------------------------------------------------------------- emit
def _scalar(formula):
    f = "=" + formula
    risky = ("\n" in f or ": " in f or " #" in f or f.endswith(":") or f.endswith(" ")
             or "\t" in f or f.startswith("= "))
    return f, risky


def emit_props(props, ind):
    out = []
    for k in sorted(props):   # Studio writes properties alphabetically
        f, risky = _scalar(_fmt(props[k]))
        if risky:
            out.append(" " * ind + k + ": |-")
            for line in f.split("\n"):
                out.append(" " * (ind + 2) + line.rstrip() if line.strip() else "")
        else:
            out.append(" " * ind + k + ": " + f)
    return out


def emit_ctl(c, ind):
    """Emit one control as a sequence item:  - Name:\n    Control: ..."""
    p = " " * ind
    out = [p + "- " + c.name + ":"]
    out.append(p + "    Control: " + c.ctype)
    if c.variant:
        out.append(p + "    Variant: " + c.variant)
    if c.props:
        out.append(p + "    Properties:")
        out += emit_props(c.props, ind + 6)
    if c.children:
        out.append(p + "    Children:")
        for ch in c.children:
            out += emit_ctl(ch, ind + 6)
    return out


HEADER = """# ************************************************************************************************
# JCB EDS Lab Material Portal - Power Apps canvas source (pa.yaml schema v3)
# Generated by tools/build.py from tools/screens.py. Edit the Python, rebuild, do not hand-edit.
# ************************************************************************************************
"""


def emit_screen(name, screen_props, root):
    out = [HEADER.rstrip(), "Screens:", "  " + name + ":"]
    if screen_props:
        out.append("    Properties:")
        out += emit_props(screen_props, 6)
    out.append("    Children:")
    out += emit_ctl(root, 6)
    return "\n".join(out) + "\n"


def emit_paste(root):
    return "\n".join(emit_ctl(root, 0)) + "\n"


def emit_app(props):
    out = [HEADER.rstrip(), "App:", "  Properties:"]
    out += emit_props(props, 4)
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- controls
def box(name, x, y, w, h, kids=None, fill="cPanel", border="cLine", thick=1, auto=False,
        direction="Vertical", gap=0, pad=0, scroll=False, visible=None, extra=None, radius=0, shadow="None"):
    p = {"Fill": fill, "BorderColor": border, "BorderThickness": thick, "DropShadow": "DropShadow." + shadow,
         "RadiusTopLeft": radius, "RadiusTopRight": radius, "RadiusBottomLeft": radius, "RadiusBottomRight": radius}
    if x is not None:
        p.update({"X": x, "Y": y})
    if w is not None:
        p["Width"] = w
    if h is not None:
        p["Height"] = h
    if auto:
        p.update({"LayoutDirection": "LayoutDirection." + direction, "LayoutGap": gap,
                  "LayoutAlignItems": "LayoutAlignItems.Stretch",
                  "LayoutJustifyContent": "LayoutJustifyContent.Start",
                  "PaddingTop": pad, "PaddingBottom": pad, "PaddingLeft": pad, "PaddingRight": pad})
        if scroll:
            p["LayoutOverflowY"] = "LayoutOverflow.Scroll"
    if visible is not None:
        p["Visible"] = visible
    if extra:
        p.update(extra)
    return Ctl(name, CONTAINER, p, kids, "AutoLayout" if auto else "ManualLayout")


def lbl(name, text, x, y, w, h, size=13, color="cInk", bold=False, semibold=False, align="Left",
        font=UI, fill=None, valign="Middle", wrap=None, visible=None, extra=None, onselect=None, pad=0):
    p = {"Text": text, "X": x, "Y": y, "Width": w, "Height": h, "Size": size, "Color": color,
         "Font": font, "Align": "Align." + align, "VerticalAlign": "VerticalAlign." + valign,
         "PaddingLeft": pad, "PaddingRight": pad, "PaddingTop": 0, "PaddingBottom": 0,
         "FontWeight": "FontWeight.Bold" if bold else ("FontWeight.Semibold" if semibold else "FontWeight.Normal")}
    if fill:
        p["Fill"] = fill
    if wrap is not None:
        p["Wrap"] = wrap
    if visible is not None:
        p["Visible"] = visible
    if onselect:
        raise ValueError(name + ": clickable labels show the text cursor - use overlay() or btn()")
    if extra:
        p.update(extra)
    return Ctl(name, LABEL, p)


def rect(name, x, y, w, h, fill, visible=None, extra=None):
    p = {"X": x, "Y": y, "Width": w, "Height": h, "Fill": fill, "BorderColor": fill}
    if visible is not None:
        p["Visible"] = visible
    if extra:
        p.update(extra)
    return Ctl(name, RECT, p)


WRITES = re.compile(r"\b(Patch|Collect|Remove|RemoveIf|UpdateIf)\(\s*tbl")


def guard(f):
    """Every formula that writes to Excel is wrapped, so a failed save never fails silently:
    the person sees the connector's own message and the busy flag is cleared."""
    if not WRITES.search(f) or f.startswith("IfError("):
        return f
    return ('IfError(%s, Set(gBusy, false); Notify("Saving failed: " & FirstError.Message & '
            '" Nothing was changed. If someone has the lab data file open on their PC, ask them to close it, then try '
            'again.", NotificationType.Error))' % f)


BTN_KINDS = {
    #            fill                       text      border     hover fill               hover text  hover border
    "primary":   ("cJcb",                     "cOnJcb", "cJcb",    "cOrange",               "cOnJcb",   "cOrange"),
    "secondary": ("RGBA(255,255,255,0.08)",   "cInk",   "cLine2",  "cJcbWash",              "cJcb",     "cJcb"),
    "danger":    ("RGBA(242,114,98,0.10)",    "cStop",  "cStop",   "RGBA(242,114,98,0.24)", "cInk",     "cStop"),
    "ghost":     ("cClear",                   "cInk2",  "cClear",  "cJcbWash",              "cJcb",     "cClear"),
    "overlay":   ("cClear",                   "cClear", "cClear",  "cRowHover",             "cClear",   "cClear"),
}


def btn(name, text, x, y, w, h, onselect, kind="primary", visible=None, disabled=None, size=11, extra=None,
        radius=None, align="Center"):
    """Classic button = the arrow (hand) pointer, rounded, bold. kind: primary / secondary / danger / ghost / overlay
    ('overlay' is an invisible full-row button that makes a whole table row clickable with the hand pointer)."""
    fill, color, border, hfill, hcolor, hborder = BTN_KINDS[kind]
    r = radius if radius is not None else (0 if kind == "overlay" else min(10, int(h / 2) if isinstance(h, int) else 10))
    p = {"Text": tq(text), "X": x, "Y": y, "Width": w, "Height": h, "OnSelect": guard(onselect),
         "Fill": fill, "Color": color, "BorderColor": border, "BorderThickness": 0 if kind in ("ghost", "overlay") else 1,
         "HoverFill": hfill, "HoverColor": hcolor, "HoverBorderColor": hborder,
         "PressedFill": hfill, "PressedColor": hcolor, "PressedBorderColor": hborder,
         "DisabledFill": "RGBA(255,255,255,0.05)", "DisabledColor": "cInk3", "DisabledBorderColor": "cLine",
         "FocusedBorderColor": "cJcb", "FocusedBorderThickness": 0 if kind == "overlay" else 2,
         "RadiusTopLeft": r, "RadiusTopRight": r, "RadiusBottomLeft": r, "RadiusBottomRight": r,
         "Size": size, "FontWeight": "FontWeight.Bold", "Font": UI, "Align": "Align." + align,
         "PaddingLeft": 8, "PaddingRight": 8}
    if visible is not None:
        p["Visible"] = visible
    if disabled is not None:
        p["DisplayMode"] = "If(%s, DisplayMode.Disabled, DisplayMode.Edit)" % disabled
    if extra:
        p.update(extra)
    return Ctl(name, BUTTON, p)


def overlay(name, x, y, w, h, onselect, visible=None, tooltip=None):
    extra = {"Tooltip": q(tooltip)} if tooltip else None
    return btn(name, '""', x, y, w, h, onselect, kind="overlay", visible=visible, extra=extra)


# Inputs are light with dark text in EVERY state (normal, hover, pressed/typing, disabled).
# v1 set only Color, so hovering or typing fell back to black text on the dark fill.
INPUT_COLORS = {"Fill": "cInput", "Color": "cInputInk", "HoverFill": "cInputHover", "HoverColor": "cInputInk",
                "PressedFill": "cInput", "PressedColor": "cInputInk", "BorderColor": "cInputLine",
                "HoverBorderColor": "cJcb", "PressedBorderColor": "cJcb", "FocusedBorderColor": "cOrange",
                "FocusedBorderThickness": 2, "DisabledFill": "RGBA(255,255,255,0.10)", "DisabledColor": "cInk2",
                "DisabledBorderColor": "cLine", "BorderThickness": 1}


def inp(name, x, y, w, h, default='""', hint="", mode=None, number=False, visible=None, extra=None,
        size=12, font=UI, onchange=None, disabled=None):
    p = {"X": x, "Y": y, "Width": w, "Height": h, "Default": default, "HintText": q(hint),
         "Size": size, "Font": font, "PaddingLeft": 10, "PaddingRight": 6,
         "RadiusTopLeft": 8, "RadiusTopRight": 8, "RadiusBottomLeft": 8, "RadiusBottomRight": 8}
    p.update(INPUT_COLORS)
    if mode == "multi":
        p["Mode"] = "TextMode.MultiLine"
    if number:
        p["Format"] = "TextFormat.Number"
    if visible is not None:
        p["Visible"] = visible
    if onchange:
        p["OnChange"] = onchange
    if disabled is not None:
        p["DisplayMode"] = "If(%s, DisplayMode.Disabled, DisplayMode.Edit)" % disabled
    if extra:
        p.update(extra)
    return Ctl(name, TEXTINPUT, p)


def dd(name, x, y, w, h, items, default=None, visible=None, extra=None, onchange=None):
    p = {"X": x, "Y": y, "Width": w, "Height": h, "Items": items,
         "SelectionFill": "cJcb", "SelectionColor": "cOnJcb",
         "ChevronBackground": "cInput", "ChevronFill": "cOrange",
         "ChevronHoverBackground": "cJcb", "ChevronHoverFill": "cOnJcb",
         "Size": 12, "Font": UI, "PaddingLeft": 10}
    p.update(INPUT_COLORS)
    if default is not None:
        p["Default"] = default
    if visible is not None:
        p["Visible"] = visible
    if onchange:
        p["OnChange"] = onchange
    if extra:
        p.update(extra)
    return Ctl(name, DROPDOWN, p)


# Studio's current Classic/DatePicker rejects (PA2108) every Hover*/Pressed* colour and the calendar
# HoverDateFill / SelectedDateFill, although older control templates listed them. Only these are set.
DATE_COLORS = {k: v for k, v in INPUT_COLORS.items() if not k.startswith(("Hover", "Pressed"))}


def date(name, x, y, w, h, default="Today()", visible=None, extra=None):
    p = {"X": x, "Y": y, "Width": w, "Height": h, "DefaultDate": default, "Format": q("dd-mmm-yyyy"),
         "IconBackground": "cJcb", "IconFill": "cOnJcb",
         "Size": 12, "Font": UI, "PaddingLeft": 10,
         "IsEditable": "false", "StartYear": 2020, "EndYear": 2040}
    p.update(DATE_COLORS)
    if visible is not None:
        p["Visible"] = visible
    if extra:
        p.update(extra)
    return Ctl(name, DATEPICKER, p)


def gallery(name, x, y, w, h, items, row_h, kids, fill="RGBA(0,0,0,0)", visible=None, onselect=None,
            selected_fill=None, extra=None):
    p = {"X": x, "Y": y, "Width": w, "Height": h, "Items": items, "TemplateSize": row_h,
         "TemplatePadding": 0, "ShowScrollbar": "true", "Fill": fill, "BorderColor": "cLine",
         "BorderThickness": 0}
    if selected_fill:
        p["TemplateFill"] = selected_fill
    if visible is not None:
        p["Visible"] = visible
    if onselect:
        p["OnSelect"] = onselect
    if extra:
        p.update(extra)
    return Ctl(name, GALLERY, p, kids, GALLERY_VARIANT)


def img(name, x, y, w, h, image, visible=None, extra=None):
    p = {"X": x, "Y": y, "Width": w, "Height": h, "Image": image, "ImagePosition": "ImagePosition.Fit",
         "BorderColor": "RGBA(0,0,0,0)"}
    if visible is not None:
        p["Visible"] = visible
    if extra:
        p.update(extra)
    return Ctl(name, IMAGE, p)


def icon(name, x, y, w, h, ico, color="cInk2", onselect=None, visible=None, tooltip=None, pad=8):
    p = {"X": x, "Y": y, "Width": w, "Height": h, "Icon": "Icon." + ico, "Color": color,
         "PaddingTop": pad, "PaddingBottom": pad, "PaddingLeft": pad, "PaddingRight": pad}
    if onselect:
        p["OnSelect"] = guard(onselect)
        p["HoverColor"] = "cJcb"
        p["PressedColor"] = "cOrange"
    if visible is not None:
        p["Visible"] = visible
    if tooltip:
        p["Tooltip"] = q(tooltip)
        p["AccessibleLabel"] = q(tooltip)
    return Ctl(name, ICON, p)


def pill(name, x, y, w, status, h=22, visible=None):
    """Status pill: outlined, Title Case text (APPROVED is stored in Excel, Approved is shown)."""
    col = "Coalesce(LookUp(nfPill, K = Upper(%s)).C, cInk3)" % status
    txt = "Coalesce(LookUp(nfPill, K = Upper(%s)).D, %s)" % (status, status)
    return lbl(name, txt, x, y, w, h, size=9, color=col, bold=True, align="Center",
               visible=visible,
               extra={"BorderColor": col, "BorderThickness": 1, "Fill": "RGBA(0,0,0,0.25)", "Wrap": "false"})
