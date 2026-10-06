"""Export every Excel table of the prepared workbook to JSON with a column type per column,
the way Power Apps' Excel connector would type them (number / text / datetime)."""
import datetime as dt
import json
import sys

import openpyxl


def excel_health(wb):
    """Stand-in for Excel's own calculation of the three Data Health formulas in Settings (LibreOffice cannot
    open files in this sandbox). Same rules as the formulas: ROWS(table) = data rows of the table range;
    SUMPRODUCT of +/-1 per Type (Excel '=' compares text ignoring case) times ABS(Qty)."""
    def tab(name):
        for ws in wb.worksheets:
            if name in ws.tables:
                return list(ws[ws.tables[name].ref])
    parts, moves = tab("tblParts"), tab("tblMoves")
    hdr = [c.value for c in moves[0]]
    ti, qi = hdr.index("Type"), hdr.index("Qty")
    sign = {"RECEIPT": 1, "RETURN": 1, "ADJUST+": 1, "ISSUE": -1, "SCRAP": -1, "ADJUST-": -1}
    tot = sum(sign.get(str(r[ti].value or "").upper(), 0) * abs(float(r[qi].value or 0)) for r in moves[1:])
    return {"=ROWS(tblParts)": len(parts) - 1, "=ROWS(tblMoves)": len(moves) - 1, "SUMPRODUCT": round(tot, 6)}


def main(xlsx, out):
    wb = openpyxl.load_workbook(xlsx)
    calc = excel_health(wb)
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
                    if isinstance(v, str) and v.startswith("=") and tn == "tblSettings":
                        v = str(calc["SUMPRODUCT"] if v.startswith("=SUMPRODUCT") else calc.get(v, v))
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
