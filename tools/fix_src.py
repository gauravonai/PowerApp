"""Combined fix for Power Apps Studio import errors in pa.yaml sources (safe to run more than once).

  1. PA2108  Unknown property 'CalendarHeaderFill' (Classic/DatePicker)  -> the line is removed.
  2. PA2105  'GroupContainer@1.4.0' is older than the current version     -> the version is removed
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


def fix_text(t):
    t2 = BADPROP.sub("", t)
    t2 = VERSION.sub(r"\1", t2)
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
    return out


if __name__ == "__main__":
    for a in sys.argv[1:]:
        fix_msapp(a) if a.lower().endswith(".msapp") else fix_folder(a)
