"""
App-level Power Fx: App.Formulas (named formulas), App.OnStart and App.StartScreen.

Named formulas are recalculated automatically whenever an Excel table changes
(after a Patch/Collect/Refresh), so stock on hand, reservations and the request
views are never stored anywhere - exactly like the HTA, stock is ALWAYS the sum
of the Movements rows.
"""
import art

ICON = {"dash": "Home", "stock": "Search", "bom": "ListScrollWatchlist", "newreq": "AddDocument", "myreq": "Note",
        "newpart": "Add", "queue": "Check", "newpartq": "DocumentWithContent", "inventory": "Devices",
        "inward": "ArrowDown", "ledger": "Sort", "demand": "TrendingHashtag", "invoice": "Draw",
        "invlist": "DocumentWithContent", "cost": "HalfFilledCircle", "proc": "Waypoint", "purch": "ArrowRight",
        "lic": "Lock", "team": "People", "about": "Information"}

MYWORK = ("My Work", [("stock", "Check Stock"), ("bom", "BOM Compare"), ("newreq", "New Request"),
                      ("myreq", "My Requests"), ("newpart", "Brand New Purchase Part")])
NAV = {
    "Engineer": [("Overview", [("dash", "Dashboard")]),
                 ("Material", [("stock", "Check Stock"), ("bom", "BOM Compare"), ("newreq", "New Request"),
                               ("myreq", "My Requests"), ("newpart", "Brand New Purchase Part")]),
                 ("Help", [("about", "About")])],
    "Lab Admin": [("Overview", [("dash", "Dashboard")]),
                  ("Requests", [("queue", "Request Queue"), ("newpartq", "New Purchase Parts")]),
                  ("Inventory", [("inventory", "Component Inventory"), ("inward", "Material Inward"),
                                 ("ledger", "Stock Transactions"), ("demand", "High Demand Parts")]),
                  ("Deliveries", [("invoice", "Create Invoice"), ("invlist", "Invoices"), ("cost", "Cost Sheet")]),
                  ("Purchasing", [("proc", "Procurement (PR/PO)"), ("purch", "Ongoing Purchase"),
                                  ("lic", "Software Licenses")]),
                  MYWORK,
                  ("Admin", [("team", "Team Access"), ("about", "About")])],
    "Manager": [("Overview", [("dash", "Dashboard")]),
                ("Approvals & Reports", [("queue", "All Requests"), ("newpartq", "New Purchase Parts"),
                                         ("proc", "Procurement (PR/PO)"), ("invlist", "Invoices"),
                                         ("purch", "Ongoing Purchase"), ("demand", "High Demand Parts"),
                                         ("lic", "Software Licenses"), ("inventory", "Inventory")]),
                MYWORK,
                ("Help", [("about", "About")])],
}

# key -> screen.  'dash' is role dependent.
SCREEN_OF = {"stock": "scrStock", "bom": "scrBom", "newreq": "scrNewReq", "myreq": "scrMyReq",
             "newpart": "scrNewPart", "queue": "scrQueue", "newpartq": "scrNewPartQ",
             "inventory": "scrInventory", "inward": "scrInward", "ledger": "scrLedger", "demand": "scrDemand",
             "invoice": "scrInvoice", "invlist": "scrInvList", "cost": "scrCost", "proc": "scrProc",
             "purch": "scrPurch", "lic": "scrLic", "team": "scrTeam", "about": "scrAbout"}

