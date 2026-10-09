# Prompt for Google AI (Gemini): diagnose empty Check Stock / BOM Compare

Copy everything below the line.

---

You are a senior Microsoft Power Apps (canvas app, Power Fx) engineer. Help me find and fix why two screens show
no data. Ask me for screenshots or values when you need them, one step at a time, and give me exact formulas to paste.
Keep answers short and practical.

## The app
- Canvas app "EDS Lab Material Portal" (imported from an .msapp built from pa.yaml source). Data = Excel Online
  (Business) workbook in OneDrive with 12 tables. App setting "Power Fx 1.0" is ON. Data row limit should be 2000.
- In MY app the tables appear in the Data panel as: tblCalib, tblSettings (plain) and tblInvoice_1, tblLicenses_1,
  tblMoves_1, tblNewPart_1, tblParts_1, tblProc_1, tblPurch_1, tblReqLines_1, tblRequests_1, tblUsers_1.
  The app's formulas were written for the PLAIN names (tblParts, tblMoves, tblRequests, tblReqLines, ...).
  I believe the Excel connection itself works (a hand-made test label reading tblParts_1 showed rows).
- Stock is never typed: it is calculated. App.Formulas (named formulas) build it in this chain:
  tblParts -> nfParts; tblMoves -> nfMoves -> nfOnHand; tblRequests -> nfReq; tblReqLines -> nfLines -> nfHeld -> nfResv;
  tblSettings -> nfSet -> nLowConn/nLowTerm/nLowDef;  nfParts + nfOnHand + nfResv + nLow* -> nfStock.
- Screens that use it: "Check Stock" (gallery Items = Filter(nfStock, ...)) and "BOM Compare" (button goBom reads the
  pasted text in txtBom, parses part number + qty per line into collection colBom, looks each part up in nfStock).

## The problem
Check Stock shows no parts and BOM Compare does not find parts / shows nothing, for the Engineer role.
The Compare button shows a yellow warning triangle in Studio.

## What I need from you
1. Tell me how to find the exact error: App checker (Studio, stethoscope icon) -> Formulas, and the red underline
   message in App -> Formulas. I will send you what it says.
2. Diagnose with these test formulas (I paste each into a label's Text, one at a time; the first that is red, ERR or 0
   is the break):
   "Parts sheet: " & IfError(Text(CountRows(tblParts_1)), "ERR: " & FirstError.Message)
   "Moves sheet: " & IfError(Text(CountRows(tblMoves_1)), "ERR: " & FirstError.Message)
   "Req sheets: " & IfError(CountRows(tblRequests_1) & " / " & CountRows(tblReqLines_1), "ERR: " & FirstError.Message)
   "nfParts: " & IfError(Text(CountRows(nfParts)), "ERR: " & FirstError.Message)
   "nfMoves: " & IfError(Text(CountRows(nfMoves)), "ERR: " & FirstError.Message)
   "nfOnHand: " & IfError(Text(CountRows(nfOnHand)), "ERR: " & FirstError.Message)
   "nfReq/nfLines: " & IfError(CountRows(nfReq) & " / " & CountRows(nfLines), "ERR: " & FirstError.Message)
   "nfResv: " & IfError(Text(CountRows(nfResv)), "ERR: " & FirstError.Message)
   "nfStock: " & IfError(CountRows(nfStock) & " parts, " & CountRows(Filter(nfStock, OnHand > 0)) & " in stock", "ERR: " & FirstError.Message)
