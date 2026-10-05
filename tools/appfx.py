"""
App-level Power Fx: App.Formulas (named formulas), App.OnStart and App.StartScreen.

Named formulas are recalculated automatically whenever an Excel table changes
(after a Patch/Collect/Refresh), so stock on hand, reservations and the request
views are never stored anywhere - exactly like the HTA, stock is ALWAYS the sum
of the Movements rows.
"""

NAV = {
    "Engineer": [("OVERVIEW", [("dash", "Dashboard")]),
                 ("MATERIAL", [("stock", "Check Stock"), ("bom", "BOM Compare"), ("newreq", "NEW REQUEST"),
                               ("myreq", "My Requests"), ("newpart", "Brand New Purchase Part")])],
    "Lab Admin": [("OVERVIEW", [("dash", "Dashboard")]),
                  ("REQUESTS", [("queue", "Request Queue"), ("newpartq", "New Purchase Parts")]),
                  ("INVENTORY", [("inventory", "Component Inventory"), ("inward", "Material Inward"),
                                 ("ledger", "Stock Transactions"), ("demand", "High Demand Parts")]),
                  ("DELIVERIES", [("invoice", "Create Invoice"), ("invlist", "Invoices"), ("cost", "Cost Sheet")]),
                  ("PURCHASING", [("proc", "Procurement (PR/PO)"), ("purch", "Ongoing Purchase"),
                                  ("lic", "Software Licenses")]),
                  ("TOOLS", [("stock", "Check Stock"), ("bom", "BOM Compare"), ("team", "Team access")])],
    "Manager": [("OVERVIEW", [("dash", "Dashboard")]),
                ("REPORTS", [("queue", "All Requests"), ("invlist", "Invoices"), ("proc", "Procurement (PR/PO)"),
                             ("purch", "Ongoing Purchase"), ("demand", "High Demand Parts"),
                             ("lic", "Software Licenses"), ("inventory", "Inventory")])],
}

# key -> screen.  'dash' is role dependent.
SCREEN_OF = {"stock": "scrStock", "bom": "scrBom", "newreq": "scrNewReq", "myreq": "scrMyReq",
             "newpart": "scrNewPart", "queue": "scrQueue", "newpartq": "scrNewPartQ",
             "inventory": "scrInventory", "inward": "scrInward", "ledger": "scrLedger", "demand": "scrDemand",
             "invoice": "scrInvoice", "invlist": "scrInvList", "cost": "scrCost", "proc": "scrProc",
             "purch": "scrPurch", "lic": "scrLic", "team": "scrTeam"}

PILL = [("IN STOCK", "cOk"), ("LOW STOCK", "cWarn"), ("OUT OF STOCK", "cStop"), ("FULLY RESERVED", "cSteel"),
        ("AVAILABLE", "cOk"), ("SHORTAGE", "cStop"), ("NEW PART", "cSteel"), ("PARTIAL", "cWarn"),
        ("DRAFT", "cInk3"), ("SUBMITTED", "cSteel"), ("ADMIN REVIEW", "cWarn"), ("RESERVED", "cJcb"),
        ("READY FOR RELEASE", "cOk"), ("PARTIALLY RELEASED", "cWarn"), ("RELEASED", "cOk"),
        ("COMPLETED", "cInk3"), ("CANCELLED", "cStop"), ("REJECTED", "cStop"), ("PURCHASE REQUIRED", "cStop"),
        ("PR RAISED", "cSteel"), ("APPROVED", "cJcb"), ("PO RAISED", "cJcb"), ("GRN IN PROGRESS", "cWarn"),
        ("DELIVERED (CLOSED)", "cOk"), ("EXPIRED", "cStop"), ("EXPIRING SOON", "cWarn"), ("ACTIVE", "cOk"),
        ("RECEIPT", "cOk"), ("RELEASE", "cStop"), ("RETURN", "cOk"), ("ADJUST+", "cSteel"), ("ADJUST-", "cWarn"),
        ("SCRAP", "cStop"), ("REQUIRED", "cStop"), ("IN TRANSIT", "cSteel"), ("RECEIVED", "cOk"),
        ("ISSUED", "cOk"), ("SHORTFALL", "cSteel"), ("OK", "cOk"), ("ISSUES", "cWarn"),
        ("LAB LEAD", "cJcb"), ("LAB ADMIN", "cJcb"), ("MANAGER", "cSteel"), ("ENGINEER", "cInk2")]


