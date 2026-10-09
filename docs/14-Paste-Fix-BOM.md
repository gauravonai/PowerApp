# Paste fix: BOM Compare says "New Part" for parts that exist

## What is wrong
BOM lines are read correctly (right part, right qty), but the match against stock fails. The usual cause is an
**invisible character in the Excel part-number cells**: a non-breaking space (from SAP / web copy), a tab or a
zero-width space. On screen `MC000RVT1CXX1SQ001` and `MC000RVT1CXX1SQ001 ` look identical; to Power Apps they differ.

## Step 0: start from a clean app (your current one was damaged)
The Google steps replaced the whole App.Formulas (about 90 named formulas deleted, 381 errors) and pointed it at
`tblSettings_1`, which does not exist (your Data panel has plain `tblSettings`). Do not repair that app.
1. Import `EDS-Lab-Portal-v2.0.8.msapp` (you already have it) as a **new** app.
2. Add data → Excel Online (Business) → your workbook → tick the 12 tables **once** → Connect.
   In a brand-new app the names are always plain (`tblParts`). `_1` only appears if a table is added twice.
3. Settings → General → Data row limit = **2000**.

## Step 1: prove the cause (30 seconds)
On **Check Stock**, add a label, set its **Text** to the formula below, type a part number that BOM says is
"New Part" into the search box:
```
With({k: Upper(Trim(qStk.Text))}, "Typed: [" & k & "] " & Len(k) & " chars  |  exact match: " & CountRows(Filter(tblParts, Upper(Text(PartNo)) = k)) & "  |  contains: " & CountRows(Filter(tblParts, k in Upper(Text(PartNo)))) & "  |  Excel cell: [" & LookUp(tblParts, k in Upper(Text(PartNo))).PartNo & "] " & Len(LookUp(tblParts, k in Upper(Text(PartNo))).PartNo) & " chars")
```
- `exact match: 0` and `contains: 1`, and the Excel cell has more chars than you typed → **invisible character**. Do step 2.
- `contains: 0` → the part really is not in the Parts sheet (or spelled differently).

## Step 2a: fastest fix, in Excel (no formula change)
In the Parts sheet (and Movements, RequestLines): select the PartNo column → **Ctrl+H** →
Find what: hold **Alt**, type **0160** on the number pad (non-breaking space) → Replace with: (empty) → Replace All.
Then in the app press the **Live · Synced** pill (refresh) and compare again.

## Step 2b: permanent fix, in the app (paste 4 formulas)
These ignore invisible characters for good. App → **Formulas**: find each definition below (it starts with
`nfParts =`, `nfMoves =`, `nfLines =`) and replace only that definition, up to and including its `;`.

### nfParts
```
nfParts = ForAll(
    Filter(tblParts, !IsBlank(PartNo) && Lower(Trim(Text(Active))) <> "no") As P,
    {PartNo: Trim(Substitute(Substitute(Substitute(Substitute(Substitute(Text(P.PartNo), Char(160), " "), Char(9), " "), Char(10), " "), Char(13), " "), UniChar(8203), "")), PN: Upper(Trim(Substitute(Substitute(Substitute(Substitute(Substitute(Text(P.PartNo), Char(160), " "), Char(9), " "), Char(10), " "), Char(13), " "), UniChar(8203), ""))), Description: Text(P.Description),
     Category: Text(P.Category), SubCategory: Text(P.SubCategory), UOM: Coalesce(Text(P.UOM), "NO"),
     Location: Text(P.Location), Supplier: Text(P.Supplier), UnitCost: Coalesce(IfError(Value(Text(P.UnitCost)), IfError(Value(First(Split(Trim(Text(P.UnitCost)), " ")).Value), 0)), 0),
     RefQty: Coalesce(IfError(Value(Text(P.ReorderRefQty)), IfError(Value(First(Split(Trim(Text(P.ReorderRefQty)), " ")).Value), 0)), 0)});
```