3. Likely causes to check, in this order:
   a) Name mismatch: named formulas say tblParts but the app only has tblParts_1 (Studio adds _1 when a table with that
      name was already connected). Fix A: remove the _1 data sources, save, reopen, add the 10 tables once so they get
      plain names. Fix B (if I must keep _1): edit App -> Formulas and replace each table name with its _1 name
      (tblParts -> tblParts_1, tblMoves -> tblMoves_1, tblRequests -> tblRequests_1, tblReqLines -> tblReqLines_1,
      tblUsers -> tblUsers_1, tblPurch -> tblPurch_1, tblProc -> tblProc_1, tblInvoice -> tblInvoice_1,
      tblNewPart -> tblNewPart_1, tblLicenses -> tblLicenses_1) and the same in screen formulas (Studio search pane
      can find them). Careful not to create tblParts_1_1.
   b) A column the formulas use is missing or renamed in my workbook (any missing column breaks the whole named formula
      and everything after it in the chain, e.g. nfReq breaks nfResv which breaks nfStock).
   c) Data row limit below the number of rows (Settings -> General -> Data row limit = 2000).
   d) Power Fx 1.0 switched off (Settings -> Updates).
4. Give me the corrected formula to paste for whatever is broken. Keep the same output columns because other screens use them.

## Columns the formulas expect in each Excel table
- tblCalib: AssetNo, AssetName, Location, LastCalDate, IntervalMonths, DueDate, Owner, Status, Notes
- tblInvoice: InvoiceNo, InvoiceDate, ToName, CCName, FromName, FromExt, FromMobile, HarnessPartNos, JobDescription, BusinessUnit, BUContact, CostCentre, ApplicationDesc, DetailsOfRequest, NoOfCircuits, DCContact, DCMobile, JobReceived, StartDate, CompletionDate, MaterialCost, AssemblyCost, TransportCost, TotalCost, RefRequest, ImagePath, Status, Notes
- tblLicenses: SoftwareName, Vendor, LicenseType, SeatsTotal, SeatsInUse, ExpiryDate, AnnualCost, Status, Notes
- tblMoves: Date, PartNo, Type, Qty, Reference, UnitCost, By, Reason, EntryId
- tblNewPart: SrNo, RequestNo, RequesterName, Category, SubCategory, PlantCode, PartName, MakeBrand, ModelNo, OtherSpecs, Remarks, UOM, HSNCode, Status, DateRaised
- tblParts: PartNo, Description, Category, SubCategory, UOM, Location, Supplier, UnitCost, ReorderRefQty, Active, Notes
- tblProc: PRNumber, Department, Summary, ServiceType, Qty, DateRaised, RaisedBy, ApprovedBy, ApprovedDate, PONumber, Vendor, POAmount, Stage, PODate, DeliveredDate, Notes, PRAmount, InvestmentType, POApprovedDate, Ownership, POCopyPath
- tblPurch: PartNo, Description, QtyRequired, QtyConfirmed, RequestNo, RaisedBy, PRNumber, SupplierNo, SupplierName, Stage, DateRaised, ExpectedDate, Notes
- tblReqLines: RequestNo, Sr, PartNo, Description, QtyRequested, QtyReserved, QtyReleased, UOM, LineStatus, UnitCost, StoreLocation, Remarks
- tblRequests: RequestNo, Kind, Status, RaisedByEmail, RaisedByName, DateRaised, Machine, ProjectCode, HarnessPartNo, BuildStage, BusinessUnit, CostCentre, BUContact, DCContact, NoOfCircuits, RequiredBy, ScopeOfWork, ParentRequest, LastUpdated, LastUpdatedBy, History
- tblSettings: Key, Value, Notes
- tblUsers: Username, FullName, Role, BusinessUnit, Password, PasswordSetOn, Email