def nav_table():
    rows = []
    for role, groups in NAV.items():
        seq = 0
        for grp, items in groups:
            seq += 1
            rows.append('{Role:"%s", Seq:%d, Hdr:true, Key:"", Label:"%s"}' % (role, seq, grp))
            for key, label in items:
                seq += 1
                rows.append('{Role:"%s", Seq:%d, Hdr:false, Key:"%s", Label:"%s"}' % (role, seq, key, label))
    return "Table(\n    " + ",\n    ".join(rows) + ")"


def nav_switch():
    parts = ['"dash", Navigate(If(gRole = "Manager", scrMgrDash, scrDash), ScreenTransition.None)']
    for k, s in SCREEN_OF.items():
        parts.append('"%s", Navigate(%s, ScreenTransition.None)' % (k, s))
    return "Switch(ThisItem.Key,\n  " + ",\n  ".join(parts) + ")"


def D(x):
    """Read any Excel date cell (Date, DateTime, ISO text or local text) as a Date."""
    return "If(IsBlank(%s), Blank(), DateValue(Text(%s)))" % (x, x)


def N(x):
    """Read any Excel number cell (number or text) as a number, blank -> 0."""
    return "Coalesce(Value(Text(%s)), 0)" % x


def T(x):
    return "Text(%s)" % x


