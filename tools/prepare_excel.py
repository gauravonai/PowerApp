"""
Make the OneDrive / SharePoint copy of EDS-Lab-Data.xlsx that the Power Apps version uses.

    python3 tools/prepare_excel.py <path to the real EDS-Lab-Data.xlsx>

What it changes (nothing else is touched - every table, formula and row stays):
  1. Users: adds an Email column on the far right (optional sign-in match; blank is fine).
  2. Every table that is EMPTY today (Requests, RequestLines, Invoice, OngoingPurchase, Calibration)
     and Procurement (whose approval / PO / date columns are all blank) gets ONE typed row whose key
     starts with SAMPLE. Power Apps decides each Excel column's type (text / number / date) from the
     data it finds; a table with no data makes every column "text", and then saving a number or a
     date into it fails. The app ignores every row whose key starts with SAMPLE.
  3. NewPartRequest's existing sample row is re-keyed to SAMPLE-NPR-00001 and its date made a real date.
  4. A "POWER APPS" sheet explaining the above is added at the end.
"""
import datetime as dt
import shutil
import sys

import openpyxl
from openpyxl.worksheet.table import TableColumn

D = dt.datetime(2026, 1, 1, 12, 0)
DFMT = "yyyy-mm-dd"

SAMPLES = {
    "tblRequests": ["SAMPLE-REQ-00000", "SAMPLE", "COMPLETED", "sample@jcb.com", "SAMPLE row (keeps column types)", D,
                    "SAMPLE", "SAMPLE", "SAMPLE", "Proto", "SAMPLE", "SAMPLE", "SAMPLE", "SAMPLE", 1, D,
                    "SAMPLE row - Power Apps ignores rows whose key starts with SAMPLE. Do not delete.", "SAMPLE",
                    "2026-01-01T12:00:00", "SAMPLE", "[]"],
    "tblReqLines": ["SAMPLE-REQ-00000", 1, "SAMPLE", "SAMPLE row (keeps column types)", 1.5, 0.5, 0.5, "NO",
                    "COMPLETED", 0.5, "SAMPLE", "SAMPLE"],
    "tblInvoice": ["SAMPLE-INV", D, "SAMPLE", "SAMPLE", "SAMPLE", "SAMPLE", "SAMPLE", "SAMPLE", "SAMPLE", "SAMPLE",
                   "SAMPLE", "SAMPLE", "SAMPLE", "SAMPLE row (keeps column types)", 1, "SAMPLE", "SAMPLE", D, D, D,
                   0.5, 0.5, 200.5, 1.5, "SAMPLE", "SAMPLE", "SAMPLE", "SAMPLE"],
    "tblPurch": ["SAMPLE", "SAMPLE row (keeps column types)", 1.5, 0.5, "SAMPLE", "SAMPLE", "SAMPLE-PR", "SAMPLE",
                 "SAMPLE", "RECEIVED", D, D, "SAMPLE"],
    "tblCalib": ["SAMPLE", "SAMPLE row (keeps column types)", "SAMPLE", D, 12, D, "SAMPLE", "SAMPLE", "SAMPLE"],
    "tblProc": ["SAMPLE-PR", "SAMPLE", "SAMPLE row (keeps column types)", "MATERIAL", 1, D, "SAMPLE", "SAMPLE", D,
                "SAMPLE-PO", "SAMPLE", 0.5, "REJECTED", D, D, "SAMPLE", 0.5, "Opex", D, "SAMPLE", "SAMPLE"],
}


def table_of(wb, name):
    for ws in wb.worksheets:
        if name in ws.tables:
            return ws, ws.tables[name]
    raise KeyError(name)


def bounds(ref):
    a, b = ref.split(":")
    col = lambda s: "".join(ch for ch in s if ch.isalpha())
    row = lambda s: int("".join(ch for ch in s if ch.isdigit()))
    return col(a), row(a), col(b), row(b)


def set_row(ws, row, values):
    for j, v in enumerate(values, start=1):
        c = ws.cell(row=row, column=j, value=v)
        if isinstance(v, dt.datetime):
            c.number_format = DFMT


def main(src, dst):
    shutil.copyfile(src, dst)
    wb = openpyxl.load_workbook(dst)

    # 1. Users.Email
    ws, t = table_of(wb, "tblUsers")
    c1, r1, c2, r2 = bounds(t.ref)
    hdr = [c.value for c in ws[1]]
    if "Email" not in hdr:
        col = len([h for h in hdr if h]) + 1
        ws.cell(row=1, column=col, value="Email")
        letter = openpyxl.utils.get_column_letter(col)
        t.ref = "%s%d:%s%d" % (c1, r1, letter, r2)
        if t.autoFilter is not None:
            t.autoFilter.ref = t.ref
        t.tableColumns.append(TableColumn(id=col, name="Email"))
        ws.column_dimensions[letter].width = 32

    # 2. typed SAMPLE rows
    for tname, values in SAMPLES.items():
        ws, t = table_of(wb, tname)
        c1, r1, c2, r2 = bounds(t.ref)
        keys = [ws.cell(row=r, column=1).value for r in range(r1 + 1, r2 + 1)]
        if any(str(k or "").startswith("SAMPLE") for k in keys):
            continue
        blank_rows = [r for r in range(r1 + 1, r2 + 1)
                      if all(ws.cell(row=r, column=j).value in (None, "") for j in range(1, len(values) + 1))]
        if blank_rows:
            row = blank_rows[0]
        else:
            row = r2 + 1
            t.ref = "%s%d:%s%d" % (c1, r1, c2, row)
            if t.autoFilter is not None:
                t.autoFilter.ref = t.ref
        set_row(ws, row, values)

    # 3. NewPartRequest sample row
    ws, t = table_of(wb, "tblNewPart")
    for r in range(2, ws.max_row + 1):
        if str(ws.cell(row=r, column=7).value or "").upper().startswith("SAMPLE"):
            ws.cell(row=r, column=2, value="SAMPLE-NPR-00001")
            v = ws.cell(row=r, column=15).value
            if isinstance(v, str) and len(v) >= 10:
                y, m, d = (int(x) for x in v[:10].split("-"))
                ws.cell(row=r, column=15, value=dt.datetime(y, m, d, 12)).number_format = DFMT
    # make sure the DateRaised column is a date column even for new rows
    # 4. note sheet
    if "POWER APPS" not in wb.sheetnames:
        n = wb.create_sheet("POWER APPS")
        lines = [
            "THIS COPY IS FOR THE POWER APPS VERSION OF THE PORTAL",
            "",
            "Keep it on OneDrive for Business or a SharePoint document library. Power Apps reads and writes it through the",
            "Excel Online (Business) connector. It is a separate file from the one the HTA uses on the lab PC.",
            "",
            "Rows whose first column starts with SAMPLE are there on purpose: Power Apps works out whether a column holds",
            "text, numbers or dates from the data in it, and an empty table makes every column text. The app ignores",
            "every SAMPLE row. Leave them in.",
            "",
            "Users has an extra Email column on the right. Leave it blank if each person's Username is the part of their",
            "email address before the @ (gaurav.shelke for gaurav.shelke@jcb.com). Fill it only when that is not true.",
            "",
            "When Power Apps first connects it adds a hidden __PowerAppsId__ column to each table. That is normal.",
        ]
        for i, l in enumerate(lines, start=1):
            n.cell(row=i, column=2, value=l)
        n.column_dimensions["B"].width = 120
    wb.save(dst)
    print("wrote", dst)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "excel/EDS-Lab-Data-PowerApps.xlsx")