## The named formulas of the stock chain (App -> Formulas), exactly as in the app
```
nfSet = ForAll(Filter(tblSettings, !IsBlank(Key)) As S, {Key: Trim(Text(S.Key)), Val: Text(S.Value)});

nLowConn = Coalesce(Value(LookUp(nfSet, Key = "LowStockPct_Connector").Val), 25);

nLowTerm = Coalesce(Value(LookUp(nfSet, Key = "LowStockPct_Terminal").Val), 20);

nLowDef = Coalesce(Value(LookUp(nfSet, Key = "LowStockPct_Default").Val), 20);

nfParts = ForAll(
    Filter(tblParts, !IsBlank(PartNo) && Lower(Trim(Text(Active))) <> "no") As P,
    {PartNo: Trim(Text(P.PartNo)), PN: Upper(Trim(Text(P.PartNo))), Description: Text(P.Description),
     Category: Text(P.Category), SubCategory: Text(P.SubCategory), UOM: Coalesce(Text(P.UOM), "NO"),
     Location: Text(P.Location), Supplier: Text(P.Supplier), UnitCost: Coalesce(IfError(Value(Text(P.UnitCost)), IfError(Value(First(Split(Trim(Text(P.UnitCost)), " ")).Value), 0)), 0),
     RefQty: Coalesce(IfError(Value(Text(P.ReorderRefQty)), IfError(Value(First(Split(Trim(Text(P.ReorderRefQty)), " ")).Value), 0)), 0)});

nfMoves = ForAll(
    Filter(tblMoves, !IsBlank(PartNo)) As M,
    With({t: Upper(Trim(Text(M.Type))), q: Abs(Coalesce(IfError(Value(Text(M.Qty)), IfError(Value(First(Split(Trim(Text(M.Qty)), " ")).Value), 0)), 0))},
        {Date: If(IsBlank(M.Date), Blank(), IfError(With({t: Trim(Text(M.Date))}, If(!("-" in t) && !("/" in t) && !(":" in t) && !IsBlank(IfError(Value(t), Blank())) && Value(t) > 1000, DateAdd(Date(1899, 12, 30), RoundDown(Value(t), 0), TimeUnit.Days), DateValue(t))), Blank())), PartNo: Trim(Text(M.PartNo)), PN: Upper(Trim(Text(M.PartNo))),
         Type: If(t = "ISSUE", "RELEASE", t), RawType: t, Qty: q,
         SQty: Switch(t, "RECEIPT", q, "RETURN", q, "ADJUST+", q, "ISSUE", -q, "SCRAP", -q, "ADJUST-", -q, 0),
         Reference: Text(M.Reference), UnitCost: Coalesce(IfError(Value(Text(M.UnitCost)), IfError(Value(First(Split(Trim(Text(M.UnitCost)), " ")).Value), 0)), 0), By: Text(M.By), Reason: Text(M.Reason),
         EntryId: Text(M.EntryId)}));

nfOnHand = ForAll(Distinct(nfMoves, PN) As G,
    {PN: G.Value, OnHand: Round(Sum(Filter(nfMoves, PN = G.Value), SQty), 3)});

nfReq = ForAll(
    Filter(tblRequests, !IsBlank(RequestNo) && !StartsWith(Text(RequestNo), "SAMPLE")) As R,
    {RequestNo: Text(R.RequestNo), Kind: Upper(Text(R.Kind)), Status: Upper(Coalesce(Text(R.Status), "SUBMITTED")),
     RaisedByEmail: Lower(Text(R.RaisedByEmail)), RaisedByName: Text(R.RaisedByName), DateRaised: If(IsBlank(R.DateRaised), Blank(), IfError(With({t: Trim(Text(R.DateRaised))}, If(!("-" in t) && !("/" in t) && !(":" in t) && !IsBlank(IfError(Value(t), Blank())) && Value(t) > 1000, DateAdd(Date(1899, 12, 30), RoundDown(Value(t), 0), TimeUnit.Days), DateValue(t))), Blank())),
     Machine: Text(R.Machine), ProjectCode: Text(R.ProjectCode), HarnessPartNo: Text(R.HarnessPartNo),
     BuildStage: Text(R.BuildStage), BusinessUnit: Text(R.BusinessUnit), CostCentre: Text(R.CostCentre),
     BUContact: Text(R.BUContact), DCContact: Text(R.DCContact), NoOfCircuits: Coalesce(IfError(Value(Text(R.NoOfCircuits)), IfError(Value(First(Split(Trim(Text(R.NoOfCircuits)), " ")).Value), 0)), 0),
     RequiredBy: If(IsBlank(R.RequiredBy), Blank(), IfError(With({t: Trim(Text(R.RequiredBy))}, If(!("-" in t) && !("/" in t) && !(":" in t) && !IsBlank(IfError(Value(t), Blank())) && Value(t) > 1000, DateAdd(Date(1899, 12, 30), RoundDown(Value(t), 0), TimeUnit.Days), DateValue(t))), Blank())), ScopeOfWork: Text(R.ScopeOfWork), ParentRequest: Text(R.ParentRequest),
     LastUpdated: Text(R.LastUpdated), LastUpdatedBy: Text(R.LastUpdatedBy), History: Text(R.History)});

nfLines = ForAll(
    Filter(tblReqLines, !IsBlank(RequestNo) && !StartsWith(Text(RequestNo), "SAMPLE")) As L,
    {RequestNo: Text(L.RequestNo), Sr: Coalesce(IfError(Value(Text(L.Sr)), IfError(Value(First(Split(Trim(Text(L.Sr)), " ")).Value), 0)), 0), PartNo: Trim(Text(L.PartNo)), PN: Upper(Trim(Text(L.PartNo))),
     Description: Text(L.Description), QtyRequested: Coalesce(IfError(Value(Text(L.QtyRequested)), IfError(Value(First(Split(Trim(Text(L.QtyRequested)), " ")).Value), 0)), 0), QtyReserved: Coalesce(IfError(Value(Text(L.QtyReserved)), IfError(Value(First(Split(Trim(Text(L.QtyReserved)), " ")).Value), 0)), 0),
     QtyReleased: Coalesce(IfError(Value(Text(L.QtyReleased)), IfError(Value(First(Split(Trim(Text(L.QtyReleased)), " ")).Value), 0)), 0), UOM: Text(L.UOM), LineStatus: Upper(Text(L.LineStatus)),
     UnitCost: Coalesce(IfError(Value(Text(L.UnitCost)), IfError(Value(First(Split(Trim(Text(L.UnitCost)), " ")).Value), 0)), 0), StoreLocation: Text(L.StoreLocation), Remarks: Text(L.Remarks)});

nfDeadStatus = ["COMPLETED", "CANCELLED", "REJECTED"];

nfHoldStatus = ["RESERVED", "READY FOR RELEASE", "PARTIALLY RELEASED", "PURCHASE REQUIRED"];

nfHeld = Filter(nfLines As HL, HL.QtyReserved - HL.QtyReleased > 0 &&
    LookUp(nfReq As RQ, RQ.RequestNo = HL.RequestNo).Status in nfHoldStatus);

nfResv = ForAll(Distinct(nfHeld, PN) As G, {PN: G.Value, Res: Sum(Filter(nfHeld, PN = G.Value), QtyReserved - QtyReleased)});

nfStock = ForAll(nfParts As P,
    With({on: Coalesce(LookUp(nfOnHand, PN = P.PN).OnHand, 0),
          rv: Coalesce(LookUp(nfResv, PN = P.PN).Res, 0),
          pct: Switch(P.SubCategory, "Connector", nLowConn, "Terminal", nLowTerm, nLowDef)},
        {PartNo: P.PartNo, PN: P.PN, Description: P.Description, Category: P.Category, SubCategory: P.SubCategory,
         UOM: P.UOM, Location: P.Location, Supplier: P.Supplier, UnitCost: P.UnitCost, RefQty: P.RefQty,
         OnHand: on, Reserved: rv, Avail: Round(on - rv, 3), StockValue: on * P.UnitCost,
         Status: If(on <= 0, "OUT OF STOCK",
                    P.RefQty > 0 && on <= P.RefQty * pct / 100, "LOW STOCK",
                    on - rv <= 0, "FULLY RESERVED",
                    "IN STOCK"),
         Quality: Trim(If(IsBlank(P.Location), "LOCATION MISSING ") & If(P.UnitCost = 0, "COST MISSING ") &
                       If(IsBlank(P.Category), "CATEGORY MISSING"))}));
```