### nfMoves
```
nfMoves = ForAll(
    Filter(tblMoves, !IsBlank(PartNo)) As M,
    With({t: Upper(Trim(Text(M.Type))), q: Abs(Coalesce(IfError(Value(Text(M.Qty)), IfError(Value(First(Split(Trim(Text(M.Qty)), " ")).Value), 0)), 0))},
        {Date: If(IsBlank(M.Date), Blank(), IfError(With({t: Trim(Text(M.Date))}, If(!("-" in t) && !("/" in t) && !(":" in t) && !IsBlank(IfError(Value(t), Blank())) && Value(t) > 1000, DateAdd(Date(1899, 12, 30), RoundDown(Value(t), 0), TimeUnit.Days), DateValue(t))), Blank())), PartNo: Trim(Substitute(Substitute(Substitute(Substitute(Substitute(Text(M.PartNo), Char(160), " "), Char(9), " "), Char(10), " "), Char(13), " "), UniChar(8203), "")), PN: Upper(Trim(Substitute(Substitute(Substitute(Substitute(Substitute(Text(M.PartNo), Char(160), " "), Char(9), " "), Char(10), " "), Char(13), " "), UniChar(8203), ""))),
         Type: If(t = "ISSUE", "RELEASE", t), RawType: t, Qty: q,
         SQty: Switch(t, "RECEIPT", q, "RETURN", q, "ADJUST+", q, "ISSUE", -q, "SCRAP", -q, "ADJUST-", -q, 0),
         Reference: Text(M.Reference), UnitCost: Coalesce(IfError(Value(Text(M.UnitCost)), IfError(Value(First(Split(Trim(Text(M.UnitCost)), " ")).Value), 0)), 0), By: Text(M.By), Reason: Text(M.Reason),
         EntryId: Text(M.EntryId)}));
```

### nfLines
```
nfLines = ForAll(
    Filter(tblReqLines, !IsBlank(RequestNo) && !StartsWith(Text(RequestNo), "SAMPLE")) As L,
    {RequestNo: Text(L.RequestNo), Sr: Coalesce(IfError(Value(Text(L.Sr)), IfError(Value(First(Split(Trim(Text(L.Sr)), " ")).Value), 0)), 0), PartNo: Trim(Substitute(Substitute(Substitute(Substitute(Substitute(Text(L.PartNo), Char(160), " "), Char(9), " "), Char(10), " "), Char(13), " "), UniChar(8203), "")), PN: Upper(Trim(Substitute(Substitute(Substitute(Substitute(Substitute(Text(L.PartNo), Char(160), " "), Char(9), " "), Char(10), " "), Char(13), " "), UniChar(8203), ""))),
     Description: Text(L.Description), QtyRequested: Coalesce(IfError(Value(Text(L.QtyRequested)), IfError(Value(First(Split(Trim(Text(L.QtyRequested)), " ")).Value), 0)), 0), QtyReserved: Coalesce(IfError(Value(Text(L.QtyReserved)), IfError(Value(First(Split(Trim(Text(L.QtyReserved)), " ")).Value), 0)), 0),
     QtyReleased: Coalesce(IfError(Value(Text(L.QtyReleased)), IfError(Value(First(Split(Trim(Text(L.QtyReleased)), " ")).Value), 0)), 0), UOM: Text(L.UOM), LineStatus: Upper(Text(L.LineStatus)),
     UnitCost: Coalesce(IfError(Value(Text(L.UnitCost)), IfError(Value(First(Split(Trim(Text(L.UnitCost)), " ")).Value), 0)), 0), StoreLocation: Text(L.StoreLocation), Remarks: Text(L.Remarks)});
```