FORMULAS = r"""
// =====================================================================
//  JCB EDS LAB MATERIAL PORTAL  -  App.Formulas  (named formulas)
//  Same rules as the HTA v8. Stock is NEVER typed: it is the sum of
//  the Movements rows, recalculated here every time Excel changes.
// =====================================================================

// ---------- theme: the HTA palette, one accent (JCB yellow) ----------
cBg = RGBA(21, 22, 26, 1);
cPanel = RGBA(29, 31, 36, 1);
cPanel2 = RGBA(36, 39, 45, 1);
cSunk = RGBA(17, 18, 22, 1);
cLine = RGBA(49, 53, 60, 1);
cLine2 = RGBA(61, 66, 74, 1);
cInk = RGBA(234, 232, 227, 1);
cInk2 = RGBA(163, 168, 176, 1);
cInk3 = RGBA(113, 118, 126, 1);
cJcb = RGBA(242, 176, 30, 1);
cJcbDark = RGBA(200, 143, 16, 1);
cJcbWash = RGBA(46, 38, 20, 1);
cOnJcb = RGBA(21, 22, 26, 1);
cSteel = RGBA(108, 156, 198, 1);
cOk = RGBA(79, 174, 125, 1);
cWarn = RGBA(217, 155, 60, 1);
cStop = RGBA(220, 115, 97, 1);
fMono = "Consolas, 'Courier New', monospace";
fUI = "'Segoe UI', 'Open Sans', sans-serif";
nfChartHex = ["#f2b01e", "#6c9cc6", "#4fae7d", "#dc7361", "#a3a8b0", "#c88f10", "#d99b3c", "#8a7fc0"];
nfPill = %(PILL)s;

// ---------- navigation (same groups and labels as the HTA) ----------
nfNav = %(NAV)s;

// ---------- who is signed in (Microsoft 365 login, no passwords) ----------
nfEmail = Lower(Trim(User().Email));
nfUserKey = First(Split(nfEmail, "@")).Value;
nfMeRow = With(
    {byMail: LookUp(tblUsers, !IsBlank(Email) && Lower(Trim(Text(Email))) = nfEmail)},
    If(IsBlank(byMail),
        LookUp(tblUsers, Lower(Trim(Text(Username))) = nfUserKey || Lower(Trim(Text(Username))) = nfEmail),
        byMail));
nfMeName = Coalesce(Text(nfMeRow.FullName), User().FullName, nfEmail);
nfMeInitials = Upper(Concat(FirstN(Split(Trim(nfMeName), " "), 2), Left(Value, 1)));
// Role text is tolerated the same way the HTA tolerates it; anything unknown = Engineer.
nfRoleCanon = With(
    {k: Lower(Substitute(Substitute(Substitute(Substitute(Text(nfMeRow.Role), " ", ""), "-", ""), "_", ""), ".", ""))},
    If(IsBlank(k), "Engineer",
        k in ["lablead", "lead", "labhead", "teamlead"], "Lab Lead",
        "admin" in k || k in ["store", "storekeeper", "stores"] || "incharge" in k, "Lab Admin",
        "manager" in k || k in ["mgr", "hod", "head"], "Manager",
        "Engineer"));

// ---------- settings tab ----------
nfSet = ForAll(Filter(tblSettings, !IsBlank(Key)) As S, {Key: Trim(Text(S.Key)), Val: Text(S.Value)});
nLowConn = Coalesce(Value(LookUp(nfSet, Key = "LowStockPct_Connector").Val), 25);
nLowTerm = Coalesce(Value(LookUp(nfSet, Key = "LowStockPct_Terminal").Val), 20);
nLowDef = Coalesce(Value(LookUp(nfSet, Key = "LowStockPct_Default").Val), 20);
tLabName = Coalesce(LookUp(nfSet, Key = "LabName").Val, "EDS Lab");
tSupport = Coalesce(LookUp(nfSet, Key = "SupportContact").Val, "your Lab Admin");

// ---------- Finance-locked cost constants (Assumptions sheet) ----------
kMachineCost = 418000;
kDepPA = 41800;
kProtoHrs = 12;
kHrsDay = 15;
kDaysMonth = 20;
kMonthsPA = 12;
kStdHrsPA = 3600;
kTechs = 1;
kRateHr = 1239;
kKwhHr = 10;
kRateKwh = 9;
kKwhPA = 36000;
kElecPA = 324000;
kAmcHr = 50;
kTransport = 200;
kCktPerHr = 7.5;

// ---------- Parts (retired parts, Active = No, are hidden like the HTA) ----------
nfParts = ForAll(
    Filter(tblParts, !IsBlank(PartNo) && Lower(Trim(Text(Active))) <> "no") As P,
    {PartNo: Trim(Text(P.PartNo)), PN: Upper(Trim(Text(P.PartNo))), Description: Text(P.Description),
     Category: Text(P.Category), SubCategory: Text(P.SubCategory), UOM: Coalesce(Text(P.UOM), "NO"),
     Location: Text(P.Location), Supplier: Text(P.Supplier), UnitCost: %(N_P_UnitCost)s,
     RefQty: %(N_P_Ref)s});

// ---------- Movements, signed by type exactly like the LiveStock SUMIFS ----------
nfMoves = ForAll(
    Filter(tblMoves, !IsBlank(PartNo)) As M,
    With({t: Upper(Trim(Text(M.Type))), q: Abs(%(N_M_Qty)s)},
        {Date: %(D_M_Date)s, PartNo: Trim(Text(M.PartNo)), PN: Upper(Trim(Text(M.PartNo))),
         Type: If(t = "ISSUE", "RELEASE", t), RawType: t, Qty: q,
         SQty: Switch(t, "RECEIPT", q, "RETURN", q, "ADJUST+", q, "ISSUE", -q, "SCRAP", -q, "ADJUST-", -q, 0),
         Reference: Text(M.Reference), UnitCost: %(N_M_Cost)s, By: Text(M.By), Reason: Text(M.Reason),
         EntryId: Text(M.EntryId)}));
nfOnHand = ForAll(Distinct(nfMoves, PN) As G,
    {PN: G.Value, OnHand: Round(Sum(Filter(nfMoves, PN = G.Value), SQty), 3)});

// ---------- Requests + lines ----------
nfReq = ForAll(
    Filter(tblRequests, !IsBlank(RequestNo) && !StartsWith(Text(RequestNo), "SAMPLE")) As R,
    {RequestNo: Text(R.RequestNo), Kind: Upper(Text(R.Kind)), Status: Upper(Coalesce(Text(R.Status), "SUBMITTED")),
     RaisedByEmail: Lower(Text(R.RaisedByEmail)), RaisedByName: Text(R.RaisedByName), DateRaised: %(D_R_Raised)s,
     Machine: Text(R.Machine), ProjectCode: Text(R.ProjectCode), HarnessPartNo: Text(R.HarnessPartNo),
     BuildStage: Text(R.BuildStage), BusinessUnit: Text(R.BusinessUnit), CostCentre: Text(R.CostCentre),
     BUContact: Text(R.BUContact), DCContact: Text(R.DCContact), NoOfCircuits: %(N_R_Circ)s,
     RequiredBy: %(D_R_Need)s, ScopeOfWork: Text(R.ScopeOfWork), ParentRequest: Text(R.ParentRequest),
     LastUpdated: Text(R.LastUpdated), LastUpdatedBy: Text(R.LastUpdatedBy), History: Text(R.History)});
nfLines = ForAll(
    Filter(tblReqLines, !IsBlank(RequestNo) && !StartsWith(Text(RequestNo), "SAMPLE")) As L,
    {RequestNo: Text(L.RequestNo), Sr: %(N_L_Sr)s, PartNo: Trim(Text(L.PartNo)), PN: Upper(Trim(Text(L.PartNo))),
     Description: Text(L.Description), QtyRequested: %(N_L_Q)s, QtyReserved: %(N_L_Res)s,
     QtyReleased: %(N_L_Rel)s, UOM: Text(L.UOM), LineStatus: Upper(Text(L.LineStatus)),
     UnitCost: %(N_L_Cost)s, StoreLocation: Text(L.StoreLocation), Remarks: Text(L.Remarks)});
nfDeadStatus = ["COMPLETED", "CANCELLED", "REJECTED"];
nfHoldStatus = ["RESERVED", "READY FOR RELEASE", "PARTIALLY RELEASED", "PURCHASE REQUIRED"];
// stock held for a request = reserved but not yet released
nfHeld = Filter(nfLines As HL, HL.QtyReserved - HL.QtyReleased > 0 &&
    LookUp(nfReq As RQ, RQ.RequestNo = HL.RequestNo).Status in nfHoldStatus);
nfResv = ForAll(Distinct(nfHeld, PN) As G, {PN: G.Value, Res: Sum(Filter(nfHeld, PN = G.Value), QtyReserved - QtyReleased)});

// ---------- LIVE STOCK: same answer as the LiveStock tab, plus reservations ----------
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
nfCategories = Sort(Distinct(Filter(nfParts, !IsBlank(Category)), Category), Value);

// ---------- request views ----------
nfReqView = AddColumns(nfReq,
    Lines, CountRows(Filter(nfLines As X, X.RequestNo = RequestNo)),
    ShortLines, CountRows(Filter(nfLines As X, X.RequestNo = RequestNo && X.LineStatus in ["SHORTAGE", "NEW PART"])),
    ShortQty, Sum(Filter(nfLines As X, X.RequestNo = RequestNo), Max(0, QtyRequested - Max(QtyReserved, QtyReleased))),
    IsMine, RaisedByEmail = nfEmail);
nfQueueCount = CountRows(Filter(nfReq, Status in ["SUBMITTED", "ADMIN REVIEW"]));
nfMyOpenCount = CountRows(Filter(nfReq, RaisedByEmail = nfEmail && !(Status in nfDeadStatus)));
nfYearPfx = Text(Year(Today()));
nfNextReqSeq = Coalesce(Max(ForAll(Filter(nfReq, StartsWith(RequestNo, "REQ-" & nfYearPfx & "-") ||
    StartsWith(RequestNo, "SHT-" & nfYearPfx & "-")) As R, IfError(Value(Right(R.RequestNo, 5)), 0)), Value), 0) + 1;

// ---------- shortfall book (what open, already-reserved requests still cannot be given) ----------
// Shortfall = requested - reserved.  (The HTA computed requested - reserved - released, which
// hides a real shortfall once the reserved part is released; see docs/06.)
nfGapLines = Filter(nfLines As GL, GL.QtyRequested - Max(GL.QtyReserved, GL.QtyReleased) > 0 &&
    With({st: LookUp(nfReq As RQ, RQ.RequestNo = GL.RequestNo).Status},
        !(st in nfDeadStatus) && !(st in ["SUBMITTED", "ADMIN REVIEW"])));
nfShortBook = Sort(ForAll(Distinct(nfGapLines, PN) As G,
    With({rows: Filter(nfGapLines, PN = G.Value)},
        {PN: G.Value, PartNo: First(rows).PartNo, Description: First(rows).Description,
         Qty: Sum(rows, QtyRequested - Max(QtyReserved, QtyReleased)),
         Requests: Concat(Distinct(rows, RequestNo), Value, ", "),
         Who: Concat(Distinct(ForAll(rows As W, LookUp(nfReq As RQ, RQ.RequestNo = W.RequestNo).RaisedByName), Value), Value, ", "),
         NewPart: IsBlank(LookUp(nfParts, PN = G.Value))})), Qty, SortOrder.Descending);

// ---------- other tabs ----------
nfPurch = ForAll(Filter(tblPurch, !IsBlank(PartNo) && !StartsWith(Text(PartNo), "SAMPLE")) As U,
    {PartNo: Trim(Text(U.PartNo)), PN: Upper(Trim(Text(U.PartNo))), Description: Text(U.Description),
     QtyRequired: %(N_U_Need)s, QtyConfirmed: %(N_U_Conf)s, RequestNo: Text(U.RequestNo),
     RaisedBy: Text(U.RaisedBy), PRNumber: Text(U.PRNumber), SupplierNo: Text(U.SupplierNo),
     SupplierName: Text(U.SupplierName), Stage: Upper(Coalesce(Text(U.Stage), "REQUIRED")),
     DateRaised: %(D_U_Raised)s, ExpectedDate: %(D_U_Eta)s, Notes: Text(U.Notes)});
nfProc = ForAll(Filter(tblProc, !IsBlank(PRNumber) && !StartsWith(Text(PRNumber), "SAMPLE")) As X,
    {PRNumber: Text(X.PRNumber), Department: Text(X.Department), Summary: Text(X.Summary),
     ServiceType: Text(X.ServiceType), Qty: %(N_X_Qty)s, DateRaised: %(D_X_Raised)s, RaisedBy: Text(X.RaisedBy),
     ApprovedBy: Text(X.ApprovedBy), ApprovedDate: %(D_X_Appr)s, PONumber: Text(X.PONumber),
     Vendor: Text(X.Vendor), POAmount: %(N_X_Amt)s, Stage: Upper(Coalesce(Text(X.Stage), "PR RAISED")),
     PODate: %(D_X_PODate)s, DeliveredDate: %(D_X_Del)s, Notes: Text(X.Notes), PRAmount: %(N_X_PRAmt)s,
     InvestmentType: Text(X.InvestmentType), POApprovedDate: %(D_X_POAppr)s, Ownership: Text(X.Ownership),
     POCopyPath: Text(X.POCopyPath)});
nfLic = ForAll(Filter(tblLicenses, !IsBlank(SoftwareName) && !StartsWith(Text(SoftwareName), "SAMPLE")) As C,
    With({exp: %(D_C_Exp)s},
        {SoftwareName: Text(C.SoftwareName), Vendor: Text(C.Vendor), LicenseType: Text(C.LicenseType),
         SeatsTotal: %(N_C_Tot)s, SeatsInUse: %(N_C_Use)s, ExpiryDate: exp, AnnualCost: %(N_C_Cost)s,
         Notes: Text(C.Notes),
         Status: If(IsBlank(exp), "", exp < Today(), "EXPIRED", exp <= DateAdd(Today(), 45, TimeUnit.Days), "EXPIRING SOON", "ACTIVE")}));
nfNewPart = ForAll(Filter(tblNewPart, !IsBlank(RequestNo) && !StartsWith(Text(RequestNo), "SAMPLE")) As NP,
    {SrNo: %(N_NP_Sr)s, RequestNo: Text(NP.RequestNo), RequesterName: Text(NP.RequesterName),
     Category: Text(NP.Category), SubCategory: Text(NP.SubCategory), PlantCode: Text(NP.PlantCode),
     PartName: Text(NP.PartName), MakeBrand: Text(NP.MakeBrand), ModelNo: Text(NP.ModelNo),
     OtherSpecs: Text(NP.OtherSpecs), Remarks: Text(NP.Remarks), UOM: Text(NP.UOM), HSNCode: Text(NP.HSNCode),
     Status: Upper(Coalesce(Text(NP.Status), "DRAFT")), DateRaised: %(D_NP_Raised)s});
nfInv = ForAll(Filter(tblInvoice, !IsBlank(InvoiceNo) && !StartsWith(Text(InvoiceNo), "SAMPLE")) As V,
    {InvoiceNo: Text(V.InvoiceNo), InvoiceDate: %(D_V_Date)s, ToName: Text(V.ToName), CCName: Text(V.CCName),
     FromName: Text(V.FromName), FromExt: Text(V.FromExt), FromMobile: Text(V.FromMobile),
     HarnessPartNos: Text(V.HarnessPartNos), JobDescription: Text(V.JobDescription),
     BusinessUnit: Text(V.BusinessUnit), BUContact: Text(V.BUContact), CostCentre: Text(V.CostCentre),
     ApplicationDesc: Text(V.ApplicationDesc), DetailsOfRequest: Text(V.DetailsOfRequest),
     NoOfCircuits: %(N_V_Circ)s, DCContact: Text(V.DCContact), DCMobile: Text(V.DCMobile),
     JobReceived: %(D_V_Recd)s, StartDate: %(D_V_Start)s, CompletionDate: %(D_V_Done)s,
     MaterialCost: %(N_V_Mat)s, AssemblyCost: %(N_V_Asm)s, TransportCost: %(N_V_Trn)s,
     TotalCost: %(N_V_Tot)s, RefRequest: Text(V.RefRequest), ImagePath: Text(V.ImagePath),
     Status: Upper(Coalesce(Text(V.Status), "DRAFT")), Notes: Text(V.Notes)});
nfCalib = ForAll(Filter(tblCalib, !IsBlank(AssetNo) && !StartsWith(Text(AssetNo), "SAMPLE")) As K,
    With({due: %(D_K_Due)s},
        {AssetNo: Text(K.AssetNo), AssetName: Text(K.AssetName), Location: Text(K.Location), DueDate: due,
         Owner: Text(K.Owner), Days: If(IsBlank(due), Blank(), DateDiff(Today(), due, TimeUnit.Days))}));
nfCalibDue = Sort(Filter(nfCalib, !IsBlank(Days) && Days <= 30), Days);

// ---------- invoice numbering: IDC EDS/{FY}/{NNN}, restarts every 1 April ----------
nfFYStart = If(Month(Today()) >= 4, Year(Today()), Year(Today()) - 1);
nfFY = Text(Mod(nfFYStart, 100), "00") & "-" & Text(Mod(nfFYStart + 1, 100), "00");
nfInvPrefix = "IDC EDS/" & nfFY & "/";
nfNextInvNo = nfInvPrefix & Text(Coalesce(Max(ForAll(Filter(nfInv, StartsWith(InvoiceNo, nfInvPrefix)) As I,
    IfError(Value(Mid(I.InvoiceNo, Len(nfInvPrefix) + 1)), 0)), Value), 0) + 1, "000");
nfNextNprSeq = Coalesce(Max(ForAll(Filter(nfNewPart, StartsWith(RequestNo, "NPR-" & nfYearPfx & "-")) As R,
    IfError(Value(Right(R.RequestNo, 5)), 0)), Value), 0) + 1;

// ---------- manager dashboard ----------
nfRevBU0 = ForAll(Distinct(nfInv, Upper(Coalesce(BusinessUnit, "UNSPECIFIED"))) As G,
    {K: G.Value, V: Sum(Filter(nfInv, Upper(Coalesce(BusinessUnit, "UNSPECIFIED")) = G.Value), TotalCost)});
nfRevBU1 = Sort(nfRevBU0, V, SortOrder.Descending);
nfRevByBU = ForAll(Sequence(CountRows(nfRevBU1)) As I,
    With({r: Index(nfRevBU1, I.Value)}, {K: r.K, V: r.V, Col: Index(nfChartHex, Mod(I.Value - 1, 8) + 1).Value}));
nfRevTotal = Sum(nfInv, TotalCost);
nfProcBars = Table(
    {K: "DELIVERED", V: CountRows(Filter(nfProc, "DELIVERED" in Stage)), C: cOk},
    {K: "PO", V: CountRows(Filter(nfProc, !("DELIVERED" in Stage) && ("PO" in Stage || "GRN" in Stage))), C: cSteel},
    {K: "PR", V: CountRows(Filter(nfProc, !("DELIVERED" in Stage) && !("PO" in Stage) && !("GRN" in Stage))), C: cJcb});
nfOngoing = CountRows(Filter(nfReq, !(Status in nfDeadStatus)));
nfUpcoming = CountRows(Filter(nfReq As R, !(R.Status in nfDeadStatus) &&
    CountRows(Filter(nfLines As L, L.RequestNo = R.RequestNo && (L.QtyReserved > 0 || L.QtyRequested > L.QtyReleased))) > 0));

// ---------- ledger: every movement with the request it belongs to ----------
nfLedger = With({n: CountRows(nfMoves)},
    ForAll(Sequence(n) As I,
        With({M: Index(nfMoves, n - I.Value + 1)},
            With({rq: LookUp(nfReq, RequestNo = M.Reference), p: LookUp(nfParts, PN = M.PN),
                  rl: Lower(M.Reason)},
                {Date: M.Date, PartNo: M.PartNo, PN: M.PN, Description: p.Description, Type: M.Type,
                 SQty: M.SQty, Qty: M.Qty, Reference: M.Reference, UnitCost: M.UnitCost, Reason: M.Reason,
                 Harness: rq.HarnessPartNo, Machine: rq.Machine,
                 IssuedTo: Coalesce(rq.RaisedByName,
                    If(StartsWith(rl, "issued to "),
                        With({rest: Mid(M.Reason, 11)},
                            If(IsBlank(Find(" for ", Lower(rest))), rest, Left(rest, Find(" for ", Lower(rest)) - 1))),
                        "")),
                 IssuedBy: First(Split(M.By, "@")).Value}))));
"""