# raw value (as stored in Excel) -> colour, display text (Title Case, consistent everywhere)
PILL = [("IN STOCK", "cOk", "In Stock"), ("LOW STOCK", "cWarn", "Low Stock"), ("OUT OF STOCK", "cStop", "Out of Stock"),
        ("FULLY RESERVED", "cSteel", "Fully Reserved"), ("AVAILABLE", "cOk", "Available"), ("SHORTAGE", "cStop", "Shortage"),
        ("NEW PART", "cSteel", "New Part"), ("PARTIAL", "cWarn", "Partial"), ("DRAFT", "cInk3", "Draft"),
        ("SUBMITTED", "cSteel", "Submitted"), ("ADMIN REVIEW", "cWarn", "Admin Review"), ("APPROVED", "cJcb", "Approved"),
        ("RESERVED", "cJcb", "Reserved"), ("READY FOR RELEASE", "cOk", "Ready for Release"),
        ("PARTIALLY RELEASED", "cWarn", "Partially Released"), ("RELEASED", "cOk", "Released"),
        ("COMPLETED", "cInk2", "Completed"), ("CANCELLED", "cStop", "Cancelled"), ("REJECTED", "cStop", "Rejected"),
        ("PURCHASE REQUIRED", "cStop", "Purchase Required"), ("PR RAISED", "cSteel", "PR Raised"),
        ("PO RAISED", "cJcb", "PO Raised"), ("GRN IN PROGRESS", "cWarn", "GRN in Progress"),
        ("DELIVERED (CLOSED)", "cOk", "Delivered (Closed)"), ("EXPIRED", "cStop", "Expired"),
        ("EXPIRING SOON", "cWarn", "Expiring Soon"), ("ACTIVE", "cOk", "Active"), ("RECEIPT", "cOk", "Receipt"),
        ("RELEASE", "cStop", "Release"), ("RETURN", "cOk", "Return"), ("ADJUST+", "cSteel", "Adjust+"),
        ("ADJUST-", "cWarn", "Adjust-"), ("SCRAP", "cStop", "Scrap"), ("REQUIRED", "cStop", "Required"),
        ("IN TRANSIT", "cSteel", "In Transit"), ("RECEIVED", "cOk", "Received"), ("ISSUED", "cOk", "Issued"),
        ("SHORTFALL", "cSteel", "Shortfall"), ("OK", "cOk", "OK"), ("ISSUES", "cWarn", "Issues"),
        ("LAB LEAD", "cJcb", "Lab Lead"), ("LAB ADMIN", "cJcb", "Lab Admin"), ("MANAGER", "cSteel", "Manager"),
        ("ENGINEER", "cInk2", "Engineer"), ("PO", "cJcb", "PO"), ("FOC", "cSteel", "FOC"),
        ("NOT SET UP", "cWarn", "Not Set Up"), ("SET", "cOk", "Set"), ("TEMPORARY", "cWarn", "Temporary"),
        ("NOT SET", "cInk3", "Not Set"), ("PENDING APPROVAL", "cJcb", "Pending Approval"), ("MATERIAL", "cInk2", "Material"), ("SERVICE", "cInk2", "Service"),
        ("TOOL", "cInk2", "Tool"), ("LICENSE", "cInk2", "License"), ("COMPONENTS", "cInk2", "Components")]


def nav_table():
    rows = []
    for role, groups in NAV.items():
        seq = 0
        for grp, items in groups:
            seq += 1
            rows.append('{Role:"%s", Seq:%d, Hdr:true, Key:"", Label:"%s", Ico:Icon.Home}' % (role, seq, grp))
            for key, label in items:
                seq += 1
                rows.append('{Role:"%s", Seq:%d, Hdr:false, Key:"%s", Label:"%s", Ico:Icon.%s}'
                            % (role, seq, key, label, ICON[key]))
    return "Table(\n    " + ",\n    ".join(rows) + ")"


def nav_switch():
    parts = ['"dash", Navigate(If(gRole = "Manager", scrMgrDash, scrDash), ScreenTransition.Fade)']
    for k, s in SCREEN_OF.items():
        parts.append('"%s", Navigate(%s, ScreenTransition.Fade)' % (k, s))
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

