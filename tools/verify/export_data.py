"""Export every Excel table of the prepared workbook to JSON with a column type per column,
the way Power Apps' Excel connector would type them (number / text / datetime)."""
import datetime as dt
import json
import sys

import openpyxl


def main(xlsx, out):
    wb = openpyxl.load_workbook(xlsx)
    res = {}
    for ws in wb.worksheets:
        for tn in ws.tables:
            t = ws.tables[tn]
            rows = list(ws[t.ref])
            hdr = [c.value for c in rows[0]]
            types = {}
            for j, h in enumerate(hdr):
                kinds = {type(r[j].value).__name__ for r in rows[1:] if r[j].value is not None}
                if kinds <= {"int", "float"} and kinds:
                    types[h] = "n"
                elif kinds == {"datetime"}:
                    types[h] = "d"
                elif any(isinstance(r[j].value, str) and r[j].value.startswith("=") for r in rows[1:]):
                    types[h] = "s"          # calculated column (Licenses.Status) - text
                else:
                    types[h] = "s"
            data = []
            for r in rows[1:]:
                rec = {}
                for j, h in enumerate(hdr):
                    v = r[j].value
                    if v is None:
                        continue
                    if types[h] == "n":
                        rec[h] = float(v)
                    elif types[h] == "d":
                        rec[h] = v.strftime("%Y-%m-%dT%H:%M:%S")
                    else:
                        rec[h] = str(v)
                if rec:
                    data.append(rec)
            res[tn] = {"types": types, "rows": data}
    json.dump(res, open(out, "w"), indent=0)
    print({k: len(v["rows"]) for k, v in res.items()})


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