def formulas():
    pill = "Table(\n    " + ",\n    ".join('{K:"%s", C:%s}' % (k, c) for k, c in PILL) + ")"
    sub = {
        "PILL": pill, "NAV": nav_table(),
        "N_P_UnitCost": N("P.UnitCost"), "N_P_Ref": N("P.ReorderRefQty"),
        "N_M_Qty": N("M.Qty"), "D_M_Date": D("M.Date"), "N_M_Cost": N("M.UnitCost"),
        "D_R_Raised": D("R.DateRaised"), "N_R_Circ": N("R.NoOfCircuits"), "D_R_Need": D("R.RequiredBy"),
        "N_L_Sr": N("L.Sr"), "N_L_Q": N("L.QtyRequested"), "N_L_Res": N("L.QtyReserved"),
        "N_L_Rel": N("L.QtyReleased"), "N_L_Cost": N("L.UnitCost"),
        "N_U_Need": N("U.QtyRequired"), "N_U_Conf": N("U.QtyConfirmed"),
        "D_U_Raised": D("U.DateRaised"), "D_U_Eta": D("U.ExpectedDate"),
        "N_X_Qty": N("X.Qty"), "D_X_Raised": D("X.DateRaised"), "D_X_Appr": D("X.ApprovedDate"),
        "N_X_Amt": N("X.POAmount"), "D_X_PODate": D("X.PODate"), "D_X_Del": D("X.DeliveredDate"),
        "N_X_PRAmt": N("X.PRAmount"), "D_X_POAppr": D("X.POApprovedDate"),
        "D_C_Exp": D("C.ExpiryDate"), "N_C_Tot": N("C.SeatsTotal"), "N_C_Use": N("C.SeatsInUse"),
        "N_C_Cost": N("C.AnnualCost"),
        "N_NP_Sr": N("NP.SrNo"), "D_NP_Raised": D("NP.DateRaised"),
        "D_V_Date": D("V.InvoiceDate"), "N_V_Circ": N("V.NoOfCircuits"), "D_V_Recd": D("V.JobReceived"),
        "D_V_Start": D("V.StartDate"), "D_V_Done": D("V.CompletionDate"), "N_V_Mat": N("V.MaterialCost"),
        "N_V_Asm": N("V.AssemblyCost"), "N_V_Trn": N("V.TransportCost"), "N_V_Tot": N("V.TotalCost"),
        "D_K_Due": D("K.DueDate"),
        "NAVSW": nav_switch(),
    }
    return (FORMULAS % sub).strip("\n")


