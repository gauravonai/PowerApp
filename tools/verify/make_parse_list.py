"""formulas.json -> parse.json (App.Formulas split into one entry per named formula)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from split_formulas import split  # noqa: E402

items = json.load(open("tools/out/formulas.json"))
out = []
for it in items:
    if it.get("kind") == "formulas":
        out += [{"id": "App.Formulas." + n, "f": e} for n, e in split(it["f"])]
    else:
        out.append({"id": it["id"], "f": it["f"]})
json.dump(out, open("tools/out/parse.json", "w"))