// ---------- theme v2: dark glass over a sunset workshop, gold + orange accents ----------
cBg = RGBA(16, 12, 16, 1);
cPanel = RGBA(22, 17, 22, 0.80);
cPanel2 = RGBA(40, 30, 32, 0.86);
cSunk = RGBA(10, 8, 11, 0.55);
cGlass = RGBA(14, 10, 14, 0.66);
cLine = RGBA(255, 255, 255, 0.10);
cLine2 = RGBA(255, 255, 255, 0.20);
cInk = RGBA(248, 244, 238, 1);
cInk2 = RGBA(214, 205, 196, 1);
cInk3 = RGBA(168, 157, 148, 1);
cJcb = RGBA(253, 185, 19, 1);
cJcbDark = RGBA(247, 148, 29, 1);
cOrange = RGBA(247, 148, 29, 1);
cJcbWash = RGBA(253, 185, 19, 0.16);
cOnJcb = RGBA(28, 20, 8, 1);
cSteel = RGBA(128, 178, 222, 1);
cOk = RGBA(96, 196, 140, 1);
cWarn = RGBA(244, 170, 66, 1);
cStop = RGBA(242, 114, 98, 1);
cInput = RGBA(252, 250, 246, 1);
cInputHover = RGBA(255, 246, 224, 1);
cInputInk = RGBA(28, 22, 16, 1);
cInputHint = RGBA(120, 110, 100, 1);
cInputLine = RGBA(205, 192, 178, 1);
cRowHover = RGBA(253, 185, 19, 0.10);
cClear = RGBA(0, 0, 0, 0);
fMono = "Consolas, 'Courier New', monospace";
fUI = "'Segoe UI', 'Open Sans', sans-serif";
nfChartHex = ["#fdb913", "#f7941d", "#80b2de", "#60c48c", "#f27262", "#d6cdc4", "#c88f10", "#a98fd8"];
// vector art (no image files, so it also works with Paste code)
imgBg = %(IMG_BG)s;
imgHeader = %(IMG_HEADER)s;
imgLogo = %(IMG_LOGO)s;
imgLine = %(IMG_LINE)s;
imgAvatar = %(IMG_AVATAR)s;
nfPill = %(PILL)s;

// ---------- navigation (same groups and labels as the HTA) ----------
nfNav = %(NAV)s;

// ---------- who is signed in: see the Login screen (username + password from the Users tab).
// The signed-in person lives in variables gMe, gMeName, gMeEmail, gRole... set by the Log In button.

// ---------- settings tab ----------
nfSet = ForAll(Filter(tblSettings, !IsBlank(Key)) As S, {Key: Trim(Text(S.Key)), Val: Text(S.Value)});
nLowConn = Coalesce(Value(LookUp(nfSet, Key = "LowStockPct_Connector").Val), 25);
nLowTerm = Coalesce(Value(LookUp(nfSet, Key = "LowStockPct_Terminal").Val), 20);
nLowDef = Coalesce(Value(LookUp(nfSet, Key = "LowStockPct_Default").Val), 20);
tLabName = Coalesce(LookUp(nfSet, Key = "LabName").Val, "EDS Lab");
tSupport = Coalesce(LookUp(nfSet, Key = "SupportContact").Val, "your Lab Admin");
// Data health: the workbook counts its own rows with Excel formulas (Settings tab), so the app can
// prove it has read every row. If these differ, the Data row limit is too low or a table is not connected.
nXlParts = Value(LookUp(nfSet, Key = "ExcelPartRows").Val);
nXlMoves = Value(LookUp(nfSet, Key = "ExcelMovementRows").Val);
nXlStock = Value(LookUp(nfSet, Key = "ExcelStockTotal").Val);
nAppParts = CountRows(tblParts);
nAppMoves = CountRows(tblMoves);
nAppStock = Round(Sum(nfMoves, SQty), 3);
nfHealthOk = !IsBlank(nXlMoves) && nXlParts = nAppParts && nXlMoves = nAppMoves && Abs(nXlStock - nAppStock) < 0.001;
nfHealthText = If(IsBlank(nXlMoves), "Health rows missing in Settings",
    nfHealthOk, "All rows read",
    nAppMoves < nXlMoves, "Only " & nAppMoves & " of " & nXlMoves & " movements read",
    "Counts differ from Excel");

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
    ShortQty, Sum(Filter(nfLines As X, X.RequestNo = RequestNo), Max(0, QtyRequested - Max(QtyReserved, QtyReleased))));