### BOM Compare → button "Compare Against Stock" (goBom) → OnSelect (replace all)
```
Refresh(tblParts); Refresh(tblMoves); Refresh(tblRequests); Refresh(tblReqLines); Refresh(tblSettings); Set(gLastSync, Now()); With({rows: With({raw: Filter(ForAll(ForAll(ForAll(Filter(ForAll(Split(Substitute(txtBom.Text, Char(13), ""), Char(10)) As L, {Tok: Filter(Split(TrimEnds(Substitute(Substitute(Substitute(Substitute(Substitute(Substitute(L.Value, UniChar(8203), ""), UniChar(65279), ""), Char(9), " "), Char(160), " "), ",", " "), ";", " ")), " "), !IsBlank(Value))}), CountRows(Tok) > 0) As R, {T: LastN(R.Tok, CountRows(R.Tok) - If(CountRows(R.Tok) >= 3 && Len(First(R.Tok).Value) <= 3 && !IsBlank(IfError(Value(First(R.Tok).Value), Blank())), 1, 0))}) As R, With({t1: Upper(First(R.T).Value), t2: If(CountRows(R.T) >= 2, Upper(Concat(FirstN(R.T, 2), Value, " ")), ""), t3: If(CountRows(R.T) >= 3, Upper(Concat(FirstN(R.T, 3), Value, " ")), "")}, With({k: If(!IsBlank(t3) && !IsBlank(LookUp(nfStock, PN = t3)), 3, !IsBlank(t2) && !IsBlank(LookUp(nfStock, PN = t2)), 2, 1)}, {PN: Switch(k, 3, t3, 2, t2, t1), Rest: LastN(R.T, CountRows(R.T) - k)}))) As R, With({nums: Filter(R.Rest, !IsBlank(IfError(Value(Value), Blank())))}, {PN: R.PN, Q: If(CountRows(nums) = 0, 0, Value(Last(nums).Value))})), !IsBlank(PN) && Q > 0)}, ForAll(Distinct(raw, PN) As D, {PN: D.Value, Q: Sum(Filter(raw, PN = D.Value), Q)}))}, ClearCollect(colBom, ForAll(Sequence(CountRows(rows)) As I, With({B: Index(rows, I.Value)}, With({p: LookUp(nfStock, PN = B.PN)}, {Sr: I.Value, PartNo: Coalesce(p.PartNo, B.PN), PN: B.PN, Qty: B.Q, Description: Coalesce(p.Description, "— not in the lab catalogue —"), UOM: Coalesce(p.UOM, ""), Location: Coalesce(p.Location, "—"), OnHand: Coalesce(p.OnHand, 0), Reserved: Coalesce(p.Reserved, 0), Avail: Coalesce(p.Avail, 0), UnitCost: Coalesce(p.UnitCost, 0), Short: If(IsBlank(p), B.Q, Max(0, Round(B.Q - p.Avail, 3))), Status: If(IsBlank(p), "NEW PART", B.Q <= p.Avail, "AVAILABLE", p.Avail <= 0, "OUT OF STOCK", "SHORTAGE"), Found: !IsBlank(p)}))))); Set(gBomRead, CountRows(Filter(ForAll(Split(Substitute(txtBom.Text, Char(13), ""), Char(10)) As L, {Tok: Filter(Split(TrimEnds(Substitute(Substitute(Substitute(Substitute(Substitute(Substitute(L.Value, UniChar(8203), ""), UniChar(65279), ""), Char(9), " "), Char(160), " "), ",", " "), ";", " ")), " "), !IsBlank(Value))}), CountRows(Tok) > 0))); Set(gBomInfo, gBomRead & " line(s) read · " & CountRows(colBom) & " part(s) compared · " & CountRows(Filter(colBom, Found)) & " found in stock list · " & CountRows(Filter(colBom, !Found)) & " new part(s)" & If(gBomRead > CountRows(colBom), " · " & (gBomRead - CountRows(colBom)) & " line(s) skipped (no quantity, or same part twice)", "")); If(CountRows(colBom) = 0, Notify("No line had a part number and a quantity. Paste the part number first and the quantity last on each line.", NotificationType.Warning), Notify("Compared " & CountRows(colBom) & " part(s) with live stock as of " & Text(gLastSync, "hh:mm:ss") & ".", NotificationType.Success))
```

Tested on the real workbook with a non-breaking space, a tab and a zero-width space injected into Parts cells:
the parts are found, on hand is correct, the request is raised and reaches the Lab Admin (Phase 1 run, 16/16).
