# Live data: is the app really reading the Excel file? (easy steps)

Do **Part A** first (2 minutes). Do Part B only if Part A shows a red row.

## Part 0: the connector (answer to "which connector?")
The tables must come from the **Excel Online (Business)** connector:
Left rail **Data** (cylinder icon) → **+ Add data** → type **Excel Online (Business)** → **OneDrive for Business** →
pick `EDS-Lab-Data-PowerApps.xlsx` → tick **all 12** tables → **Connect**.

In the Data panel the names must be **exactly** these, all plain (this is what a fresh import always gives):
`tblParts, tblMoves, tblUsers, tblSettings, tblRequests, tblReqLines, tblPurch, tblProc, tblInvoice, tblNewPart, tblLicenses, tblCalib`.
Power Apps takes the name from the **table inside the workbook**, so renaming or moving the Excel file changes nothing.

**If names end in `_1`** (`tblParts_1`…): a table with that name was already connected, so Power Apps added a suffix and
the app can't find its tables (every list stays empty). Fix: Data panel → **⋯ → Remove** on *every* table until the panel
is empty → **File → Save** → close the Studio tab → reopen the app (Apps → ⋯ → Edit) → add all 12 tables **once**, from
**one** file only. Never rename (Power Apps can't), never add a table that is still in the list, never mix two workbooks.

Also check two settings (gear icon **Settings**):
1. **General → Data row limit = 2000.** The default 500 hides most Movements rows, so stock is wrong.
2. **Updates → Power Fx 1.0 → On**, if you see it. v2.0.3 turns it on by itself. It was **off** in v2.0.2, which is the
   most likely reason every list stayed empty.

## Part A: System Check (2 minutes)
1. Import **EDS-Lab-Portal-v2.0.5.msapp** (Welcome screen bottom right shows *Version 2.0.5*). Connect the tables as above.
2. Press **F5** (play) → **Log In** → top right **System Check**.
3. Every row must say **OK** (picture: `docs/preview/scrCheck.png`). Expected with the workbook I gave you:
   Parts list 418 rows · Stock movements 775 rows · Live stock 418 parts · Out / low stock 10 / 37.
4. Any row **NOT WORKING** or **ERROR**: take a screenshot of this page and send it to me. Each row is one link in
   the chain, so the first red row tells me exactly what to fix.

## Part B: build a 7-control test by hand (10 minutes, no code from me except these formulas)
This test reads the Excel tables **directly**, without any of my app formulas. If it works, the live link works.

**Picture of what to build:** `docs/preview/v2/live-data-test.png`

1. Tree view → **+ New screen** → **Blank**. Name it `scrTest`.
2. **Insert → Label** (control 1). In the formula bar choose property **Text** and paste:
```
"Parts: " & CountRows(tblParts)
```
   You should see **Parts: 418**.
3. **Insert → Label** (control 2) → Text:
```
"Movements: " & CountRows(tblMoves)
```
   You should see **Movements: 775**. If you see **500**, the Data row limit is still 500 (Part 0).
4. **Insert → Text input** (control 3). Rename it **txtPart** (double-click its name in the Tree view).
   Property **Default**: `"7213/0024"`
5. **Insert → Label** (control 4) → Text, formula **F4**:
```
"On hand: " & Sum(Filter(tblMoves, Upper(Trim(Text(PartNo))) = Upper(Trim(txtPart.Text))), Switch(Upper(Trim(Text(Type))), "RECEIPT", 1, "RETURN", 1, "ADJUST+", 1, "ISSUE", -1, "SCRAP", -1, "ADJUST-", -1, 0) * Abs(Value(Text(Qty))))
```
   You should see **On hand: 40**. Type another part number in control 3 and it changes instantly.
6. **Insert → Button** (control 5) → Text `"Refresh"` → OnSelect:
```
Refresh(tblParts); Refresh(tblMoves)
```
7. **Insert → Text input** (control 6). Rename it **txtBom**. Property **Mode**: `TextMode.MultiLine`. Default: `""`.
8. **Insert → Gallery → Blank vertical** (control 7) → Items, formula **F7**:
```
ForAll(Filter(Split(txtBom.Text, Char(10)), !IsBlank(Trim(Value))) As L, With({pn: Upper(Trim(First(Split(Trim(Substitute(Substitute(L.Value, Char(9), " "), Char(13), "")), " ")).Value))}, {Part: pn, OnHand: Sum(Filter(tblMoves, Upper(Trim(Text(PartNo))) = pn), Switch(Upper(Trim(Text(Type))), "RECEIPT", 1, "RETURN", 1, "ADJUST+", 1, "ISSUE", -1, "SCRAP", -1, "ADJUST-", -1, 0) * Abs(Value(Text(Qty))))}))
```
   Then click inside the gallery's first row → **Insert → Label** → Text:
```
ThisItem.Part & "   →   on hand " & ThisItem.OnHand
```
9. Press **F5**. Paste two columns from your BOM in Excel (part number, quantity) into control 6.
   Each line shows its on-hand quantity.

**Real-time proof:** in Excel (web), add a row to the **Movements** table: today's date, `7213/0024`, `RECEIPT`, `1`.
Back in the app press **Refresh** (control 5): control 4 changes from 40 to **41**. Delete the test row after.

### What the result means
| Part B result | Meaning | Next step |
|---|---|---|
| Works (418 / 775 / 40) | Excel link is fine; the problem is inside the app formulas | Send me the System Check screenshot (Part A). I fix it in the generator. |
| Formula shows a red underline | Hover over it and send me the message | Usually a table name with `_1`, or Power Fx 1.0 off |
| 0 rows / blank | The table is not connected or the file is empty | Redo Part 0 |

All the formulas above were run on your workbook with Microsoft's Power Fx engine before I sent them
(Parts 418, Movements 775, 7213/0024 = 40, and the BOM rows equal the app's own stock).
