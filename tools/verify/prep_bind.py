"""Turn app.json into bind.json: every formula rewritten so the stand-alone Power Fx engine can bind it.
Only host (Studio) features are swapped for stand-ins; business logic is left untouched:
  Navigate(..)            -> MockNav(..)          (screens become text variables, so screen names are still checked)
  Notify(..)              -> MockNotify(..)
  Reset(ctl) / Refresh(t) -> true                 (Refresh target is still checked to be a data source)
  Print()                 -> true
  Select(Parent)          -> true
  Parent. / Self.         -> ParentX. / SelfX.    (supplied as typed parameters)
  OneDriveForBusiness.X(  -> MockX(
  User().Email/FullName   -> fixed test identity
"""
import json
import re
import sys

# enums that belong to the canvas host (Studio), not to the Power Fx core language
HOST_ENUMS = {"DropShadow", "Align", "VerticalAlign", "FontWeight", "ScreenTransition", "NotificationType",
              "LayoutDirection", "LayoutAlignItems", "LayoutJustifyContent", "LayoutOverflow", "ImagePosition",
              "TextMode", "TextFormat", "DisplayMode", "Icon", "AlignInContainer"}

TABLES = ["tblParts", "tblMoves", "tblUsers", "tblSettings", "tblProc", "tblLicenses", "tblNewPart", "tblInvoice",
          "tblPurch", "tblCalib", "tblRequests", "tblReqLines"]


def prep(f, email, name):
    f = f.replace("User().Email", '"%s"' % email).replace("User().FullName", '"%s"' % name)
    f = f.replace("Navigate(", "MockNav(").replace("Notify(", "MockNotify(")
    f = f.replace("OneDriveForBusiness.CreateFile(", "MockCreateFile(")
    f = f.replace("OneDriveForBusiness.GetFileContentByPath(", "MockGetFile(")
    f = f.replace("OneDriveForBusiness.GetFileMetadataByPath(", "MockMeta(")
    f = f.replace("Exit(true)", "true")
    f = re.sub(r"\bReset\(\s*\w+\s*\)", "true", f)
    for m in re.finditer(r"\bRefresh\(\s*(\w+)\s*\)", f):
        if m.group(1) not in TABLES:
            raise SystemExit("Refresh of unknown table " + m.group(1))
    f = re.sub(r"\bRefresh\(\s*\w+\s*\)", "true", f)
    f = f.replace("Print()", "true").replace("Select(Parent)", "true")
    f = re.sub(r"\bSetFocus\(\s*\w+\s*\)", "true", f)
    f = f.replace("Back()", "true")
    f = re.sub(r"\bParent\.", "ParentX.", f)
    f = re.sub(r"\bSelf\.", "SelfX.", f)
    return f


def main(app_json, out_json, email="gaurav.shelke@jcb.com", name="Gaurav Shelke"):
    app = json.load(open(app_json))
    enums = {}
    allf = [app["formulas"], app["onstart"]] + [v for c in app["controls"] for v in c["props"].values()]
    ctl_names = {c["name"] for c in app["controls"]}
    for f in allf:
        for a, b in re.findall(r"\b([A-Z][A-Za-z]+)\.([A-Z][A-Za-z]*)\b", f):
            if a not in HOST_ENUMS:
                continue
            enums.setdefault(a, set()).add(b)
    enums.setdefault("NotificationType", set()).update({"Success", "Error", "Warning", "Information"})
    enums.setdefault("ScreenTransition", set()).add("None")
    out = {
        "formulas": prep(app["formulas"], email, name),
        "named": ordered_named(prep(app["formulas"], email, name)),
        "onstart": prep(app["onstart"], email, name),
        "startscreen": app["startscreen"],
        "screens": app["screens"],
        "enums": {k: sorted(v) for k, v in enums.items()},
        "tests": app.get("tests", {}),
        "controls": [dict(c, props={k: prep(v, email, name) for k, v in c["props"].items()}) for c in app["controls"]],
    }
    json.dump(out, open(out_json, "w"), ensure_ascii=False)
    print("enums:", {k: len(v) for k, v in enums.items()})



def ordered_named(formulas_text):
    """Named formulas in dependency order (each one after everything it uses)."""
    sys.path.insert(0, __import__("os").path.dirname(__file__))
    from split_formulas import split
    pairs = split(formulas_text)
    names = {n for n, _ in pairs}
    deps = {n: {m for m in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", e) if m in names and m != n} for n, e in pairs}
    done, out = set(), []
    while len(out) < len(pairs):
        progressed = False
        for n, e in pairs:
            if n not in done and deps[n] <= done:
                out.append({"name": n, "expr": e}); done.add(n); progressed = True
        if not progressed:
            raise SystemExit("circular named formulas: " + ", ".join(n for n, _ in pairs if n not in done))
    return out


if __name__ == "__main__":
    main(*sys.argv[1:])