ONSTART = r"""
// App.OnStart - only session state. All data lives in the named formulas (App.Formulas).
Set(gRole, nfRoleCanon);
Set(gBusy, false);
Set(gReqNo, "");
Set(gInvReq, "");
Set(gInvEdit, "");
Set(gCostReq, "");
Set(gPrintKind, "cost");
Set(gPrinting, false);
Set(gBomText, "");
Set(gShortSr, -1);
Set(gEditPr, "");
Set(gEditPurch, "");
Set(gPanel, "");
Set(gVendorPick, "");
Set(gEditPurchReq, "");
Set(gPrintCkt, 200);
ClearCollect(colBom, {Sr: 0, PartNo: "", PN: "", Qty: 0, Description: "", UOM: "", Location: "", OnHand: 0,
    Reserved: 0, Avail: 0, UnitCost: 0, Short: 0, Status: "", Found: false});
Clear(colBom);
ClearCollect(colNP, ForAll(Sequence(3) As S, {Id: S.Value, RequesterName: nfMeName, Category: "", SubCategory: "",
    PlantCode: "", PartName: "", MakeBrand: "", ModelNo: "", OtherSpecs: "", Remarks: "", UOM: "NO", HSNCode: ""}));
ClearCollect(colInvLines, {Sr: 0, PartNo: "", Description: "", Qty: 0, UnitCost: 0});
Clear(colInvLines);
ClearCollect(colCostLines, {Sr: 0, PartNo: "", Description: "", Qty: 0, UnitCost: 0});
Clear(colCostLines)
"""


def onstart():
    return ONSTART.strip("\n")


STARTSCREEN = 'If(IsBlank(nfMeRow), scrNoAccess, nfRoleCanon = "Manager", scrMgrDash, scrDash)'
