"""Every property used on every control must exist in that control's official template
(manifests extracted from Microsoft's own sample apps in microsoft/PowerApps-Tooling -> control_props.json).
Layout-child properties (FillPortions, LayoutMin*) are only allowed on children of auto-layout containers."""
import json
import sys

props = json.load(open("tools/verify/control_props.json"))
app = json.load(open("tools/out/app.json"))
by_name = {c["name"]: c for c in app["controls"]}
LAYOUT_CHILD = {"FillPortions", "LayoutMinHeight", "LayoutMinWidth", "AlignInContainer", "LayoutMaxHeight", "LayoutMaxWidth"}
bad, checked, unchecked = [], 0, set()
for c in app["controls"]:
    allowed = props.get(c["type"])
    if allowed is None:
        unchecked.add(c["type"])
        continue
    parent = by_name.get(c["parent"]) if c["parent"] else None
    in_auto = parent is not None and "LayoutDirection" in parent["props"]
    for p in c["props"]:
        checked += 1
        if p in LAYOUT_CHILD:
            if not in_auto:
                bad.append("%s.%s: layout-child property but parent %s is not auto-layout" % (c["name"], p, c["parent"]))
        elif p not in allowed:
            bad.append("%s (%s).%s: not a property of this control" % (c["name"], c["type"], p))
for b in bad[:40]:
    print(b)
print("property names: %d checked against official templates, %d problems; not checkable here: %s"
      % (checked, len(bad), ", ".join(sorted(unchecked)) or "none"))
sys.exit(len(bad))