## Compare Against Stock button (goBom.OnSelect)
```
Refresh(tblParts); Refresh(tblMoves); Refresh(tblRequests); Refresh(tblReqLines); Refresh(tblSettings); Set(gLastSync, Now()); With({rows: With({raw: Filter(ForAll(ForAll(ForAll(Filter(ForAll(Split(Substitute(txtBom.Text, Char(13), ""), Char(10)) As L, {Tok: Filter(Split(TrimEnds(Substitute(Substitute(Substitute(Substitute(L.Value, Char(9), " "), Char(160), " "), ",", " "), ";", " ")), " "), !IsBlank(Value))}), CountRows(Tok) > 0) As R, {T: LastN(R.Tok, CountRows(R.Tok) - If(CountRows(R.Tok) >= 3 && Len(First(R.Tok).Value) <= 3 && !IsBlank(IfError(Value(First(R.Tok).Value), Blank())), 1, 0))}) As R, With({t1: Upper(First(R.T).Value), t2: If(CountRows(R.T) >= 2, Upper(Concat(FirstN(R.T, 2), Value, " ")), ""), t3: If(CountRows(R.T) >= 3, Upper(Concat(FirstN(R.T, 3), Value, " ")), "")}, With({k: If(!IsBlank(t3) && !IsBlank(LookUp(nfStock, PN = t3)), 3, !IsBlank(t2) && !IsBlank(LookUp(nfStock, PN = t2)), 2, 1)}, {PN: Switch(k, 3, t3, 2, t2, t1), Rest: LastN(R.T, CountRows(R.T) - k)}))) As R, With({nums: Filter(R.Rest, !IsBlank(IfError(Value(Value), Blank())))}, {PN: R.PN, Q: If(CountRows(nums) = 0, 0, Value(Last(nums).Value))})), !IsBlank(PN) && Q > 0)}, ForAll(Distinct(raw, PN) As D, {PN: D.Value, Q: Sum(Filter(raw, PN = D.Value), Q)}))}, ClearCollect(colBom, ForAll(Sequence(CountRows(rows)) As I, With({B: Index(rows, I.Value)}, With({p: LookUp(nfStock, PN = B.PN)}, {Sr: I.Value, PartNo: Coalesce(p.PartNo, B.PN), PN: B.PN, Qty: B.Q, Description: Coalesce(p.Description, "— not in the lab catalogue —"), UOM: Coalesce(p.UOM, ""), Location: Coalesce(p.Location, "—"), OnHand: Coalesce(p.OnHand, 0), Reserved: Coalesce(p.Reserved, 0), Avail: Coalesce(p.Avail, 0), UnitCost: Coalesce(p.UnitCost, 0), Short: If(IsBlank(p), B.Q, Max(0, Round(B.Q - p.Avail, 3))), Status: If(IsBlank(p), "NEW PART", B.Q <= p.Avail, "AVAILABLE", p.Avail <= 0, "OUT OF STOCK", "SHORTAGE"), Found: !IsBlank(p)}))))); Set(gBomRead, CountRows(Filter(ForAll(Split(Substitute(txtBom.Text, Char(13), ""), Char(10)) As L, {Tok: Filter(Split(TrimEnds(Substitute(Substitute(Substitute(Substitute(L.Value, Char(9), " "), Char(160), " "), ",", " "), ";", " ")), " "), !IsBlank(Value))}), CountRows(Tok) > 0))); Set(gBomInfo, gBomRead & " line(s) read · " & CountRows(colBom) & " part(s) compared · " & CountRows(Filter(colBom, Found)) & " found in stock list · " & CountRows(Filter(colBom, !Found)) & " new part(s)" & If(gBomRead > CountRows(colBom), " · " & (gBomRead - CountRows(colBom)) & " line(s) skipped (no quantity, or same part twice)", "")); If(CountRows(colBom) = 0, Notify("No line had a part number and a quantity. Paste the part number first and the quantity last on each line.", NotificationType.Warning), Notify("Compared " & CountRows(colBom) & " part(s) with live stock as of " & Text(gLastSync, "hh:mm:ss") & ".", NotificationType.Success))
```
