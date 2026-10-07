"""Combined fix for Power Apps Studio import errors in pa.yaml sources (safe to run more than once).

  1. PA2108  Unknown property 'CalendarHeaderFill' (Classic/DatePicker)  -> the line is removed.
  2. PA2108  Unknown property 'HoverColor' / 'HoverFill' / 'HoverBorderColor' / 'HoverDateFill' / 'PressedColor' /
     'PressedFill' / 'PressedBorderColor' / 'SelectedDateFill' for control type 'Classic/DatePicker'
     -> removed, but only inside date pickers (text boxes and dropdowns accept them).
  3. PA2105  'GroupContainer@1.4.0' is older than the current version     -> the version is removed
     from every control type ("GroupContainer@1.4.0" -> "GroupContainer"), so Studio always uses its
     current version. Pinning "@1.5.0" instead would raise the same warning again at Microsoft's next update.

Usage
    python3 tools/fix_src.py app/Src                 # a folder of *.pa.yaml (or paste/*.yaml)
    python3 tools/fix_src.py OldApp.msapp            # an .msapp: writes OldApp-fixed.msapp next to it
"""
import os
import re
import sys
import zipfile

VERSION = re.compile(r"^(\s*Control:\s*[A-Za-z0-9/]+)@[0-9][0-9.]*\s*$", re.M)
BADPROP = re.compile(r"^\s*CalendarHeaderFill:.*\n", re.M)


DATEPICKER_BAD = ("HoverBorderColor", "HoverColor", "HoverDateFill", "HoverFill", "PressedBorderColor",
                  "PressedColor", "PressedFill", "SelectedDateFill")
CONTROL = re.compile(r"^(\s*)Control:\s*([A-Za-z0-9/]+)")
PROP = re.compile(r"^(\s*)([A-Za-z]+):")


def datepicker_lines(lines):
    """Indexes of the rejected property lines (and their |- continuation lines) inside Classic/DatePicker controls."""
    out, ctl, ind, skip_ind = set(), None, -1, None
    for i, l in enumerate(lines):
        m = CONTROL.match(l)
        if m:
            ctl, ind = m.group(2), len(m.group(1))
            skip_ind = None
            continue
        if skip_ind is not None:
            if l.strip() == "" or len(l) - len(l.lstrip()) > skip_ind:
                out.add(i)
                continue
            skip_ind = None
        p = PROP.match(l)
        if ctl and ctl.endswith("DatePicker") and p and len(p.group(1)) > ind and p.group(2) in DATEPICKER_BAD:
            out.add(i)
            skip_ind = len(p.group(1))
        elif p and len(p.group(1)) < ind:
            ctl = None
    return out


def fix_text(t):
    t2 = BADPROP.sub("", t)
    t2 = VERSION.sub(r"\1", t2)
    lines = t2.split("\n")
    drop = datepicker_lines(lines)
    if drop:
        t2 = "\n".join(l for i, l in enumerate(lines) if i not in drop)
    return t2, (t != t2)


def fix_folder(d):
    n = 0
    for root, _, files in os.walk(d):
        for f in files:
            if f.endswith((".yaml", ".yml")):
                p = os.path.join(root, f)
                t, changed = fix_text(open(p, encoding="utf-8").read())
                if changed:
                    open(p, "w", encoding="utf-8").write(t)
                    n += 1
    print("fixed %d file(s) in %s" % (n, d))


def fix_msapp(src):
    dst = src[:-6] + "-fixed.msapp"
    n = 0
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith((".yaml", ".yml")):
                t, changed = fix_text(data.decode("utf-8"))
                if changed:
                    data, n = t.encode("utf-8"), n + 1
            zout.writestr(item, data)
    print("fixed %d file(s) -> %s" % (n, dst))


def check(text):
    """Used by the build: returns the problems still present (empty list = clean)."""
    out = []
    if VERSION.search(text):
        out.append("pinned control version: " + VERSION.search(text).group(0).strip())
    if "CalendarHeaderFill" in text:
        out.append("CalendarHeaderFill property")
    if datepicker_lines(text.split("\n")):
        out.append("Hover/Pressed/SelectedDateFill colour on a Classic/DatePicker")
    return out


if __name__ == "__main__":
    for a in sys.argv[1:]:
        fix_msapp(a) if a.lower().endswith(".msapp") else fix_folder(a)