nfQueueCount = CountRows(Filter(nfReq, Status in ["SUBMITTED", "ADMIN REVIEW", "APPROVED"]));
nfYearPfx = Text(Year(Today()));
nfNextReqSeq = Coalesce(Max(ForAll(Filter(nfReq, StartsWith(RequestNo, "REQ-" & nfYearPfx & "-") ||
    StartsWith(RequestNo, "SHT-" & nfYearPfx & "-")) As R, IfError(Value(Right(R.RequestNo, 5)), 0)), Value), 0) + 1;

// ---------- shortfall book (what open, already-reserved requests still cannot be given) ----------
// Shortfall = requested - reserved.  (The HTA computed requested - reserved - released, which
// hides a real shortfall once the reserved part is released; see docs/06.)
nfGapLines = Filter(nfLines As GL, GL.QtyRequested - Max(GL.QtyReserved, GL.QtyReleased) > 0 &&
    With({st: LookUp(nfReq As RQ, RQ.RequestNo = GL.RequestNo).Status},
        !(st in nfDeadStatus) && !(st in ["SUBMITTED", "ADMIN REVIEW", "APPROVED"])));
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
    {K: "Delivered", V: CountRows(Filter(nfProc, "DELIVERED" in Stage)), C: cOk},
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
    pill = "Table(\n    " + ",\n    ".join('{K:"%s", C:%s, D:"%s"}' % (k, c, d) for k, c, d in PILL) + ")"
    sub = {
        "PILL": pill, "NAV": nav_table(),
        "IMG_BG": art.photo_uri(), "IMG_HEADER": art.uri(art.HEADER), "IMG_LOGO": art.uri(art.LOGO),
        "IMG_LINE": art.uri(art.LINE), "IMG_AVATAR": art.uri(art.AVATAR),
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
Set(gRole, "");
Set(gRoleHome, "Engineer");
Set(gMe, LookUp(tblUsers, false));
Set(gPend, LookUp(tblUsers, false));
Set(gMeName, "");
Set(gMeEmail, "");
Set(gMeInitials, "");
Set(gIsLead, false);
Set(gIsAdmin, false);
Set(gIsMgr, false);
Set(gRoleOptions, Table({Value: "Engineer"}));
Set(gLoginMode, "login");
Set(gLoginMsg, "");
Set(gLoginTries, 0);
Set(gTempCode, "");
Set(gLastSync, Now());
Set(gSyncNote, "");
Set(gPhotoCheck, "Not tested yet on this device.");
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
ClearCollect(colNP, {Id: 0, RequesterName: "", Category: "", SubCategory: "", PlantCode: "", PartName: "",
    MakeBrand: "", ModelNo: "", OtherSpecs: "", Remarks: "", UOM: "NO", HSNCode: ""});
Clear(colNP);
Set(gNpForm, {Id: 0, RequesterName: "", Category: "", SubCategory: "", PlantCode: "", PartName: "",
    MakeBrand: "", ModelNo: "", OtherSpecs: "", Remarks: "", UOM: "NO", HSNCode: ""});
ClearCollect(colInvLines, {Sr: 0, PartNo: "", Description: "", Qty: 0, UnitCost: 0});
Clear(colInvLines);
ClearCollect(colCostLines, {Sr: 0, PartNo: "", Description: "", Qty: 0, UnitCost: 0});
Clear(colCostLines)
"""


def onstart():
    return ONSTART.strip("\n")


STARTSCREEN = 'scrWelcome'


# ----------------------------------------------------------------------------- login helpers (Python -> Power Fx)
ALPHA = "".join(chr(c) for c in range(32, 127)).replace('"', '""')


def role_canon(x):
    """One role word as typed in the Users tab -> Engineer / Lab Admin / Lab Lead / Manager / Pending / Disabled."""
    return ('With({k: Lower(Substitute(Substitute(Substitute(Substitute(%s, " ", ""), "-", ""), "_", ""), ".", ""))}, '
            'If(IsBlank(k), "Engineer", k in ["pending", "requested"], "Pending", '
            'k in ["disabled", "rejected", "left", "inactive"], "Disabled", '
            'k in ["lablead", "lead", "labhead", "teamlead"], "Lab Lead", '
            '"admin" in k || k in ["store", "storekeeper", "stores"] || "incharge" in k, "Lab Admin", '
            '"manager" in k || k in ["mgr", "hod", "head"], "Manager", "Engineer"))' % x)


def role_list(role_text):
    return ('ForAll(Split(Substitute(Substitute(Substitute(%s, ";", ","), "/", ","), "+", ","), ",") As RR, %s)'
            % (role_text, role_canon("RR.Value")))


HASH_K = [(7919, 104723, 15485863, 2750159, 999983), (6007, 130363, 32452843, 1299709, 1000003),
          (4513, 611953, 49979687, 3571, 7368787), (7727, 86028121, 67867967, 104395301, 2038074743 % 1000003)]


def hash_fx(pw, salt, prefix):
    """Scrambles a password with its username as salt (the Excel cell never holds the password itself).
    Pure Power Fx: no crypto functions exist in canvas apps. tools/verify checks it against hash_py()."""
    piece = ('Text(Mod(Sum(ForAll(Sequence(n) As J, With({x: Index(c, J.Value).Value, y: Index(c, Mod(J.Value, n) + 1).Value, '
             'z: Index(c, Mod(J.Value + 1, n) + 1).Value}, Mod(x * x * x * (J.Value * %d + %d) + x * y * (J.Value * %d + %d) '
             '+ y * z * %d + x, 2147483647))), Value), 2147483647), "0000000000")')
    pieces = " & ".join(piece % k for k in HASH_K)
    return ('With({s: Lower(%s) & "|" & %s & "|" & Lower(%s) & "|EDSLAB-PA1"}, '
            'With({c: ForAll(Sequence(Len(s)) As I, Coalesce(Find(Mid(s, I.Value, 1), "%s"), 97))}, '
            'With({n: CountRows(c)}, "%s" & %s)))' % (salt, pw, salt, ALPHA, prefix, pieces))


def hash_py(pw, salt, prefix):
    alpha = "".join(chr(c) for c in range(32, 127))
    s = salt.lower() + "|" + pw + "|" + salt.lower() + "|EDSLAB-PA1"
    c = [(alpha.find(ch) + 1) or 97 for ch in s]
    n, out = len(c), prefix
    for k1, k2, k3, k4, k5 in HASH_K:
        tot = 0
        for j in range(1, n + 1):
            x, y, z = c[j - 1], c[j % n], c[(j + 1) % n]
            tot += (x ** 3 * (j * k1 + k2) + x * y * (j * k3 + k4) + y * z * k5 + x) % 2147483647
        out += "%010d" % (tot % 2147483647)
    return out


def login_ok(u):
    """Behaviour formula: make record u the signed-in person and open their usual role."""
    return ('Set(gMe, %(U)s); Set(gMeName, Coalesce(Trim(Text(gMe.FullName)), Trim(Text(gMe.Username)))); '
            'Set(gMeEmail, Lower(Coalesce(Trim(Text(gMe.Email)), Trim(Text(gMe.Username))))); '
            'Set(gMeInitials, Upper(Concat(FirstN(Split(gMeName, " "), 2), Left(Value, 1)))); '
            'With({rl: %(RL)s}, Set(gIsLead, "Lab Lead" in rl); Set(gIsAdmin, gIsLead || "Lab Admin" in rl); '
            'Set(gIsMgr, "Manager" in rl); Set(gRoleHome, Coalesce(First(rl).Value, "Engineer"))); '
            'Set(gRoleOptions, ForAll(Filter(Table({V: "Engineer", Ok: true}, {V: "Lab Admin", Ok: gIsAdmin}, '
            '{V: "Manager", Ok: gIsAdmin || gIsMgr}), Ok) As RO, {Value: RO.V})); '
            'Set(gRole, gRoleHome); Set(gLoginTries, 0); Set(gLoginMode, "login"); Set(gLoginMsg, ""); '
            'Set(gNpForm, Patch(gNpForm, {RequesterName: gMeName})); Set(gLastSync, Now()); '
            'Notify("Welcome, " & gMeName & ".", NotificationType.Success); '
            'Navigate(If(gRole = "Manager", scrMgrDash, scrDash), ScreenTransition.Fade)'
            % {"U": u, "RL": role_list("Text(gMe.Role)")})
