"""
Every screen of the JCB EDS Lab Material Portal, mirroring the HTA v8 views one for one.
Each screen = one root container (header + left nav + scrolling content column), so that
Route B can paste a whole screen with ONE "Paste code".
"""
from pa import (tc, Ctl, box, lbl, rect, btn, overlay, inp, dd, date, gallery, img, icon, pill, q, MONO, UI, ADDMEDIA, TIMER)
from ui import (prepend, W, sec, head, card, tiles, Col, table, field, meter, kv, num, inr, inrs, fdate, noon, hist, cost)
from appfx import nav_switch, hash_fx, role_canon

ADMIN = 'gRole in ["Lab Admin", "Lab Lead"]'
MGR = 'gRole = "Manager"'
APPROVER = 'gRole in ["Lab Admin", "Lab Lead", "Manager"]'
ENG = 'gRole = "Engineer"'
BUSY = "gBusy"

SCREENS = []          # (screen name, nav key, root container)
APP_VERSION = "2.0.5 · 08-Oct-2026"   # shown on the Welcome screen, so you can tell which build is imported


def DISP(x):
    """Status code as stored in Excel (PR RAISED) -> the Title Case text shown everywhere (PR Raised)."""
    return "Coalesce(LookUp(nfPill, K = Upper(%s)).D, %s)" % (x, x)


def disp_list(codes, first=None):
    """A dropdown list of codes shown in Title Case. Formulas read it back with Upper(...Selected.Value)."""
    import json as _j
    from appfx import PILL
    d = {k: v for k, _, v in PILL}
    items = [d.get(c, tc(c.title()) if c.isupper() else c) for c in _j.loads(codes)]
    if first:
        items = [first] + items
    return "[" + ", ".join('"%s"' % i for i in items) + "]"


REFRESH_ALL = ("Refresh(tblParts); Refresh(tblMoves); Refresh(tblRequests); Refresh(tblReqLines); Refresh(tblPurch); "
               "Refresh(tblProc); Refresh(tblInvoice); Refresh(tblNewPart); Refresh(tblLicenses); Refresh(tblUsers); "
               "Refresh(tblSettings); Refresh(tblCalib); Set(gLastSync, Now())")
REFRESH_STOCK = ("Refresh(tblParts); Refresh(tblMoves); Refresh(tblRequests); Refresh(tblReqLines); "
                 "Refresh(tblSettings); Set(gLastSync, Now())")
DASH = 'Navigate(If(gRole = "Manager", scrMgrDash, scrDash), ScreenTransition.Fade)'
LOGOUT = ('Set(gRole, ""); Set(gMe, LookUp(tblUsers, false)); Set(gMeName, ""); Set(gMeEmail, ""); Set(gIsLead, false); '
          'Set(gIsAdmin, false); Set(gIsMgr, false); Set(gRoleOptions, Table({Value: "Engineer"})); Set(gReqNo, ""); '
          'Set(gBomText, ""); Clear(colBom); Clear(colNP); Set(gPanel, ""); Set(gShortSr, -1); Set(gLoginMode, "login"); '
          'Set(gLoginMsg, "✓  You have logged out."); Navigate(scrLogin, ScreenTransition.Fade)')


def backdrop(K, shade="RGBA(8, 6, 10, 0.55)"):
    """The sunset workshop picture behind every screen, graded darker on working screens."""
    return [img("bg" + K, 0, 0, 1366, 768, "imgBg", extra={"ImagePosition": "ImagePosition.Fill"}),
            rect("bgSh" + K, 0, 0, 1366, 768, shade)]


def shell(key, scr, nav_key, content, extra_root=None):
    """Background + glass header + pill navigation + scrolling content column, all inside one root container."""
    K = key
    hdr = [
        rect("hdrBg" + K, 0, 0, 1366, 56, "cGlass"),
        img("hdrLn" + K, 0, 55, 1366, 2, "imgLine", extra={"ImagePosition": "ImagePosition.Stretch"}),
        img("hdrLogo" + K, 14, 8, 40, 40, "imgLogo"),
        lbl("hdrT1" + K, '"EDS Lab Material Portal"', 62, 6, 330, 26, size=16, bold=True, color="cInk"),
        lbl("hdrT2" + K, '"JCB India  ·  " & tLabName', 62, 31, 330, 18, size=9, semibold=True, color="cJcb"),
        btn("hdrSync" + K, 'If(nfHealthOk || !(%s), "●  Live  ·  Synced ", "●  Check Data Health  ·  Synced ") & '
                           'Text(gLastSync, "hh:mm")' % ADMIN, 630, 13, 200, 30, REFRESH_ALL + "; " +
            'Notify("Data refreshed at " & Text(Now(), "hh:mm") & "." & If(%s, " " & nfHealthText & ".", ""), '
            'NotificationType.Information)' % ADMIN, kind="ghost", size=9,
            extra={"Color": "If(nfHealthOk || !(%s), cOk, cWarn)" % ADMIN, "HoverColor": "cJcb", "PressedColor": "cJcb",
                   "Tooltip": q("Refresh all data now. Stock also refreshes by itself every 2 minutes.")}),
        Ctl("hdrTmr" + K, TIMER, {"X": 0, "Y": 0, "Width": 10, "Height": 10, "Duration": 120000, "Repeat": "true",
                                  "AutoStart": "true", "AutoPause": "true", "Visible": "false",
                                  "OnTimerEnd": REFRESH_STOCK}),
        lbl("hdrAsL" + K, '"View as"', 840, 13, 56, 30, size=9, color="cInk3", align="Right",
            visible="CountRows(gRoleOptions) > 1"),
        dd("hdrAs" + K, 902, 13, 128, 30, "gRoleOptions",
           default='If(gRole = "Lab Lead", "Lab Admin", gRole)',
           visible="CountRows(gRoleOptions) > 1",
           onchange='Set(gRole, If(Self.Selected.Value = "Lab Admin" && gIsLead, "Lab Lead", Self.Selected.Value)); ' + DASH,
           extra={"Size": 10, "Tooltip": q("Switch role without logging out (only the roles you hold)")}),
        img("hdrAv" + K, 1042, 10, 36, 36, "imgAvatar"),
        lbl("hdrAvT" + K, "gMeInitials", 1042, 10, 36, 36, size=11, bold=True, color="cOnJcb", align="Center"),
        lbl("hdrNm" + K, "gMeName", 1084, 8, 160, 20, size=11, bold=True, color="cInk"),
        lbl("hdrRl" + K, 'gRole & " view"', 1084, 28, 160, 18, size=9, semibold=True, color="cJcb"),
        btn("hdrOut" + K, '"Log Out"', 1252, 12, 100, 32, LOGOUT, kind="secondary", size=10,
            extra={"Tooltip": q("Back to the login page to choose a role (or let someone else sign in)")}),
    ]
    act = '!ThisItem.Hdr && ThisItem.Key = "%s"' % nav_key
    cnt = ('Switch(ThisItem.Key, "queue", nfQueueCount, "myreq", CountRows(Filter(nfReq, RaisedByEmail = gMeEmail && !(Status in nfDeadStatus))), '
           '"newpartq", CountRows(Filter(nfNewPart, Status = "SUBMITTED")), 0)')
    navrow = [
        lbl("navHdr" + K, "ThisItem.Label", 18, 14, 190, 24, size=10, bold=True, color="cOrange",
            visible="ThisItem.Hdr"),
        btn("navBtn" + K, "ThisItem.Label", 10, 3, 204, 34, "Select(Parent)", kind="ghost", size=10, align="Left",
            radius=17, visible="!ThisItem.Hdr",
            extra={"PaddingLeft": 40, "PaddingRight": 28, "Fill": "If(%s, cJcb, cClear)" % act,
                   "Color": "If(%s, cOnJcb, cInk2)" % act,
                   "HoverFill": "If(%s, cJcb, cJcbWash)" % act, "HoverColor": "If(%s, cOnJcb, cJcb)" % act,
                   "PressedFill": "cOrange", "PressedColor": "cOnJcb",
                   "FontWeight": "If(%s, FontWeight.Bold, FontWeight.Semibold)" % act}),
        Ctl("navIco" + K, "Classic/Icon", {"X": 24, "Y": 11, "Width": 18, "Height": 18, "Icon": "ThisItem.Ico",
                                           "Color": "If(%s, cOnJcb, cJcb)" % act, "OnSelect": "Select(Parent)",
                                           "HoverColor": "cOrange", "Visible": "!ThisItem.Hdr",
                                           "PaddingTop": 0, "PaddingBottom": 0, "PaddingLeft": 0, "PaddingRight": 0}),
        btn("navCnt" + K, cnt, 190, 11, 26, 18, "Select(Parent)", kind="ghost", size=9, radius=9,
            visible="!ThisItem.Hdr && %s > 0" % cnt,
            extra={"Fill": "If(%s, cOnJcb, cJcbWash)" % act, "Color": "cJcb", "PaddingLeft": 0, "PaddingRight": 0,
                   "HoverFill": "cJcb", "HoverColor": "cOnJcb"}),
    ]
    nav = [
        rect("navBg" + K, 0, 57, 224, 711, "cGlass"),
        rect("navLn" + K, 223, 57, 1, 711, "cLine"),
        gallery("navGal" + K, 0, 64, 224, 696,
                'Sort(Filter(nfNav, Role = If(gRole = "Lab Lead", "Lab Admin", gRole)), Seq)', 40, navrow,
                onselect="If(!ThisItem.Hdr, %s)" % nav_switch(), extra={"ShowScrollbar": "false"}),
    ]
    body = box("body" + K, 224, 57, 1142, 711, content, fill="cClear", border="cClear", thick=0, auto=True,
               gap=16, pad=26, scroll=True)
    root = box("root" + K, 0, 0, 1366, 768, backdrop(K) + hdr + nav + [body] + (extra_root or []), fill="cBg",
               border="cBg", thick=0)
    SCREENS.append((scr, nav_key, root))
    return root


def lines_status_expr(qty, avail, found):
    return 'If(!%s, "NEW PART", %s <= %s, "AVAILABLE", %s <= 0, "SHORTAGE", "PARTIAL")' % (found, qty, avail, avail)


# =====================================================================  DASHBOARD
def scr_dash():
    K = "Dsh"
    open_n = 'CountRows(Filter(nfReq, Status in ["SUBMITTED", "ADMIN REVIEW", "APPROVED"]))'
    rdy = 'CountRows(Filter(nfReq, Status in ["READY FOR RELEASE", "RESERVED"]))'
    shrt = 'CountRows(Filter(nfReq, Status = "PURCHASE REQUIRED"))'
    out = 'CountRows(Filter(nfStock, Status = "OUT OF STOCK"))'
    low = 'CountRows(Filter(nfStock, Status = "LOW STOCK"))'
    pr_open = 'CountRows(Filter(nfProc, Stage in ["PR RAISED", "APPROVED"]))'
    po_open = 'CountRows(Filter(nfProc, Stage in ["PO RAISED", "GRN IN PROGRESS"]))'
    lic = 'CountRows(Filter(nfLic, Status in ["EXPIRED", "EXPIRING SOON"]))'
    mine = "CountRows(Filter(nfReq, RaisedByEmail = gMeEmail))"
    t1 = tiles("tiA" + K, [
        ("a", "Open requests", open_n, 'If(%s > 0, "waiting for the store", "nothing waiting")' % open_n),
        ("g", "Ready to release", rdy, '"stock held, awaiting collection"'),
        ("r", "Purchase required", shrt, '"shortages needing a PR"'),
        ("r", "Out of stock", out, '"of " & CountRows(nfStock) & " components"'),
        ("w", "Low stock", low, '"below reorder threshold"')], visible=ADMIN)
    t2 = tiles("tiB" + K, [
        ("w", "PRs in progress", pr_open, '"raised, awaiting approval"'),
        ("a", "POs in progress", po_open, '"ordered, awaiting GRN / delivery"'),
        ("r", "Licenses need attention", lic, '"expiring or expired"'),
        ("b", "Stock value", inrs("Sum(nfStock, StockValue)"), '"at last purchase price"')], visible=ADMIN)
    t3 = tiles("tiC" + K, [
        ("a", "My open requests", mine, '"raised by you"'),
        ("", "Components", "CountRows(nfStock)", '"in the lab catalogue"'),
        ("w", "Low stock", low, '"check before you plan a build"'),
        ("r", "Out of stock", out, '"will need purchasing"')], visible="!(%s)" % ADMIN)
    items = ('FirstN(Sort(Filter(nfReqView, If(%s, !(Status in ["COMPLETED", "CANCELLED"]), RaisedByEmail = gMeEmail)), '
             'DateRaised, SortOrder.Descending), 8)' % ADMIN)
    req = card("cdReq" + K, 'If(%s, "Needs Your Action", "Your Requests")' % ADMIN, 420, table("rq" + K, items, [
        Col("Request", 150, "ThisItem.RequestNo", "mono"),
        Col("Harness", 150, "ThisItem.HarnessPartNo", "mono"),
        Col("Requester", 190, "ThisItem.RaisedByName"),
        Col("Lines", 70, "ThisItem.Lines", align="Right"),
        Col("Short", 70, "ThisItem.ShortLines", align="Right",
            color="If(ThisItem.ShortLines > 0, cStop, cInk)"),
        Col("", 30, '""'),
        Col("Status", 190, "ThisItem.Status", "pill"),
        Col("Submitted", None, fdate("ThisItem.DateRaised"), "mono")],
        h=374, row_h=40, onrow='Set(gReqNo, ThisItem.RequestNo); Navigate(scrReqDetail, ScreenTransition.None)',
        empty="Nothing here yet",
        empty_sub='When an engineer submits a BOM it lands here.'),
        right=[btn("cdReqGo" + K, '"Open all"', "Parent.Width - 112", 9, 96, 28,
                   'If(%s, Navigate(scrQueue, ScreenTransition.None), Navigate(scrMyReq, ScreenTransition.None))' % ADMIN,
                   kind="secondary", size=10)], title_is_formula=True)
    np = card("cdNp" + K, "Need something the lab does not stock?", 150, [
        lbl("cdNpT" + K, '"If the part has never been bought before it will not show up in Check Stock or BOM '
                         'Compare. Raise it here and the store turns it into a purchase request."',
            16, 58, 900, 40, size=12, color="cInk3", wrap=True, valign="Top"),
        btn("cdNpB" + K, '"BRAND NEW PURCHASE PART"', 16, 100, 240, 34,
            "Navigate(scrNewPart, ScreenTransition.None)")], visible="!(%s)" % ADMIN)
    lowitems = 'FirstN(Sort(Filter(nfStock, Status in ["OUT OF STOCK", "LOW STOCK"]), OnHand), 10)'
    lowc = card("cdLow" + K, "Low and out of stock", 470, table("lo" + K, lowitems, [
        Col("Part", 190, "ThisItem.PartNo", "mono"),
        Col("Description", 300, "ThisItem.Description"),
        Col("Location", 120, 'Coalesce(ThisItem.Location, "—")', "mono"),
        Col("On hand", 130, None, "custom", make=lambda n, x, w, h: meter(n, x, 18, 56, "ThisItem.OnHand",
            "ThisItem.RefQty") + [lbl(n, num("ThisItem.OnHand"), x + 60, 0, w - 68, h, size=12, align="Right")]),
        Col("Reserved", 80, num("ThisItem.Reserved"), align="Right"),
        Col("Available", 90, num("ThisItem.Avail"), align="Right", bold=True),
        Col("Status", None, "ThisItem.Status", "pill")], h=424, row_h=38, empty="All parts are above threshold"),
        right=[btn("cdLowGo" + K, '"Full inventory"', "Parent.Width - 132", 9, 116, 28,
                   "Navigate(scrInventory, ScreenTransition.None)", kind="secondary", size=10)], visible=ADMIN)
    content = [head(K, '"DASHBOARD"', 'gRole & " view · " & Text(Today(), "dd-mmm-yyyy")'), t1, t2, t3, req, np, lowc]
    shell(K, "scrDash", "dash", content)


# =====================================================================  MANAGER DASHBOARD
def scr_mgr():
    K = "Mgr"
    low = 'CountRows(Filter(nfStock, Status in ["LOW STOCK", "OUT OF STOCK"]))'
    lic = 'CountRows(Filter(nfLic, Status in ["EXPIRED", "EXPIRING SOON"]))'
    cal_due = 'CountRows(Filter(nfCalib, !IsBlank(Days) && Days < 0))'
    cal_soon = 'CountRows(Filter(nfCalib, !IsBlank(Days) && Days >= 0 && Days <= 30))'
    t = tiles("ti" + K, [
        ("b", "Materials tracked", "CountRows(nfStock)", num("Sum(nfStock, Max(0, OnHand))") + ' & " units in stock"'),
        ("a", "Software licenses", "CountRows(nfLic)", '"products tracked"'),
        ("w", "Low / out of stock", low, '"below reorder threshold"'),
        ("g", "Invoices issued", "CountRows(nfInv)", '"deliveries billed"'),
        ("If(%s > 0, cStop, cLine2)" % cal_due, "Calibration due",
         'If(CountRows(nfCalib) = 0, "—", Text(%s + %s))' % (cal_due, cal_soon),
         'If(CountRows(nfCalib) = 0, "Not set up yet", %s & " overdue, " & %s & " within 30 days")'
         % (cal_due, cal_soon)),
        ("If(%s > 0, cStop, cLine2)" % lic, "Expiring licenses", lic, '"within 45 days or expired"')])
    pie = ('"data:image/svg+xml;utf8," & EncodeUrl("<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'182\' height=\'182\' '
           'viewBox=\'0 0 182 182\'>" & If(nfRevTotal <= 0, '
           '"<circle cx=\'91\' cy=\'91\' r=\'89\' fill=\'#24272d\' stroke=\'#31353c\'/>'
           '<text x=\'91\' y=\'95\' text-anchor=\'middle\' fill=\'#71767e\' font-size=\'12\' '
           'font-family=\'Segoe UI,sans-serif\'>no data yet</text>", '
           'Concat(ForAll(Sequence(CountRows(nfRevByBU)) As I, With({r: Index(nfRevByBU, I.Value), '
           'a0: -Pi() / 2 + 2 * Pi() * Sum(FirstN(nfRevByBU, I.Value - 1), V) / nfRevTotal}, '
           'With({a1: a0 + 2 * Pi() * r.V / nfRevTotal}, {s: If(r.V / nfRevTotal > 0.999, '
           '"<circle cx=\'91\' cy=\'91\' r=\'89\' fill=\'" & r.Col & "\'/>", '
           '"<path d=\'M 91 91 L " & Text(91 + 89 * Cos(a0), "0.00", "en-US") & " " & Text(91 + 89 * Sin(a0), "0.00", "en-US") & '
           '" A 89 89 0 " & If(r.V / nfRevTotal > 0.5, "1", "0") & " 1 " & Text(91 + 89 * Cos(a1), "0.00", "en-US") & " " & '
           'Text(91 + 89 * Sin(a1), "0.00", "en-US") & " Z\' fill=\'" & r.Col & "\' stroke=\'#1d1f24\' stroke-width=\'1\'/>")}))), s) & '
           '"<circle cx=\'91\' cy=\'91\' r=\'48\' fill=\'#1d1f24\'/>") & "</svg>")')
    leg_row = [
        rect("lgSw" + K, 0, 9, 10, 10, "ColorValue(ThisItem.Col)"),
        lbl("lgK" + K, "ThisItem.K", 18, 0, 150, 28, size=11, color="cInk2"),
        lbl("lgV" + K, inrs("ThisItem.V"), 170, 0, 90, 28, size=11, color="cInk", align="Right"),
        lbl("lgP" + K, 'Text(If(nfRevTotal > 0, ThisItem.V / nfRevTotal * 100, 0), "0") & "%"', 262, 0, 44, 28,
            size=11, color="cInk3", align="Right", font=MONO)]
    rev = card("cdRev" + K, "Revenue", 300, [
        pill("revTot" + K, "Parent.Width - 120", 12, 104, inrs("nfRevTotal")),
        img("revPie" + K, 16, 62, 182, 182, pie),
        gallery("revLg" + K, 220, 62, 310, 190, "nfRevByBU", 28, leg_row),
        lbl("revNone" + K, '"Nothing invoiced yet."', 220, 62, 300, 24, size=12, color="cInk3",
            visible="CountRows(nfRevByBU) = 0"),
        lbl("revNote" + K, '"Every invoice the lab has issued, split by business unit."', 16, 258, 500, 24, size=11,
            color="cInk3")])
    bar_row = [
        lbl("brK" + K, "ThisItem.K", 0, 0, 90, 36, size=11, bold=True, color="cInk2"),
        rect("brBg" + K, 100, 12, 330, 12, "cSunk", extra={"BorderColor": "cLine", "BorderThickness": 1}),
        rect("brFg" + K, 100, 12, "330 * Max(0.02, ThisItem.V / Max(1, Max(nfProcBars, V)))", 12, "ThisItem.C"),
        lbl("brV" + K, "ThisItem.V", 440, 0, 60, 36, size=13, bold=True, align="Right"),
        rect("brSep" + K, 0, 35, 500, 1, "cLine")]
    proc = card("cdPr" + K, "Ongoing Purchases (PR/PO) Status", 300, [
        pill("prOpen" + K, "Parent.Width - 120", 12, 104, 'CountRows(nfProc) & " open"'),
        gallery("prBars" + K, 16, 64, 510, 116, "nfProcBars", 36, bar_row),
        lbl("prNote" + K, '"Number of purchase requests at each stage. Released PO value so far: " & ' + inrs(
            "Sum(nfProc, POAmount)") + ' & "."', 16, 196, 500, 40, size=11, color="cInk3", wrap=True, valign="Top")])
    split1 = box("sp1" + K, None, None, None, 300, [rev, proc], fill="RGBA(0,0,0,0)", border="RGBA(0,0,0,0)",
                 thick=0, auto=True, direction="Horizontal", gap=16, extra={"FillPortions": 0, "LayoutMinHeight": 300})
    rev.props["FillPortions"] = 1
    proc.props["FillPortions"] = 1
    dl = card("cdDel" + K, "Deliveries", 170, [
        lbl("delN" + K, num("CountRows(nfInv)"), 16, 58, 300, 56, size=34, bold=True, color="cJcb"),
        lbl("delS" + K, '"Total invoices generated, all periods. Worth " & ' + inrs("nfRevTotal") + ' & " in total."',
            16, 116, 480, 40, size=11, color="cInk3", wrap=True, valign="Top")])
    pj = card("cdPj" + K, "Projects", 170, [
        lbl("pjK1" + K, '"Ongoing Projects"', 16, 56, 300, 26, size=13, bold=True),
        lbl("pjV1" + K, "nfOngoing", 380, 56, 120, 26, size=18, bold=True, align="Right", color="cJcb"),
        lbl("pjS1" + K, '"Part requests received and still moving"', 16, 80, 400, 20, size=10, color="cInk3"),
        lbl("pjK2" + K, '"Upcoming Projects"', 16, 108, 300, 26, size=13, bold=True),
        lbl("pjV2" + K, "nfUpcoming", 380, 108, 120, 26, size=18, bold=True, align="Right", color="cJcb"),
        lbl("pjS2" + K, '"Requests with material reserved or waiting on a PR"', 16, 132, 400, 20, size=10,
            color="cInk3")])
    dl.props["FillPortions"] = 1
    pj.props["FillPortions"] = 1
    split2 = box("sp2" + K, None, None, None, 170, [dl, pj], fill="RGBA(0,0,0,0)", border="RGBA(0,0,0,0)",
                 thick=0, auto=True, direction="Horizontal", gap=16, extra={"FillPortions": 0, "LayoutMinHeight": 170})
    cal = card("cdCal" + K, "Calibration — due and overdue", 330, table("cl" + K, "FirstN(nfCalibDue, 20)", [
        Col("Asset", 140, "ThisItem.AssetNo", "mono"),
        Col("Name", 300, "ThisItem.AssetName"),
        Col("Location", 160, "ThisItem.Location"),
        Col("Due", 120, fdate("ThisItem.DueDate"), "mono"),
        Col("Days", 120, 'If(ThisItem.Days < 0, "overdue " & Abs(ThisItem.Days), Text(ThisItem.Days))',
            align="Right", bold=True, color="If(ThisItem.Days < 0, cStop, cWarn)"),
        Col("Owner", None, "ThisItem.Owner")], h=284,
        empty="Nothing due in the next 30 days"), visible="CountRows(nfCalib) > 0")
    cal0 = card("cdCal0" + K, "Calibration", 130, [
        lbl("cal0T" + K, '"Calibration tracking is not set up yet. Ask the Lab Admin to add one row per instrument (asset, last '
                         'calibration date, interval, due date) and this card starts working. '
                         'Until then it shows a dash rather than a zero, so an empty list is never mistaken for nothing is due."',
            16, 56, 1040, 64, size=11, color="cInk3", wrap=True, valign="Top")], visible="CountRows(nfCalib) = 0")
    pend_r = 'CountRows(Filter(nfReq, Status in ["SUBMITTED", "ADMIN REVIEW"]))'
    pend_n = 'CountRows(Filter(nfNewPart, Status = "SUBMITTED"))'
    pend_p = 'CountRows(Filter(nfProc, Stage = "PR RAISED"))'
    appr = card("cdAp" + K, '"Waiting for Your Approval (" & (%s + %s + %s) & ")"' % (pend_r, pend_n, pend_p), 330, [
        btn("apR" + K, '"Material Requests:  " & %s' % pend_r, 16, 58, 250, 36, "Navigate(scrQueue, ScreenTransition.Fade)",
            kind="secondary", size=10, radius=18),
        btn("apN" + K, '"Brand New Parts:  " & %s' % pend_n, 278, 58, 250, 36, "Navigate(scrNewPartQ, ScreenTransition.Fade)",
            kind="secondary", size=10, radius=18),
        btn("apP" + K, '"Purchase Requests (PR):  " & %s' % pend_p, 540, 58, 270, 36,
            "Navigate(scrProc, ScreenTransition.Fade)", kind="secondary", size=10, radius=18)]
        + table("ap" + K, 'Sort(Filter(nfReqView, Status in ["SUBMITTED", "ADMIN REVIEW"]), DateRaised)', [
            Col("Request", 150, "ThisItem.RequestNo", "mono"),
            Col("Requester", 180, "ThisItem.RaisedByName"),
            Col("Harness", 150, "ThisItem.HarnessPartNo", "mono"),
            Col("Machine", 140, "ThisItem.Machine"),
            Col("Lines", 60, "ThisItem.Lines", align="Right"),
            Col("", 20, '""'),
            Col("Status", 150, "ThisItem.Status", "pill"),
            Col("Raised", None, fdate("ThisItem.DateRaised"), "mono")], y=106, h=210, row_h=40,
            onrow='Set(gReqNo, ThisItem.RequestNo); Set(gShortSr, -1); Navigate(scrReqDetail, ScreenTransition.Fade)',
            empty="Nothing waiting for approval", empty_sub="Open a request to approve or reject it."),
        title_is_formula=True)
    content = [head(K, '"Dashboard"', '"Live overview of electrical and controls inventory, spend and delivery"'),
               t, appr, split1, split2, cal, cal0]
    shell(K, "scrMgrDash", "dash", content)


# =====================================================================  CHECK STOCK
def stock_table(K, items, admin_edit=False, h=520):
    cols = [Col("Part", 166, "ThisItem.PartNo", "mono"),
            Col("Description", 236, "ThisItem.Description"),
            Col("Sub Category", 110, "ThisItem.SubCategory", "muted")]
    if admin_edit:
        def loc(n, x, w, rh):
            return [inp(n, x, 6, w - 40, rh - 12, default="ThisItem.Location", hint="—", size=11, font=MONO,
                        visible=ADMIN),
                    icon(n + "Sv", x + w - 38, 6, 30, rh - 12, "Save", color="cJcb", visible=ADMIN,
                         tooltip="Save location to the parts catalogue",
                         onselect='Patch(tblParts, LookUp(tblParts, Upper(Trim(Text(PartNo))) = ThisItem.PN), '
                                  '{Location: Trim(%s.Text)}); Notify(ThisItem.PartNo & " is now at " & '
                                  'Coalesce(Trim(%s.Text), "—") & ".", NotificationType.Success)' % (n, n)),
                    lbl(n + "Ro", 'Coalesce(ThisItem.Location, "—")', x, 0, w - 8, rh, size=11, font=MONO,
                        visible="!(%s)" % ADMIN)]
        cols.append(Col("Store Location", 160, None, "custom", make=loc))
    else:
        cols.append(Col("Location", 110, 'Coalesce(ThisItem.Location, "—")', "mono"))
    cols += [Col("On Hand", 100, None, "custom", make=lambda n, x, w, rh: meter(n, x, 18, 40, "ThisItem.OnHand",
                 "ThisItem.RefQty") + [lbl(n, num("ThisItem.OnHand"), x + 42, 0, w - 48, rh, size=12, align="Right")]),
             Col("Resv", 50, num("ThisItem.Reserved"), align="Right", color="cInk2"),
             Col("Avail", 60, num("ThisItem.Avail"), align="Right", bold=True),
             Col("UOM", 46, "ThisItem.UOM", "muted"),
             Col("Status", None, "ThisItem.Status", "pill")]
    return table("st" + K, items, cols, y=0, h=h, row_h=42, empty="Nothing matches",
                 empty_sub="Try a different search or filter.")


def stock_filters(K, quality=False):
    kids = [inp("q" + K, 0, 0, 330, 36, hint="Part number, description or location"),
            dd("c" + K, 344, 0, 220, 36, prepend('"All Categories"', "nfCategories")),
            dd("s" + K, 578, 0, 200, 36, '["Any Status", "In Stock", "Low Stock", "Out of Stock", "Fully Reserved"]')]
    if quality:
        kids.append(dd("dq" + K, 792, 0, 200, 36, '["Any Data Quality", "OK", "With Issues"]'))
    return kids


def stock_items(K, quality=False):
    f = ('With({s: Upper(Trim(q%s.Text)), c: c%s.Selected.Value, st: s%s.Selected.Value}, '
         'Filter(nfStock, (IsBlank(s) || s in PN || s in Upper(Description) || s in Upper(Location)) && '
         '(c = "All Categories" || Category = c) && (st = "Any Status" || Status = Upper(st))' % (K, K, K))
    if quality:
        f += ' && (dq%s.Selected.Value = "Any Data Quality" || (dq%s.Selected.Value = "OK") = IsBlank(Quality))' % (K, K)
    return f + "))"


def scr_stock():
    K = "Stk"
    items = stock_items(K)
    content = [head(K, '"CHECK STOCK"', '"Search the catalogue by part number or description"'),
               sec("flt" + K, 36, stock_filters(K) + [
                   lbl("cnt" + K, 'CountRows(stStkGal.AllItems) & " of " & CountRows(nfStock) & " components"',
                       800, 0, 290, 36, size=11, color="cInk3", align="Right")]),
               sec("tb" + K, 560, stock_table(K, items, h=560), fill="cPanel", border="cLine", thick=1)]
    shell(K, "scrStock", "stock", content)


def scr_inventory():
    K = "Inv"
    items = stock_items(K, quality=True)
    add_kids = []
    fx = [("apPn", "Part number", 0, True), ("apDs", "Description", 1, True), ("apCt", "Category", 2, True),
          ("apSc", "Sub Category", 3, False), ("apUm", "UOM (NO / M / KG)", 4, True), ("apLc", "Location", 5, False),
          ("apSp", "Supplier", 6, False), ("apUc", "Unit cost", 7, False), ("apRq", "Reorder ref qty", 8, False)]
    for nm, label, i, req in fx:
        col, row = i % 3, i // 3
        num_ = nm in ("apUc", "apRq")
        add_kids += field(nm + K, label, 16 + col * 356, 60 + row * 60, 340,
                          lambda n, x, y, w, h, num_=num_: inp(n, x, y, w, h, number=num_,
                                                               default='"NO"' if n.startswith("apUm") else '""'),
                          req=req)
    save_add = ('With({pn: Trim(apPn%(K)s.Text)}, If(IsBlank(pn) || IsBlank(Trim(apDs%(K)s.Text)) || IsBlank(Trim(apCt%(K)s.Text)), '
                'Notify("Part number, description and category are required.", NotificationType.Error), '
                '!IsBlank(LookUp(tblParts, Upper(Trim(Text(PartNo))) = Upper(pn))), '
                'Notify(pn & " is already in the catalogue.", NotificationType.Error), '
                'Collect(tblParts, {PartNo: pn, Description: Trim(apDs%(K)s.Text), Category: Trim(apCt%(K)s.Text), '
                'SubCategory: Trim(apSc%(K)s.Text), UOM: Coalesce(Trim(apUm%(K)s.Text), "NO"), Location: Trim(apLc%(K)s.Text), '
                'Supplier: Trim(apSp%(K)s.Text), UnitCost: Coalesce(Value(apUc%(K)s.Text), 0), '
                'ReorderRefQty: Coalesce(Value(apRq%(K)s.Text), 0), Active: "Yes", Notes: "Added in Power Apps by " & gMeName}); '
                'Notify(pn & " added. Stock starts at zero - record a receipt in Material Inward.", NotificationType.Success); '
                'Set(gPanel, ""); Reset(apPn%(K)s); Reset(apDs%(K)s)))' % {"K": K})
    add_kids += [btn("apGo" + K, '"Add part"', "Parent.Width - 140", 250, 124, 34, save_add),
                 btn("apNo" + K, '"Cancel"', "Parent.Width - 260", 250, 110, 34, 'Set(gPanel, "")', kind="secondary")]
    addp = card("cdAdd" + K, "Add a New Component to the Catalogue", 300, add_kids,
                visible='gPanel = "addpart" && %s' % ADMIN)
    retire = card("cdRet" + K, "Retire a component", 120, [
        lbl("rtT" + K, '"Retiring hides the part from stock lists. Its transaction history is kept; the part just stops '
                       'appearing in stock lists. Type the exact part number:"', 16, 54, 700, 40, size=11,
            color="cInk3", wrap=True, valign="Top"),
        inp("rtPn" + K, 740, 60, 200, 34, hint="Part number", font=MONO),
        btn("rtGo" + K, '"Retire"', "Parent.Width - 112", 60, 96, 34,
            'With({r: LookUp(tblParts, Upper(Trim(Text(PartNo))) = Upper(Trim(rtPn%s.Text)))}, If(IsBlank(r), '
            'Notify("No such part.", NotificationType.Error), Patch(tblParts, r, {Active: "No"}); '
            'Notify(Trim(rtPn%s.Text) & " retired.", NotificationType.Success); Set(gPanel, "")))' % (K, K),
            kind="danger")], visible='gPanel = "retire" && %s' % ADMIN)
    content = [head(K, '"COMPONENT INVENTORY"',
                    'CountRows(nfStock) & " components · stock is calculated from the transaction ledger, never typed"',
                    right=[btn("add" + K, '"+ Add part"', "Parent.Width - 236", 8, 110, 30, 'Set(gPanel, "addpart")',
                               visible=ADMIN, size=10),
                           btn("ret" + K, '"Retire part"', "Parent.Width - 116", 8, 110, 30, 'Set(gPanel, "retire")',
                               kind="secondary", visible=ADMIN, size=10)]),
               addp, retire,
               sec("flt" + K, 36, stock_filters(K, quality=True)),
               sec("cnt" + K, 18, [lbl("cntL" + K, 'CountRows(stInvGal.AllItems) & " of " & CountRows(nfStock) & " components"',
                                       0, 0, 600, 18, size=11, color="cInk3")]),
               sec("tb" + K, 560, stock_table(K, items, admin_edit=True, h=560), fill="cPanel", border="cLine", thick=1)]
    shell(K, "scrInventory", "inventory", content)


# =====================================================================  BOM COMPARE
def bom_parse(src):
    """Same rule as the HTA parseBom: one line per part, part number first, quantity last,
    tab / comma / semicolon / spaces between. Header rows have no numeric qty and drop out."""
    return ('With({raw: Filter(ForAll(Split(Substitute(%s, Char(13), ""), Char(10)) As L, '
            'With({t: TrimEnds(Substitute(Substitute(Substitute(L.Value, Char(9), " "), ",", " "), ";", " "))}, '
            'With({qt: Last(Split(t, " ")).Value}, {PN: Upper(TrimEnds(Left(t, Len(t) - Len(qt)))), '
            'Q: IfError(Value(qt), 0)}))), !IsBlank(PN) && Q > 0)}, '
            'ForAll(Distinct(raw, PN) As D, {PN: D.Value, Q: Sum(Filter(raw, PN = D.Value), Q)}))' % src)


def scr_bom():
    K = "Bom"
    sample_set = "Set(gBomText, nfSampleBom); Reset(txt%s)" % K
    compare = (REFRESH_STOCK + '; With({rows: %s}, ClearCollect(colBom, ForAll(Sequence(CountRows(rows)) As I, '
               'With({B: Index(rows, I.Value)}, With({p: LookUp(nfStock, PN = B.PN)}, '
               '{Sr: I.Value, PartNo: Coalesce(p.PartNo, B.PN), PN: B.PN, Qty: B.Q, '
               'Description: Coalesce(p.Description, "— not in the lab catalogue —"), UOM: Coalesce(p.UOM, ""), '
               'Location: Coalesce(p.Location, "—"), OnHand: Coalesce(p.OnHand, 0), Reserved: Coalesce(p.Reserved, 0), '
               'Avail: Coalesce(p.Avail, 0), UnitCost: Coalesce(p.UnitCost, 0), '
               'Short: If(IsBlank(p), B.Q, Max(0, Round(B.Q - p.Avail, 3))), '
               'Status: If(IsBlank(p), "NEW PART", B.Q <= p.Avail, "AVAILABLE", p.Avail <= 0, "OUT OF STOCK", "SHORTAGE"), '
               'Found: !IsBlank(p)}))))); '
               'If(CountRows(colBom) = 0, Notify("Paste at least one line with a part number and a quantity.", '
               'NotificationType.Warning), Notify("Compared " & CountRows(colBom) & " lines with live stock as of " & '
               'Text(gLastSync, "hh:mm:ss") & ".", NotificationType.Success))' % bom_parse("txt%s.Text" % K))
    paste = card("cdP" + K, "1 · Paste your BOM", 250, [
        inp("txt" + K, 16, 62, "Parent.Width - 32", 120, default="gBomText", mode="multi", font=MONO,
            hint="7219/0373  20  (part number, then quantity — select the two columns in Excel, Ctrl+C, click here, Ctrl+V)"),
        btn("go" + K, '"COMPARE AGAINST STOCK"', 16, 196, 220, 36, compare),
        btn("smp" + K, '"LOAD A SAMPLE HARNESS"', 248, 196, 210, 36, sample_set, kind="secondary"),
        btn("clr" + K, '"CLEAR"', 470, 196, 90, 36, 'Set(gBomText, ""); Reset(txt%s); Clear(colBom)' % K, kind="secondary"),
        lbl("hint" + K, '"Tab, comma or multiple spaces all work as the separator."', 576, 196, 500, 36, size=11,
            color="cInk3")])
    has = "CountRows(colBom) > 0"
    t = tiles("ti" + K, [
        ("", "Lines", "CountRows(colBom)", '"in this BOM"'),
        ("g", "Available", 'CountRows(Filter(colBom, Status = "AVAILABLE"))', '"can be issued today"'),
        ("r", "Short", 'CountRows(Filter(colBom, Status in ["SHORTAGE", "OUT OF STOCK"]))', '"not enough in store"'),
        ("b", "New parts", 'CountRows(Filter(colBom, Status = "NEW PART"))', '"not in the catalogue at all"'),
        ("a", "Estimated material", inrs("Sum(colBom, Qty * UnitCost)"), '"at last purchase price"')], visible=has)
    res = card("cdR" + K, "2 · Comparison", 520, table("cmp" + K, "colBom", [
        Col("#", 40, "ThisItem.Sr", "muted"),
        Col("Part number", 170, "ThisItem.PartNo", "mono"),
        Col("Description", 250, "ThisItem.Description"),
        Col("Req", 60, num("ThisItem.Qty"), align="Right"),
        Col("On hand", 70, 'If(ThisItem.Found, %s, "—")' % num("ThisItem.OnHand"), align="Right"),
        Col("Resv", 56, 'If(ThisItem.Found, %s, "—")' % num("ThisItem.Reserved"), align="Right", color="cInk2"),
        Col("Avail", 60, 'If(ThisItem.Found, %s, "—")' % num("ThisItem.Avail"), align="Right", bold=True),
        Col("Short", 60, num("ThisItem.Short"), align="Right", color="If(ThisItem.Short > 0, cStop, cInk)", bold=True),
        Col("UOM", 46, "ThisItem.UOM", "muted"),
        Col("Loc", 80, "ThisItem.Location", "mono"),
        Col("Status", None, "ThisItem.Status", "pill")], h=430, row_h=40) + [
        lbl("note" + K, '"A new part is not the same as an out-of-stock part. New means the lab has never carried it and '
                        'the store must create it first."', 16, 478, 900, 36, size=11, color="cInk3", wrap=True)],
        right=[btn("req" + K, '"Raise part request ›"', "Parent.Width - 196", 9, 180, 28,
                   "Navigate(scrNewReq, ScreenTransition.None)", visible='gRole <> "Manager"', size=10)],
        visible=has)
    content = [head(K, '"BOM COMPARE"', '"Paste two columns from Excel — part number and quantity — and see instantly '
                                         'what the lab can supply"'), paste, t, res]
    shell(K, "scrBom", "bom", content)


# =====================================================================  NEW REQUEST
def scr_newreq():
    K = "Nr"
    empty = card("cdE" + K, "Load a BOM first", 170, [
        lbl("eT" + K, '"Go to BOM Compare, paste your harness BOM, then come back — the lines carry across so you '
                      'never type them twice."', 16, 60, 900, 40, size=12, color="cInk3", wrap=True, valign="Top"),
        btn("eB" + K, '"Go to BOM Compare"', 16, 108, 200, 36, "Navigate(scrBom, ScreenTransition.None)")],
        visible="CountRows(colBom) = 0")
    has = "CountRows(colBom) > 0"
    f = []
    cw = 345

    def ti(hint, number=False):
        return lambda n, x, y, w, h: inp(n, x, y, w, h, hint=hint, number=number)
    f += field("mach" + K, "Machine / variant", 16, 60, cw, ti("3CX 74KW"), req=True)
    f += field("pcode" + K, "Project code", 16 + 360, 60, cw, ti("PCODE-00042"), req=True)
    f += field("harn" + K, "Harness part number", 16 + 720, 60, cw, ti("405/F8525"), req=True)
    f += field("stage" + K, "Build stage", 16, 122, cw,
               lambda n, x, y, w, h: dd(n, x, y, w, h, '["Mule", "DVP", "Proto", "PPAP", "Production"]'), req=True)
    f += field("bu" + K, "Business unit", 16 + 360, 122, cw,
               lambda n, x, y, w, h: dd(n, x, y, w, h, '["BHL India", "Excavator", "Loadall", "Compaction"]'), req=True)
    f += field("cc" + K, "Cost centre / BU", 16 + 720, 122, cw, ti("IDC00005"), req=True)
    f += field("buc" + K, "Business unit contact", 16, 184, 525, ti("Shashank G"), req=True)
    f += field("dcc" + K, "DC contact", 16 + 540, 184, 525, ti("Mahendra M"), req=True)
    f += field("circ" + K, "No. of circuits", 16, 246, 525, ti("48", number=True), req=True)
    f += field("need" + K, "Required by", 16 + 540, 246, 525, lambda n, x, y, w, h: date(n, x, y, w, h), req=True)
    f += [lbl("scopeLb" + K, '"Scope of Work *"', 16, 308, 400, 16, size=10, color="cInk2", semibold=True),
          inp("scope" + K, 16, 326, "Parent.Width - 32", 90, mode="multi",
              hint="Feature name, component change, add or delete, old concept vs new concept.",
              extra={"MaxLength": 1800}),
          lbl("scnt" + K, 'Len(scope%s.Text) & " / 1800 characters"' % K, 16, 418, 300, 18, size=10, color="cInk3")]
    info = card("cdI" + K, "1 · Project information", 450, f, visible=has)
    submit = (
        'With({miss: Concat(Filter(Table('
        '{n: "Machine / variant", v: mach%(K)s.Text}, {n: "Project code", v: pcode%(K)s.Text}, '
        '{n: "Harness part number", v: harn%(K)s.Text}, {n: "Cost centre", v: cc%(K)s.Text}, '
        '{n: "Business unit contact", v: buc%(K)s.Text}, {n: "DC contact", v: dcc%(K)s.Text}, '
        '{n: "No. of circuits", v: circ%(K)s.Text}, {n: "Scope of work", v: scope%(K)s.Text}), IsBlank(Trim(v))), n, ", ")}, '
        'If(!IsBlank(miss), Notify(miss & " is required before this can be submitted.", NotificationType.Error), '
        'IsBlank(need%(K)s.SelectedDate), Notify("Required by needs a valid date.", NotificationType.Error), '
        'IfError(Value(circ%(K)s.Text), 0) <= 0, Notify("No. of circuits must be a number above zero - the cost sheet runs on it.", NotificationType.Error), '
        'Set(gBusy, true); '
        'With({no: "REQ-" & nfYearPfx & "-" & Text(nfNextReqSeq, "00000")}, '
        'Collect(tblRequests, {RequestNo: no, Kind: "", Status: "SUBMITTED", '
        'RaisedByEmail: gMeEmail, RaisedByName: gMeName, DateRaised: %(NOON)s, Machine: Trim(mach%(K)s.Text), '
        'ProjectCode: Trim(pcode%(K)s.Text), HarnessPartNo: Trim(harn%(K)s.Text), BuildStage: stage%(K)s.Selected.Value, '
        'BusinessUnit: Upper(bu%(K)s.Selected.Value), CostCentre: Trim(cc%(K)s.Text), BUContact: Trim(buc%(K)s.Text), '
        'DCContact: Trim(dcc%(K)s.Text), NoOfCircuits: Value(circ%(K)s.Text), RequiredBy: %(NEED)s, '
        'ScopeOfWork: Trim(scope%(K)s.Text), ParentRequest: "", LastUpdated: Text(Now(), "yyyy-mm-ddThh:mm:ss"), '
        'LastUpdatedBy: gMeName, History: "[" & JSON({t: Text(Now(), "yyyy-mm-ddThh:mm:ss"), by: gMeName, '
        'a: "Submitted with " & CountRows(colBom) & " lines"}, JSONFormat.Compact) & "]"}); '
        'ForAll(colBom As B, Collect(tblReqLines, {RequestNo: no, Sr: B.Sr, PartNo: B.PartNo, Description: B.Description, '
        'QtyRequested: B.Qty, QtyReserved: 0, QtyReleased: 0, UOM: B.UOM, '
        'LineStatus: If(!B.Found, "NEW PART", B.Qty <= B.Avail, "AVAILABLE", B.Avail <= 0, "SHORTAGE", "PARTIAL"), '
        'UnitCost: B.UnitCost, StoreLocation: If(B.Location = "—", "", B.Location), Remarks: ""})); '
        'Notify(no & " is with the store. You will see it move through the stages on My Requests.", NotificationType.Success); '
        'Clear(colBom); Set(gBomText, ""); Set(gBusy, false); Navigate(scrMyReq, ScreenTransition.None))))'
        % {"K": K, "NOON": noon(), "NEED": noon("need%s.SelectedDate" % K)})
    sh = 'CountRows(Filter(colBom, Status <> "AVAILABLE"))'
    bom = card("cdB" + K, '"2 · BOM — " & CountRows(colBom) & " lines" & If(%s > 0, ", " & %s & " need purchasing", "")'
               % (sh, sh), 420, table("bl" + K, "colBom", [
                   Col("#", 44, "ThisItem.Sr", "muted"),
                   Col("Part", 200, "ThisItem.PartNo", "mono"),
                   Col("Description", 380, "ThisItem.Description"),
                   Col("Qty", 80, num("ThisItem.Qty"), align="Right"),
                   Col("Avail", 80, 'If(ThisItem.Found, %s, "—")' % num("ThisItem.Avail"), align="Right"),
                   Col("", 20, '""'),
                   Col("Status", None, "ThisItem.Status", "pill")], h=310, row_h=38) + [
                   btn("back" + K, '"Back"', "Parent.Width - 300", 366, 120, 38, "Navigate(scrBom, ScreenTransition.None)",
                       kind="secondary"),
                   btn("sub" + K, '"Submit request"', "Parent.Width - 168", 366, 152, 38, submit, disabled=BUSY)],
               right=[btn("edit" + K, '"Edit BOM"', "Parent.Width - 112", 9, 96, 28,
                          "Navigate(scrBom, ScreenTransition.None)", kind="secondary", size=10)],
               visible=has, title_is_formula=True)
    content = [head(K, '"NEW REQUEST"', '"Project details, then the BOM. Both are needed before the store can act."'),
               empty, info, bom]
    shell(K, "scrNewReq", "newreq", content)


# =====================================================================  MY REQUESTS / QUEUE
STATUSES = disp_list('["SUBMITTED", "ADMIN REVIEW", "APPROVED", "PURCHASE REQUIRED", "RESERVED", "READY FOR RELEASE", '
                     '"PARTIALLY RELEASED", "RELEASED", "COMPLETED", "CANCELLED", "REJECTED"]', "All Statuses")


def req_list_screen(K, scr, nav_key, title, sub, base, show_req=True, oldest_first=False):
    items = ('With({f: st%(K)s.Selected.Value, s: Upper(Trim(q%(K)s.Text))}, Sort(Filter(%(B)s, '
             '(f = "All Statuses" || Status = Upper(f)) && (IsBlank(s) || s in Upper(RequestNo & " " & HarnessPartNo & " " & '
             'Machine & " " & RaisedByName & " " & ProjectCode))), DateRaised, SortOrder.%(O)s))'
             % {"K": K, "B": base, "O": "Ascending" if oldest_first else "Descending"})
    cols = [Col("Request", 150, "ThisItem.RequestNo", "mono", sub='If(ThisItem.Kind = "SHORTAGE", "shortfall of " & '
                                                                   'ThisItem.ParentRequest, ThisItem.ProjectCode)')]
    if show_req:
        cols.append(Col("Requester", 150, "ThisItem.RaisedByName"))
    cols += [Col("Harness", 130, "ThisItem.HarnessPartNo", "mono"),
             Col("Machine", 120, "ThisItem.Machine"),
             Col("Stage", 80, "ThisItem.BuildStage", "muted"),
             Col("Lines", 54, "ThisItem.Lines", align="Right"),
             Col("Short", 54, "ThisItem.ShortLines", align="Right", bold=True,
                 color="If(ThisItem.ShortLines > 0, cStop, cInk)"),
             Col("", 16, '""'),
             Col("Status", 170, "ThisItem.Status", "pill"),
             Col("Raised", None, fdate("ThisItem.DateRaised"), "mono")]
    content = [head(K, title, sub),
               sec("flt" + K, 36, [dd("st" + K, 0, 0, 230, 36, STATUSES),
                                   inp("q" + K, 244, 0, 420, 36, hint="Search request, harness, machine or requester"),
                                   lbl("cnt" + K, 'CountRows(rl%sGal.AllItems) & " requests"' % K, 680, 0, 410, 36,
                                       size=11, color="cInk3", align="Right")]),
               sec("tb" + K, 560, table("rl" + K, items, cols, y=0, h=560, row_h=46,
                                        onrow='Set(gReqNo, ThisItem.RequestNo); Set(gShortSr, -1); '
                                              'Navigate(scrReqDetail, ScreenTransition.None)',
                                        empty="No requests yet",
                                        empty_sub="Check a BOM first, then raise a request from the comparison screen."),
                   fill="cPanel", border="cLine", thick=1)]
    shell(K, scr, nav_key, content)


def scr_myreq():
    req_list_screen("My", "scrMyReq", "myreq", '"MY REQUESTS"', '"Everything you have raised, and where it has got to. '
                    'Click a row for line-by-line progress and the history log."',
                    "Filter(nfReqView, RaisedByEmail = gMeEmail)", show_req=False)


def scr_queue():
    req_list_screen("Qu", "scrQueue", "queue", 'If(%s, "All Requests", "Request Queue")' % MGR,
                    'If(%s, "Read-only view of everything in flight", "Oldest first. Open a request to reserve or '
                    'release material.")' % MGR, "nfReqView", oldest_first=True)


# =====================================================================  REQUEST DETAIL (reserve / release)
def scr_reqdetail():
    K = "Rd"
    R = "LookUp(nfReq, RequestNo = gReqNo)"
    canact = ADMIN
    mine = "(%s.RaisedByEmail = gMeEmail)" % R
    st = "%s.Status" % R
    circ_in = inp("circ" + K, 186, 58 + 6 * 30, 110, 26, default="Text(%s.NoOfCircuits)" % R, number=True,
                  visible=canact, size=11)
    circ_sv = btn("circSv" + K, '"Save"', 304, 58 + 6 * 30, 64, 26,
                  'Patch(tblRequests, LookUp(tblRequests, Text(RequestNo) = gReqNo), {NoOfCircuits: Coalesce(Value(circ%s.Text), 0), '
                  'LastUpdated: Text(Now(), "yyyy-mm-ddThh:mm:ss"), LastUpdatedBy: gMeName, History: %s}); '
                  'Notify("Circuit count saved as " & circ%s.Text & ".", NotificationType.Success)'
                  % (K, hist("gReqNo", '"Set circuit count to " & circ%s.Text' % K), K),
                  kind="secondary", visible=canact, size=10)
    kvrows = [
        ("Status", Ctl("stP" + K, "Label@2.5.1")),   # placeholder replaced below
        ("Requester", '%s.RaisedByName & " · " & %s.RaisedByEmail' % (R, R)),
        ("Harness / machine", '%s.HarnessPartNo & " · " & %s.Machine' % (R, R)),
        ("Project / stage", '%s.ProjectCode & " · " & %s.BuildStage' % (R, R)),
        ("Business unit", '%s.BusinessUnit & " · cost centre " & %s.CostCentre' % (R, R)),
        ("Contacts", '"BU: " & %s.BUContact & " · DC: " & %s.DCContact' % (R, R)),
        ("No. of circuits", 'If(%s, "", Text(%s.NoOfCircuits))' % (canact, R)),
        ("Required by", fdate("%s.RequiredBy" % R)),
        ("Scope of work", "%s.ScopeOfWork" % R)]
    kvk = kv("kv" + K, kvrows, 16, 58, 1050)
    kvk = [k for k in kvk if k.name != "stP" + K]
    kvk += [pill("stP" + K, 186, 62, 190, st),
            lbl("stK" + K, '"Shortfall of " & %s.ParentRequest' % R, 386, 62, 300, 22, size=9, color="cSteel",
                font=MONO, visible='%s.Kind = "SHORTAGE"' % R),
            circ_in, circ_sv,
            lbl("circN" + K, '"feeds the cost sheet"', 378, 58 + 6 * 30, 200, 26, size=10, color="cInk3", visible=canact)]
    info = card("cdK" + K, "Request", 340, kvk)

    # ---- BOM lines
    def part_cell(n, x, w, rh):
        return [lbl(n, "ThisItem.PartNo", x, 6, w - 8, 20, size=11, font=MONO),
                lbl(n + "d", "ThisItem.Description", x, 26, w - 8, 18, size=10, color="cInk3")]

    def loc_cell(n, x, w, rh):
        cur = 'Coalesce(ThisItem.StoreLocation, LookUp(nfParts, PN = ThisItem.PN).Location)'
        return [inp(n, x, 9, w - 40, 30, default=cur, hint="—", size=11, font=MONO, visible=canact),
                icon(n + "Sv", x + w - 38, 9, 30, 30, "Save", color="cJcb", visible=canact,
                     tooltip="Save store location (this line and the parts catalogue)",
                     onselect='Patch(tblReqLines, LookUp(tblReqLines, Text(RequestNo) = gReqNo && Value(Text(Sr)) = ThisItem.Sr), '
                              '{StoreLocation: Trim(%s.Text)}); If(!IsBlank(LookUp(tblParts, Upper(Trim(Text(PartNo))) = ThisItem.PN)), '
                              'Patch(tblParts, LookUp(tblParts, Upper(Trim(Text(PartNo))) = ThisItem.PN), {Location: Trim(%s.Text)})); '
                              'Notify(ThisItem.PartNo & " is now at " & Coalesce(Trim(%s.Text), "—") & ".", NotificationType.Success)'
                              % (n, n, n)),
                lbl(n + "r", cur, x, 0, w - 8, rh, size=11, font=MONO, visible="!(%s)" % canact)]

    gap = "Max(0, ThisItem.QtyRequested - Max(ThisItem.QtyReserved, ThisItem.QtyReleased))"

    def status_cell(n, x, w, rh):
        return [pill(n, x, 6, w - 8, "ThisItem.LineStatus"),
                btn(n + "b", '"Request separately"', x, 30, w - 8, 18,
                    'Set(gShortSr, ThisItem.Sr)', kind="secondary", size=8,
                    visible="%s > 0 && (%s || %s) && !(%s in nfDeadStatus)" % (gap, mine, canact, st))]

    def rel_cell(n, x, w, rh):
        pend = "(ThisItem.QtyReserved - ThisItem.QtyReleased)"
        return [inp(n, x, 9, w - 8, 30, default="Text(%s)" % pend, number=True, size=11,
                    visible="%s && %s > 0 && %s in nfHoldStatus" % (canact, pend, st)),
                lbl(n + "x", '"—"', x, 0, w - 8, rh, color="cInk3",
                    visible="!(%s && %s > 0 && %s in nfHoldStatus)" % (canact, pend, st))]
    cols = [Col("Part", 190, None, "custom", make=part_cell),
            Col("Store location", 150, None, "custom", make=loc_cell),
            Col("Req", 56, num("ThisItem.QtyRequested"), align="Right"),
            Col("Avail", 60, 'If(IsBlank(LookUp(nfStock, PN = ThisItem.PN)), "—", %s)' %
                num("LookUp(nfStock, PN = ThisItem.PN).Avail + Max(0, ThisItem.QtyReserved - ThisItem.QtyReleased)"),
                align="Right", color="cInk2"),
            Col("Resv", 56, num("ThisItem.QtyReserved"), align="Right"),
            Col("Rel", 56, num("ThisItem.QtyReleased"), align="Right", bold=True),
            Col("Short", 60, num(gap), align="Right", bold=True, color="If(%s > 0, cStop, cInk3)" % gap),
            Col("", 12, '""'),
            Col("Status", 170, None, "custom", make=status_cell),
            Col("Release now", None, None, "custom", make=rel_cell)]
    linetbl = table("ln" + K, "Sort(Filter(nfLines, RequestNo = gReqNo), Sr)", cols, h=330, row_h=52)

    # ---- actions
    reserve = (
        'Set(gBusy, true); '
        'With({calc: ForAll(Filter(nfLines, RequestNo = gReqNo) As L, With({p: LookUp(nfStock, PN = L.PN)}, '
        'With({take: If(IsBlank(p), 0, Max(0, Min(p.Avail, L.QtyRequested - L.QtyReserved)))}, '
        '{Sr: L.Sr, PN: L.PN, PartNo: L.PartNo, Desc: L.Description, Req: L.QtyRequested, NewResv: L.QtyReserved + take, '
        'Gap: L.QtyRequested - (L.QtyReserved + take), '
        'St: If(IsBlank(p), "NEW PART", L.QtyReserved + take >= L.QtyRequested, "AVAILABLE", '
        'L.QtyReserved + take > 0, "PARTIAL", "SHORTAGE")})))}, '
        'ForAll(calc As C, Patch(tblReqLines, LookUp(tblReqLines, Text(RequestNo) = gReqNo && Value(Text(Sr)) = C.Sr), '
        '{QtyReserved: C.NewResv, LineStatus: C.St})); '
        'With({got: CountRows(Filter(calc, St = "AVAILABLE")), part: CountRows(Filter(calc, St = "PARTIAL")), '
        'nsh: CountRows(Filter(calc, St in ["SHORTAGE", "NEW PART"]))}, '
        'Patch(tblRequests, LookUp(tblRequests, Text(RequestNo) = gReqNo), {Status: If(part + nsh > 0, "PURCHASE REQUIRED", '
        '"READY FOR RELEASE"), LastUpdated: Text(Now(), "yyyy-mm-ddThh:mm:ss"), LastUpdatedBy: gMeName, '
        'History: %(H1)s}); '
        '%(PURCH)s; '
        'Notify(got & " line(s) fully reserved" & If(part + nsh > 0, ", " & (part + nsh) & " still short - added to '
        'Ongoing Purchase", "") & ".", NotificationType.Success))); Set(gBusy, false)'
        % {"H1": hist("gReqNo", '"Reserved stock — " & got & " full, " & part & " partial, " & nsh & " short"'),
           "PURCH": purch_add("Filter(calc, Gap > 0)")})
    release = (
        'With({req: %(R)s, calc: ForAll(lnRdGal.AllItems As G, With({qq: IfError(Value(G.lnRdC9.Text), 0), '
        'pend: G.QtyReserved - G.QtyReleased, onh: Coalesce(LookUp(nfStock, PN = G.PN).OnHand, 0)}, '
        '{Sr: G.Sr, PN: G.PN, PartNo: G.PartNo, Desc: G.Description, Req: G.QtyRequested, Resv: G.QtyReserved, '
        'Rel: G.QtyReleased, Cost: G.UnitCost, St: G.LineStatus, Q: If(pend > 0, qq, 0), Gap: G.QtyRequested - G.QtyReserved, '
        'Ok: pend > 0 && qq > 0 && qq <= pend && qq <= onh, Bad: pend > 0 && qq > 0 && (qq > pend || qq > onh)}))}, '
        'If(CountRows(Filter(calc, Bad)) > 0, Notify("Line " & First(Filter(calc, Bad)).PartNo & ": you can release at most '
        'what is reserved for it and what is physically on the shelf.", NotificationType.Error), '
        'CountRows(Filter(calc, Ok)) = 0, Notify("Enter a quantity to release on at least one line.", NotificationType.Warning), '
        'Set(gBusy, true); '
        'ForAll(Filter(calc, Ok) As C, Collect(tblMoves, {Date: %(NOON)s, PartNo: C.PartNo, Type: "ISSUE", Qty: C.Q, '
        'Reference: gReqNo, UnitCost: C.Cost, By: gMeEmail, Reason: "Issued to " & req.RaisedByName & " for " & '
        'req.HarnessPartNo, EntryId: "TXN-" & Text(GUID())})); '
        'ForAll(Filter(calc, Ok) As C, Patch(tblReqLines, LookUp(tblReqLines, Text(RequestNo) = gReqNo && Value(Text(Sr)) = C.Sr), '
        '{QtyReleased: C.Rel + C.Q, LineStatus: If(C.Rel + C.Q >= C.Req, "RELEASED", C.St)})); '
        'With({allRel: CountRows(Filter(calc, Rel + If(Ok, Q, 0) < Req)) = 0, n: CountRows(Filter(calc, Ok))}, '
        'Patch(tblRequests, LookUp(tblRequests, Text(RequestNo) = gReqNo), {Status: If(allRel, "RELEASED", "PARTIALLY RELEASED"), '
        'LastUpdated: Text(Now(), "yyyy-mm-ddThh:mm:ss"), LastUpdatedBy: gMeName, History: %(H2)s}); '
        '%(PURCH)s; '
        'Notify(n & " line(s) issued. Stock is reduced by exactly that quantity.", NotificationType.Success)); '
        'Set(gBusy, false)))'
        % {"R": R, "NOON": noon(), "H2": hist("gReqNo", '"Released material on " & n & " line(s)"'),
           "PURCH": purch_add("Filter(calc, Gap > 0)")})
    simple = lambda status, msg, nt: (
        'Patch(tblRequests, LookUp(tblRequests, Text(RequestNo) = gReqNo), {Status: "%s", LastUpdated: '
        'Text(Now(), "yyyy-mm-ddThh:mm:ss"), LastUpdatedBy: gMeName, History: %s}); Notify(gReqNo & "%s", '
        'NotificationType.%s)' % (status, hist("gReqNo", q(status.title())), msg, nt))
    acts = [
        btn("rej" + K, '"Reject"', 16, 12, 110, 36, simple("REJECTED", " rejected. The requester keeps the record.",
                                                          "Warning"), kind="danger",
            visible='%s && %s in ["SUBMITTED", "ADMIN REVIEW"]' % (APPROVER, st), disabled=BUSY),
        btn("apr" + K, '"Approve"', 136, 12, 130, 36, simple("APPROVED", " approved. The store can now reserve and release it.",
                                                            "Success"),
            visible='%s && %s in ["SUBMITTED", "ADMIN REVIEW"]' % (APPROVER, st), disabled=BUSY),
        btn("res" + K, '"Reserve available stock"', "Parent.Width - 236", 12, 220, 36, reserve,
            visible='%s && %s in ["SUBMITTED", "ADMIN REVIEW", "APPROVED", "PURCHASE REQUIRED", "PARTIALLY RELEASED"]' % (canact, st),
            disabled=BUSY),
        btn("rel" + K, '"RELEASE"', "Parent.Width - 392", 12, 140, 36, release,
            visible='%s && %s in nfHoldStatus' % (canact, st), disabled=BUSY),
        btn("inv" + K, '"Create invoice"', "Parent.Width - 568", 12, 160, 36,
            'Set(gInvEdit, ""); Set(gInvReq, gReqNo); Navigate(scrInvoice, ScreenTransition.None)', kind="secondary",
            visible='%s && %s in ["RELEASED", "PARTIALLY RELEASED", "COMPLETED"]' % (canact, st)),
        btn("cmp" + K, '"Mark completed"', "Parent.Width - 196", 12, 180, 36,
            simple("COMPLETED", " closed.", "Success"), visible='%s && %s = "RELEASED"' % (canact, st), disabled=BUSY),
        lbl("hint" + K, 'If(%s, "Reserve first, then type the quantity physically leaving the shelf in Release now.", '
                        '%s, "Approved requests go to the store, which reserves and releases the material.", '
                        '"Read-only. The store reserves and releases material from here.")' % (canact, MGR),
            16, 12, 480, 36, size=11, color="cInk3", wrap=True,
            visible='!(%s && %s in ["SUBMITTED", "ADMIN REVIEW"])' % (APPROVER, st)),
    ]
    lines = card("cdL" + K, "BOM lines", 440, linetbl + [box("act" + K, 0, 380, "Parent.Width", 60, acts, fill="cPanel2",
                                                             border="cLine")])

    # ---- shortfall panel
    sline = "LookUp(nfLines, RequestNo = gReqNo && Sr = gShortSr)"
    sgap = "Max(0, %s.QtyRequested - Max(%s.QtyReserved, %s.QtyReleased))" % (sline, sline, sline)
    sf_submit = (
        'With({no: "SHT-" & nfYearPfx & "-" & Text(nfNextReqSeq, "00000"), r: %(R)s, pn: Upper(Trim(sfPn%(K)s.Text)), '
        'qn: IfError(Value(sfQ%(K)s.Text), 0), note: Trim(sfN%(K)s.Text)}, '
        'If(IsBlank(pn), Notify("Part number is required.", NotificationType.Error), '
        'qn <= 0, Notify("Quantity must be more than zero.", NotificationType.Error), '
        'With({p: LookUp(nfStock, PN = pn), sl: %(SL)s}, '
        'Collect(tblRequests, {RequestNo: no, Kind: "SHORTAGE", Status: "SUBMITTED", '
        'RaisedByEmail: r.RaisedByEmail, RaisedByName: r.RaisedByName, DateRaised: %(NOON)s, Machine: r.Machine, '
        'ProjectCode: r.ProjectCode, HarnessPartNo: r.HarnessPartNo, BuildStage: r.BuildStage, BusinessUnit: r.BusinessUnit, '
        'CostCentre: r.CostCentre, BUContact: r.BUContact, DCContact: r.DCContact, NoOfCircuits: r.NoOfCircuits, '
        'RequiredBy: %(NEED)s, ScopeOfWork: "Shortfall from " & gReqNo & " — " & pn & " x " & qn & If(IsBlank(note), "", ". " & note), '
        'ParentRequest: gReqNo, LastUpdated: Text(Now(), "yyyy-mm-ddThh:mm:ss"), LastUpdatedBy: gMeName, '
        'History: "[" & JSON({t: Text(Now(), "yyyy-mm-ddThh:mm:ss"), by: gMeName, a: "Raised as a shortfall of " & gReqNo}, '
        'JSONFormat.Compact) & "]"}); '
        'Collect(tblReqLines, {RequestNo: no, Sr: 1, PartNo: Coalesce(p.PartNo, pn), '
        'Description: Coalesce(p.Description, sl.Description, "New part — not in the catalogue"), QtyRequested: qn, '
        'QtyReserved: 0, QtyReleased: 0, UOM: Coalesce(p.UOM, sl.UOM, "NO"), '
        'LineStatus: If(IsBlank(p), "NEW PART", qn <= p.Avail, "AVAILABLE", p.Avail <= 0, "SHORTAGE", "PARTIAL"), '
        'UnitCost: Coalesce(p.UnitCost, 0), StoreLocation: Coalesce(p.Location, ""), Remarks: note}); '
        'Patch(tblReqLines, LookUp(tblReqLines, Text(RequestNo) = gReqNo && Value(Text(Sr)) = gShortSr), '
        '{Remarks: "Shortfall of " & qn & " raised separately as " & no}); '
        'Patch(tblRequests, LookUp(tblRequests, Text(RequestNo) = gReqNo), {LastUpdated: Text(Now(), "yyyy-mm-ddThh:mm:ss"), '
        'LastUpdatedBy: gMeName, History: %(H)s}); '
        'Notify(no & " is with the store. " & gReqNo & " can be released without it.", NotificationType.Success); '
        'Set(gShortSr, -1))))'
        % {"R": R, "K": K, "SL": sline, "NOON": noon(), "NEED": "r.RequiredBy",
           "H": hist("gReqNo", '"Shortfall of " & pn & " x " & qn & " raised separately as " & no')})
    sf = card("cdSf" + K, "Request the shortfall separately", 230, [
        lbl("sfT" + K, '"This raises a separate request for the part that could not be given, so the rest of " & gReqNo & '
                       '" can be released without waiting. It goes to the store for approval."', 16, 54, 1000, 36,
            size=11, color="cInk3", wrap=True, valign="Top")]
        + field("sfPn" + K, "Part number", 16, 96, 340, lambda n, x, y, w, h: inp(n, x, y, w, h, default="%s.PartNo" % sline,
                                                                                 font=MONO), req=True)
        + field("sfQ" + K, "Quantity still needed", 372, 96, 200,
                lambda n, x, y, w, h: inp(n, x, y, w, h, default="Text(%s)" % sgap, number=True), req=True)
        + field("sfN" + K, "Note for the store", 588, 96, 486,
                lambda n, x, y, w, h: inp(n, x, y, w, h, hint="Optional — when you need it, or an alternative you would accept"))
        + [btn("sfNo" + K, '"Cancel"', "Parent.Width - 330", 170, 120, 36, "Set(gShortSr, -1)", kind="secondary"),
           btn("sfGo" + K, '"Submit to store"', "Parent.Width - 196", 170, 180, 36, sf_submit)],
        visible="gShortSr >= 0")

    # ---- history
    hist_items = ('IfError(With({tb: ForAll(Table(ParseJSON(%s.History)) As H, {t: Text(H.Value.t), by: Text(H.Value.by), '
                  'a: Text(H.Value.a)})}, ForAll(Sequence(CountRows(tb)) As I, Index(tb, CountRows(tb) - I.Value + 1))), '
                  'Table({t: "", by: "", a: ""}))' % R)
    hrow = [lbl("hT" + K, 'Substitute(Left(ThisItem.t, 16), "T", " ")', 0, 0, 150, 26, size=11, color="cInk3", font=MONO),
            lbl("hB" + K, "ThisItem.by", 156, 0, 180, 26, size=11, color="cInk2"),
            lbl("hA" + K, "ThisItem.a", 340, 0, 700, 26, size=11, color="cInk")]
    hc = card("cdH" + K, "History", 260, [gallery("hg" + K, 16, 56, "Parent.Width - 32", 190,
                                                  'Filter(%s, !IsBlank(a))' % hist_items, 26, hrow),
                                          lbl("hE" + K, '"No history recorded yet."', 16, 56, 400, 26, size=11,
                                              color="cInk3", visible="CountRows(hg%s.AllItems) = 0" % K)])
    content = [head(K, 'gReqNo & " · " & %s.HarnessPartNo' % R, '"Request detail — line-by-line progress, actions and history"',
                    right=[btn("bk" + K, '"‹ Back"', "Parent.Width - 112", 8, 100, 30,
                               'If(%s, Navigate(scrQueue, ScreenTransition.None), Navigate(scrMyReq, ScreenTransition.None))'
                               % ADMIN, kind="secondary", size=10)]),
               info, sf, lines, hc]
    shell(K, "scrReqDetail", "queue", content)


def purch_add(rows):
    """Every line still short after a reserve/release lands on Ongoing Purchase (once per part + request)."""
    return ('ForAll(%s As G, With({ex: LookUp(tblPurch, Upper(Trim(Text(PartNo))) = G.PN && Text(RequestNo) = gReqNo)}, '
            'If(IsBlank(ex), Collect(tblPurch, {PartNo: G.PartNo, Description: G.Desc, QtyRequired: G.Gap, QtyConfirmed: 0, '
            'RequestNo: gReqNo, RaisedBy: gMeName, PRNumber: "", SupplierNo: "", SupplierName: "", Stage: "REQUIRED", '
            'DateRaised: %s, Notes: LookUp(nfReq, RequestNo = gReqNo).RaisedByName & " waiting"}), '
            'Upper(Text(ex.Stage)) = "REQUIRED", Patch(tblPurch, ex, {QtyRequired: G.Gap}))))'
            % (rows, noon()))


# =====================================================================  BRAND NEW PURCHASE PART
NPCOLS = [("RequesterName", "Requester Name", True, 150), ("Category", "Category", True, 130),
          ("SubCategory", "Sub Category", False, 130), ("PlantCode", "Plant Code", True, 92),
          ("PartName", "Part / Machine Name", True, 250), ("MakeBrand", "Make / Brand", False, 130),
          ("ModelNo", "Model No.", False, 130), ("OtherSpecs", "Other Specs", False, 170),
          ("Remarks", "Remarks", False, 160), ("UOM", "UOM", True, 78), ("HSNCode", "8-Digit HSN", True, 112)]
NP_BLANK = ('{Id: 0, RequesterName: gMeName, Category: "", SubCategory: "", PlantCode: "", PartName: "", '
            'MakeBrand: "", ModelNo: "", OtherSpecs: "", Remarks: "", UOM: "NO", HSNCode: ""}')
UOMS = '["NO", "M", "KG", "EACH", "SET", "PAIR", "ROLL", "BOX", "LTR"]'


def scr_newpart():
    """One clear form per part (labels above every box), an 'Add to List' step, then one Submit for the list.
    v1 used a grid of unlabeled boxes inside a gallery, which was hard to read and lost typing on submit."""
    K = "Np"
    # form layout: (field, label, required, column, row, width-in-columns, hint)
    form = [("RequesterName", "Requester Name", True, 0, 0, 1, "Your name"),
            ("PlantCode", "Plant Code", True, 1, 0, 1, "5040"),
            ("Category", "Category", True, 2, 0, 1, "Electrical, Mechanical, Tool…"),
            ("PartName", "Part / Machine Name", True, 0, 1, 1, "Relay 24 V 40 A"),
            ("SubCategory", "Sub Category", False, 1, 1, 1, "Relay, Connector, Sensor… (if applicable)"),
            ("MakeBrand", "Make / Brand", False, 2, 1, 1, "Bosch, TE, Phoenix… (if applicable)"),
            ("ModelNo", "Model No.", False, 0, 2, 1, "If applicable"),
            ("UOM", "UOM", True, 1, 2, 1, ""),
            ("HSNCode", "8-Digit HSN", True, 2, 2, 1, "85366990"),
            ("OtherSpecs", "Other Specs", False, 0, 3, 2, "Size, weight, colour, rating (if applicable)"),
            ("Remarks", "Remarks", False, 2, 3, 1, "If applicable")]
    cw, gx = 340, 356
    kids = [lbl("fmHint" + K, '"Fields marked * are mandatory. Add each part to the list, then submit the whole list once."',
                16, 50, 900, 20, size=10, color="cInk3")]
    f_of = {}
    for fld_, label, req, col, row, span, hint in form:
        n = "npf%s%s" % (fld_, K)
        f_of[fld_] = n
        x, y, w = 16 + col * gx, 76 + row * 62, cw + (span - 1) * gx
        if fld_ == "UOM":
            kids += field(n, label, x, y, w, lambda nn, xx, yy, ww, hh: dd(nn, xx, yy, ww, hh, UOMS,
                                                                          default="gNpForm.UOM"), req=req)
        else:
            kids += field(n, label, x, y, w, lambda nn, xx, yy, ww, hh, fld_=fld_, hint=hint: inp(
                nn, xx, yy, ww, hh, default="gNpForm.%s" % fld_, hint=hint,
                extra={"MaxLength": 8} if fld_ == "HSNCode" else None), req=req)
    val = {f: ("Trim(%s.Text)" % n if f != "UOM" else "%s.Selected.Value" % n) for f, n in f_of.items()}
    rec = "{" + ", ".join("%s: %s" % (f, val[f]) for f, _, _, _ in NPCOLS) + "}"
    resets = "; ".join("Reset(%s)" % n for n in f_of.values())
    miss = ", ".join('{n: "%s", v: r.%s}' % (t, f) for f, t, rq, _ in NPCOLS if rq)
    add = ('With({r: %(REC)s}, With({miss: Concat(Filter(Table(%(MISS)s), IsBlank(v)), n, ", ")}, '
           'If(!IsBlank(miss), Notify("Please fill in " & miss & ". These are mandatory.", NotificationType.Error), '
           'Len(r.HSNCode) <> 8 || CountRows(Filter(Split(r.HSNCode, ""), !(Value in "0123456789"))) > 0, Notify("8-Digit HSN must be exactly 8 digits, for example 85366990.", '
           'NotificationType.Error), '
           'Collect(colNP, {Id: If(gNpForm.Id > 0, gNpForm.Id, Coalesce(Max(colNP, Id), 0) + 1), '
           'RequesterName: r.RequesterName, Category: r.Category, SubCategory: r.SubCategory, PlantCode: r.PlantCode, '
           'PartName: r.PartName, MakeBrand: r.MakeBrand, ModelNo: r.ModelNo, OtherSpecs: r.OtherSpecs, '
           'Remarks: r.Remarks, UOM: r.UOM, HSNCode: r.HSNCode}); '
           'Notify(r.PartName & " is on the list (" & CountRows(colNP) & " so far). Add the next part or submit the list.", '
           'NotificationType.Success); '
           'Set(gNpForm, %(BLANK)s); %(RESETS)s)))'
           % {"REC": rec, "MISS": miss, "BLANK": NP_BLANK, "RESETS": resets})
    kids += [btn("fmAdd" + K, 'If(gNpForm.Id > 0, "Update Part in List", "Add to List")', "Parent.Width - 196", 330, 180, 40,
                 add),
             btn("fmClr" + K, '"Clear Form"', "Parent.Width - 336", 330, 128, 40,
                 "Set(gNpForm, %s); %s" % (NP_BLANK, resets), kind="secondary"),
             lbl("fmEd" + K, '"Editing row " & gNpForm.Id & ". Press Update Part in List to put it back."', 16, 330, 600, 40,
                 size=11, color="cJcb", visible="gNpForm.Id > 0")]
    formc = card("cdF" + K, "1 · Part Details", 390, kids)

    req_checks = ", ".join('{n: "%s", v: r.%s}' % (t, f) for f, t, rq, _ in NPCOLS if rq)
    submit = (
        'With({live: Filter(colNP, !IsBlank(Trim(PartName)))}, '
        'With({bad: Filter(ForAll(Sequence(CountRows(live)) As I, With({r: Index(live, I.Value)}, '
        '{Row: I.Value, Miss: Concat(Filter(Table(%s), IsBlank(Trim(v))), n, ", ")})), !IsBlank(Miss))}, '
        'If(CountRows(live) = 0, Notify("Add at least one part to the list before submitting.", NotificationType.Error), '
        'CountRows(bad) > 0, Notify("Row " & First(bad).Row & " is missing " & First(bad).Miss & ", which is mandatory.", '
        'NotificationType.Error), '
        'Set(gBusy, true); '
        'With({no: "NPR-" & nfYearPfx & "-" & Text(nfNextNprSeq, "00000")}, '
        'ForAll(Sequence(CountRows(live)) As I, With({r: Index(live, I.Value)}, Collect(tblNewPart, '
        '{SrNo: I.Value, RequestNo: no, RequesterName: r.RequesterName, Category: r.Category, SubCategory: r.SubCategory, '
        'PlantCode: r.PlantCode, PartName: r.PartName, MakeBrand: r.MakeBrand, ModelNo: r.ModelNo, OtherSpecs: r.OtherSpecs, '
        'Remarks: r.Remarks, UOM: r.UOM, HSNCode: r.HSNCode, Status: "SUBMITTED", DateRaised: %s}))); '
        'Notify(no & " submitted with " & CountRows(live) & " part(s). The store will raise the purchase request.", '
        'NotificationType.Success); '
        'Clear(colNP); Set(gNpForm, %s); Set(gBusy, false)))))'
        % (req_checks, noon(), NP_BLANK))
    edit = ('Set(gNpForm, ThisItem); Remove(colNP, ThisItem); %s; '
            'Notify("Row " & ThisItem.Id & " is back in the form above for editing.", NotificationType.Information)' % resets)

    def acts(n, x, w, rh):
        return [icon(n, x, 7, 30, 30, "Edit", color="cJcb", onselect=edit, tooltip="Edit this part", pad=6),
                icon(n + "x", x + 34, 7, 30, 30, "Cancel", color="cStop", onselect="Remove(colNP, ThisItem)",
                     tooltip="Remove this part from the list", pad=6)]
    listc = card("cdL" + K, '"2 · Parts in This Request (" & CountRows(colNP) & ")"', 380, table("nl" + K, "Sort(colNP, Id)", [
        Col("#", 36, "ThisItem.Id", "muted"),
        Col("Part / Machine Name", 230, "ThisItem.PartName", bold=True, sub="ThisItem.OtherSpecs"),
        Col("Category", 160, "ThisItem.Category", sub="ThisItem.SubCategory"),
        Col("Plant", 70, "ThisItem.PlantCode", "mono"),
        Col("Make / Model", 160, "ThisItem.MakeBrand", sub="ThisItem.ModelNo"),
        Col("UOM", 56, "ThisItem.UOM"),
        Col("HSN", 96, "ThisItem.HSNCode", "mono"),
        Col("Requester", None, "ThisItem.RequesterName", "muted"),
        Col("", 76, None, "custom", make=acts)], h=264, row_h=44, empty="No parts on the list yet",
        empty_sub="Fill in the form above and press Add to List.") + [
        btn("clr" + K, '"Clear List"', "Parent.Width - 336", 322, 128, 40, "Clear(colNP)", kind="secondary",
            disabled="CountRows(colNP) = 0"),
        btn("go" + K, '"Submit to Store"', "Parent.Width - 196", 322, 180, 40, submit,
            disabled="CountRows(colNP) = 0 || gBusy")], title_is_formula=True)
    mine = card("cdM" + K, "3 · Your New Part Requests", 300, table(
        "nm" + K, 'Sort(Filter(nfNewPart, Lower(RequesterName) = Lower(gMeName)), DateRaised, SortOrder.Descending)', [
            Col("Request", 150, "ThisItem.RequestNo", "mono", sub='"Row " & ThisItem.SrNo'),
            Col("Part / Machine Name", 300, "ThisItem.PartName"),
            Col("Category", 170, "ThisItem.Category"),
            Col("HSN", 110, "ThisItem.HSNCode", "mono"),
            Col("Status", 150, "ThisItem.Status", "pill"),
            Col("Raised", None, fdate("ThisItem.DateRaised"), "mono")], h=240, row_h=42,
        empty="Nothing raised yet", empty_sub="Parts you submit appear here with their approval status."))
    content = [head(K, '"Brand New Purchase Part"', '"Ask the lab to buy a part it has never stocked. '
                                                     'One form per part, any number of parts, one submission."'),
               formc, listc, mine]
    shell(K, "scrNewPart", "newpart", content)


def scr_newpartq():
    K = "Nq"

    def approve(n, x, w, rh):
        return [btn(n, '"Approve"', x, 9, 70, 28,
                    'Patch(tblNewPart, LookUp(tblNewPart, Text(RequestNo) = ThisItem.RequestNo && Value(Text(SrNo)) = ThisItem.SrNo), '
                    '{Status: "APPROVED"}); Notify("Row approved. Add it to the catalogue once it has a part number.", '
                    'NotificationType.Success)', visible='%s && ThisItem.Status = "SUBMITTED"' % APPROVER, size=10),
                btn(n + "r", '"Reject"', x + 74, 9, 56, 28,
                    'Patch(tblNewPart, LookUp(tblNewPart, Text(RequestNo) = ThisItem.RequestNo && Value(Text(SrNo)) = ThisItem.SrNo), '
                    '{Status: "REJECTED"}); Notify("Row rejected.", NotificationType.Warning)', kind="danger",
                    visible='%s && ThisItem.Status = "SUBMITTED"' % APPROVER, size=10)]
    items = ('With({s: Upper(Trim(q%s.Text)), f: st%s.Selected.Value}, Sort(Filter(nfNewPart, (f = "All" || Status = Upper(f)) && '
             '(IsBlank(s) || s in Upper(RequestNo & " " & RequesterName & " " & PartName & " " & MakeBrand & " " & HSNCode))), '
             'DateRaised, SortOrder.Descending))' % (K, K))
    cols = [Col("Request", 120, "ThisItem.RequestNo", "mono", sub='"Sr " & ThisItem.SrNo'),
            Col("Requester", 100, "ThisItem.RequesterName"),
            Col("Part / Machine", 140, "ThisItem.PartName", sub="ThisItem.OtherSpecs"),
            Col("Category", 100, 'ThisItem.Category & If(IsBlank(ThisItem.SubCategory), "", " · " & ThisItem.SubCategory)'),
            Col("Plant", 50, "ThisItem.PlantCode", "mono"),
            Col("Make", 90, 'ThisItem.MakeBrand & " " & ThisItem.ModelNo'),
            Col("HSN", 76, "ThisItem.HSNCode", "mono"),
            Col("UOM", 40, "ThisItem.UOM", "muted"),
            Col("Status", 96, "ThisItem.Status", "pill"),
            Col("Raised", 0 or None, fdate("ThisItem.DateRaised"), "mono")]
    cols[-1].w = 96
    cols.append(Col("", None, None, "custom", make=approve))
    content = [head(K, '"NEW PURCHASE PARTS"', '"Parts engineers have asked the lab to buy for the first time."'),
               sec("flt" + K, 36, [dd("st" + K, 0, 0, 200, 36, '["All", "Submitted", "Approved", "Rejected", "Draft"]'),
                                   inp("q" + K, 214, 0, 420, 36, hint="Search request, requester, part, make or HSN")]),
               sec("tb" + K, 560, table("np" + K, items, cols, y=0, h=560, row_h=46, empty="Nothing waiting",
                                        empty_sub="When an engineer submits the Brand New Purchase Part sheet, the rows land here."),
                   fill="cPanel", border="cLine", thick=1)]
    shell(K, "scrNewPartQ", "newpartq", content)


# =====================================================================  MATERIAL INWARD
def scr_inward():
    K = "In"
    P = "LookUp(nfStock, PN = Upper(Trim(pn%s.Text)))" % K
    rec = (
        'With({p: %(P)s, qn: IfError(Value(qty%(K)s.Text), 0), t: Upper(typ%(K)s.Selected.Value)}, '
        'If(IsBlank(p), Notify("That part number is not in the catalogue.", NotificationType.Error), '
        'qn <= 0, Notify("Enter a quantity greater than zero.", NotificationType.Error), '
        't in ["ADJUST+", "ADJUST-", "SCRAP"] && IsBlank(Trim(rsn%(K)s.Text)), '
        'Notify("A reason is required for an adjustment or scrap.", NotificationType.Error), '
        't in ["ADJUST-", "SCRAP"] && qn > p.OnHand, Notify("Only " & p.OnHand & " " & p.UOM & " of " & p.PartNo & '
        '" is physically in store. Cannot remove " & qn & ".", NotificationType.Error), '
        'Set(gBusy, true); '
        'Collect(tblMoves, {Date: %(D)s, PartNo: p.PartNo, Type: If(t in ["PO", "FOC"], "RECEIPT", t), Qty: qn, '
        'Reference: Trim(ref%(K)s.Text), UnitCost: Coalesce(IfError(Value(cost%(K)s.Text), Blank()), p.UnitCost), By: gMeEmail, '
        'Reason: Trim(rsn%(K)s.Text) & If(t = "FOC", If(IsBlank(Trim(rsn%(K)s.Text)), "FOC", " (FOC)"), ""), '
        'EntryId: "TXN-" & Text(GUID())}); '
        'If(!IsBlank(Trim(loc%(K)s.Text)) && Trim(loc%(K)s.Text) <> Coalesce(p.Location, ""), '
        'Patch(tblParts, LookUp(tblParts, Upper(Trim(Text(PartNo))) = p.PN), {Location: Trim(loc%(K)s.Text)})); '
        'Notify("Recorded " & qn & " " & p.UOM & " of " & p.PartNo & ". Stock is now " & '
        '(p.OnHand + If(t in ["ADJUST-", "SCRAP"], -qn, qn)) & ".", NotificationType.Success); '
        'Reset(qty%(K)s); Reset(pn%(K)s); Reset(ref%(K)s); Reset(rsn%(K)s); Reset(cost%(K)s); Reset(loc%(K)s); '
        'Set(gBusy, false)))' % {"P": P, "K": K, "D": noon("dt%s.SelectedDate" % K)})
    f = []
    f += field("pn" + K, "Part number", 16, 60, 520, lambda n, x, y, w, h: inp(n, x, y, w, h, hint="7219/0373", font=MONO),
               req=True)
    f += [lbl("mL" + K, '"Matched Part"', 556, 60, 300, 16, size=10, color="cInk2", semibold=True),
          lbl("m" + K, 'With({p: %s}, If(IsBlank(Trim(pn%s.Text)), "Type a part number on the left.", IsBlank(p), '
                       '"Not in the catalogue. Check the number, or add the part first.", p.Description & "  ·  " & '
                       'p.SubCategory & " · " & p.UOM & " · on hand " & p.OnHand))' % (P, K),
              556, 78, 520, 34, size=12, wrap=True,
              color='If(IsBlank(Trim(pn%s.Text)), cInk3, IsBlank(%s), cWarn, cInk)' % (K, P))]
    f += field("qty" + K, "Quantity received", 16, 124, 340, lambda n, x, y, w, h: inp(n, x, y, w, h, hint="50", number=True),
               req=True)
    f += field("typ" + K, "Reference type", 372, 124, 340,
               lambda n, x, y, w, h: dd(n, x, y, w, h, '["PO", "FOC", "Return", "Adjust+", "Adjust-", "Scrap"]'), req=True)
    f += field("ref" + K, "PO / FOC number", 728, 124, 346, lambda n, x, y, w, h: inp(n, x, y, w, h, hint="9700009778"),
               req=True)
    f += field("cost" + K, "Unit cost", 16, 188, 340, lambda n, x, y, w, h: inp(n, x, y, w, h, number=True,
                                                                               default='If(IsBlank(%s), "", Text(%s.UnitCost))' % (P, P)))
    f += field("dt" + K, "Landing date", 372, 188, 340, lambda n, x, y, w, h: date(n, x, y, w, h), req=True)
    f += field("loc" + K, "Storage location", 728, 188, 346, lambda n, x, y, w, h: inp(n, x, y, w, h, hint="L-5", font=MONO,
                                                                                      default='Coalesce(%s.Location, "")' % P))
    f += field("rsn" + K, "Remarks / reason", 16, 252, 1058, lambda n, x, y, w, h: inp(n, x, y, w, h,
                                                                                     hint="Required for adjustments and scrap"))
    f += [btn("go" + K, '"Record receipt"', "Parent.Width - 196", 318, 180, 38, rec, disabled=BUSY)]
    recv = card("cdR" + K, "Receive material", 372, f)
    recent = ('With({n: CountRows(nfMoves)}, ForAll(Sequence(Min(15, n)) As I, Index(nfMoves, n - I.Value + 1)))')
    rc = card("cdL" + K, "Last 15 movements", 420, table("rc" + K, recent, [
        Col("Date", 120, fdate("ThisItem.Date"), "mono"),
        Col("Part", 220, "ThisItem.PartNo", "mono"),
        Col("Type", 130, "ThisItem.Type", "pill"),
        Col("Qty", 90, 'If(ThisItem.SQty > 0, "+", "") & %s' % num("ThisItem.SQty"), align="Right", bold=True,
            color="If(ThisItem.SQty < 0, cStop, cOk)"),
        Col("", 20, '""'),
        Col("Ref", 200, 'Coalesce(ThisItem.Reference, "—")', "mono"),
        Col("By", None, 'First(Split(ThisItem.By, "@")).Value', "muted")], h=374, row_h=34))
    content = [head(K, '"MATERIAL INWARD"', '"Record what arrived. Stock goes up only through this screen."'), recv, rc]
    shell(K, "scrInward", "inward", content)


# =====================================================================  STOCK TRANSACTIONS (ledger)
def scr_ledger():
    K = "Lg"
    items = ('With({s: Upper(Trim(q%(K)s.Text)), t: Upper(ty%(K)s.Selected.Value), d0: fr%(K)s.SelectedDate, d1: to%(K)s.SelectedDate}, '
             'Filter(nfLedger, (t = "ALL TYPES" || Type = t) && (IsBlank(d0) || Date >= d0) && (IsBlank(d1) || Date <= d1) && '
             '(IsBlank(s) || s in Upper(PartNo & " " & Description & " " & Reference & " " & Harness & " " & Machine & " " & '
             'IssuedTo & " " & IssuedBy & " " & Reason))))' % {"K": K})
    cols = [Col("Date", 96, fdate("ThisItem.Date"), "mono"),
            Col("Part", 150, "ThisItem.PartNo", "mono"),
            Col("Description", 160, "ThisItem.Description", sub="ThisItem.Reason"),
            Col("Harness", 90, 'Coalesce(ThisItem.Harness, "—")', "mono"),
            Col("Machine", 80, 'Coalesce(ThisItem.Machine, "—")'),
            Col("Type", 80, "ThisItem.Type", "pill"),
            Col("Qty", 60, 'If(ThisItem.SQty > 0, "+", "") & %s' % num("ThisItem.SQty"), align="Right", bold=True,
                color="If(ThisItem.SQty < 0, cStop, cOk)"),
            Col("", 8, '""'),
            Col("Issued to", 96, 'Coalesce(ThisItem.IssuedTo, "—")'),
            Col("Issued by", 80, "ThisItem.IssuedBy", "muted"),
            Col("Reference", 90, 'Coalesce(ThisItem.Reference, "—")', "mono"),
            Col("Unit cost", None, 'If(ThisItem.UnitCost > 0, %s, "—")' % inr("ThisItem.UnitCost"), align="Right")]
    content = [head(K, '"STOCK TRANSACTIONS"', 'CountRows(nfMoves) & " movements. Nothing here can be edited or deleted — '
                                               'corrections are new reversing rows."'),
               sec("flt" + K, 36, [inp("q" + K, 0, 0, 380, 36, hint="Part, harness, machine, person or reference"),
                                   dd("ty" + K, 394, 0, 170, 36, '["All Types", "Receipt", "Release", "Return", "Adjust+", '
                                                                 '"Adjust-", "Scrap"]'),
                                   lbl("frL" + K, '"From"', 578, 0, 44, 36, size=10, color="cInk2", semibold=True),
                                   date("fr" + K, 622, 0, 170, 36, default="Blank()"),
                                   lbl("toL" + K, '"To"', 802, 0, 26, 36, size=10, color="cInk2", semibold=True),
                                   date("to" + K, 828, 0, 170, 36, default="Blank()"),
                                   btn("clr" + K, '"Clear"', 1010, 0, 80, 36,
                                       "Reset(q%s); Reset(ty%s); Reset(fr%s); Reset(to%s)" % (K, K, K, K), kind="secondary")]),
               sec("cnt" + K, 18, [lbl("cntL" + K, 'CountRows(lg%sGal.AllItems) & " movements match"' % K, 0, 0, 600, 18,
                                       size=11, color="cInk3")]),
               sec("tb" + K, 560, table("lg" + K, items, cols, y=0, h=560, row_h=46, empty="No transactions match",
                                        empty_sub="Try a different filter."), fill="cPanel", border="cLine", thick=1)]
    shell(K, "scrLedger", "ledger", content)


# =====================================================================  HIGH DEMAND
def scr_demand():
    K = "Dm"
    fields = ("PN: r.PN, PartNo: r.PartNo, Description: r.Description, UOM: r.UOM, Times: r.Times, Qty: r.Qty, Last: r.Last, "
              "OnHand: r.OnHand, RefQty: r.RefQty, Avail: r.Avail, Status: r.Status")
    items = (
        'With({days: Switch(p%(K)s.Selected.Value, "Last 90 Days", 90, "Last 180 Days", 180, "Last 12 Months", 365, 0), '
        's: Upper(Trim(q%(K)s.Text))}, '
        'With({src: Filter(nfMoves, SQty < 0 && (days = 0 || Date >= DateAdd(Today(), -days, TimeUnit.Days)))}, '
        'With({rows: Sort(Filter(ForAll(Distinct(src, PN) As D, With({rr: Filter(src, PN = D.Value), '
        'p: LookUp(nfStock, PN = D.Value)}, {PN: D.Value, PartNo: p.PartNo, Description: p.Description, UOM: p.UOM, '
        'Times: CountRows(rr), Qty: Sum(rr, Qty), Last: Max(rr, Date), OnHand: p.OnHand, RefQty: p.RefQty, '
        'Avail: p.Avail, Status: p.Status})), !IsBlank(PartNo)), Times * 1000000 + Qty, SortOrder.Descending)}, '
        'With({f: Filter(rows, IsBlank(s) || s in PN || s in Upper(Description))}, '
        'ForAll(Sequence(Min(200, CountRows(f))) As I, With({r: Index(f, I.Value)}, '
        '{Rank: I.Value, Top: First(f).Times, %(F)s}))))))' % {"K": K, "F": fields})

    def freq(n, x, w, rh):
        col = "If(ThisItem.Avail <= 0, cStop, ThisItem.RefQty > 0 && ThisItem.OnHand <= ThisItem.RefQty * 0.2, cWarn, cOk)"
        return [rect(n + "b", x, 18, w - 16, 6, "cSunk"),
                rect(n, x, 18, "(%d) * Max(0.03, ThisItem.Times / Max(1, ThisItem.Top))" % (w - 16), 6, col)]
    cols = [Col("#", 40, "ThisItem.Rank", "muted"),
            Col("Part", 170, "ThisItem.PartNo", "mono"),
            Col("Description", 230, "ThisItem.Description"),
            Col("Times issued", 90, num("ThisItem.Times"), align="Right", bold=True),
            Col("", 10, '""'),
            Col("Frequency", 150, None, "custom", make=freq),
            Col("Qty out", 90, num("ThisItem.Qty") + ' & " " & ThisItem.UOM', align="Right"),
            Col("On hand", 70, num("ThisItem.OnHand"), align="Right"),
            Col("Reorder", 60, num("ThisItem.RefQty"), align="Right", color="cInk3"),
            Col("", 10, '""'),
            Col("Status", 120, "ThisItem.Status", "pill"),
            Col("Last out", None, fdate("ThisItem.Last"), "mono")]
    content = [head(K, '"HIGH DEMAND PARTS"', '"Which material actually moves. Ranked by how often it is issued, with the '
                                               'quantity beside it, so reorder levels can be set on evidence."'),
               sec("flt" + K, 36, [lbl("pL" + K, '"Period"', 0, 0, 60, 36, size=10, color="cInk2", semibold=True),
                                   dd("p" + K, 60, 0, 200, 36, '["Last 90 Days", "Last 180 Days", "Last 12 Months", "Everything"]',
                                      default='"Last 12 months"'),
                                   inp("q" + K, 274, 0, 380, 36, hint="Search part or description")]),
               sec("tb" + K, 560, table("dm" + K, items, cols, y=0, h=560, row_h=40, empty="No movement in this period",
                                        empty_sub="Nothing has been issued against that filter. Showing the top 200 at most."),
                   fill="cPanel", border="cLine", thick=1)]
    shell(K, "scrDemand", "demand", content)


# =====================================================================  CREATE INVOICE
INVF = [  # (field, label, kind, width-cols, from-request expr, from-invoice expr)
    ("ToName", "To", "t", "r.BUContact"), ("CCName", "Cc", "t", '""'), ("FromName", "From", "t", "gMeName"),
    ("FromExt", "Ext no", "t", '""'), ("FromMobile", "Mobile", "t", '""'),
    ("HarnessPartNos", "Harness part nos.", "t", "r.HarnessPartNo"), ("JobDescription", "Job description", "t",
                                                                       "Coalesce(r.ScopeOfWork, r.Machine)"),
    ("BusinessUnit", "Business unit", "t", "r.BusinessUnit"), ("BUContact", "Business unit contact", "t", "r.BUContact"),
    ("CostCentre", "Cost centre / BU", "t", "r.CostCentre"),
    ("ApplicationDesc", "Application description", "t", 'If(IsBlank(r.BuildStage), "", "Build stage: " & r.BuildStage)'),
    ("DCContact", "DC contact", "t", "r.DCContact"), ("DCMobile", "DC mobile", "t", '""'),
    ("NoOfCircuits", "No. of circuits", "n", "Text(r.NoOfCircuits)"),
    ("RefRequest", "Ref request", "t", "r.RequestNo"), ("Notes", "Notes", "t", '""'),
    ("DetailsOfRequest", "Details of request", "m", "r.ScopeOfWork"),
]
INVD = [("InvoiceDate", "Invoice date", "Today()"), ("JobReceived", "Job received", "r.DateRaised"),
        ("StartDate", "Start date", "r.DateRaised"), ("CompletionDate", "Completion date", "Today()")]


def scr_invoice():
    K = "Iv"
    R = "LookUp(nfReq, RequestNo = gInvReq)"
    E = "LookUp(nfInv, InvoiceNo = gInvEdit)"

    def dflt(fld, from_req, kind):
        ed = ("Text(%s.%s)" if kind == "n" else "%s.%s") % (E, fld)
        return 'If(!IsBlank(gInvEdit), %s, !IsBlank(gInvReq), With({r: %s}, %s), %s)' % (
            ed, R, from_req, "gMeName" if fld == "FromName" else '""')
    kids = []
    kids += field("no" + K, "Invoice no (auto, editable)", 16, 60, 340,
                  lambda n, x, y, w, h: inp(n, x, y, w, h, default='If(!IsBlank(gInvEdit), gInvEdit, nfNextInvNo)', font=MONO),
                  req=True)
    kids += field("st" + K, "Status", 372, 60, 200, lambda n, x, y, w, h: dd(
        n, x, y, w, h, '["Draft", "Issued"]', default='If(!IsBlank(gInvEdit), %s, "Draft")' % DISP("%s.Status" % E)))
    kids += [lbl("fr" + K + "Lb", '"Fill from a Request"', 588, 60, 300, 16, size=10, color="cInk2", semibold=True),
             dd("fr" + K, 588, 78, 300, 34, prepend('"— Choose —"', 'ForAll(Sort(Filter(nfReq, Status in ["RELEASED", "PARTIALLY RELEASED", "COMPLETED"]), '
                                         'DateRaised, SortOrder.Descending), RequestNo)'),
                onchange='If(Self.Selected.Value <> "— Choose —", Set(gInvEdit, ""); Set(gInvReq, Self.Selected.Value))'),
             btn("ld" + K, '"Load BOM from request"', 900, 78, 174, 34,
                 'If(IsBlank(gInvReq), Notify("Pick a request first.", NotificationType.Warning), '
                 'ClearCollect(colInvLines, ForAll(Filter(nfLines, RequestNo = gInvReq) As L, {Sr: L.Sr, PartNo: L.PartNo, '
                 'Description: L.Description, Qty: If(L.QtyReleased > 0, L.QtyReleased, L.QtyRequested), '
                 'UnitCost: If(L.UnitCost > 0, L.UnitCost, Coalesce(LookUp(nfParts, PN = L.PN).UnitCost, 0))})))',
                 kind="secondary", size=10)]
    y, col = 124, 0
    for fld_, label, kind, fr in INVF:
        if kind == "m":
            continue
        x = 16 + col * 268
        kids += field(fld_ + K, label, x, y, 256, lambda n, x_, y_, w, h, f=fld_, fr=fr, kind=kind: inp(
            n, x_, y_, w, h, default=dflt(f, fr, kind), number=(kind == "n")), req=fld_ in ("NoOfCircuits", "ToName"))
        col += 1
        if col == 4:
            col, y = 0, y + 62
    if col:
        y += 62
    for i, (fld_, label, fr) in enumerate(INVD):
        kids += field(fld_ + K, label, 16 + i * 268, y, 256, lambda n, x_, y_, w, h, f=fld_, fr=fr: date(
            n, x_, y_, w, h, default='If(!IsBlank(gInvEdit), %s.%s, !IsBlank(gInvReq), With({r: %s}, %s), Today())'
                                     % (E, f, R, fr)))
    y += 62
    kids += [lbl("DetailsOfRequest" + K + "Lb", '"Details of Request"', 16, y, 400, 16, size=10, color="cInk2", semibold=True),
             inp("DetailsOfRequest" + K, 16, y + 18, "Parent.Width - 32", 60, mode="multi",
                 default=dflt("DetailsOfRequest", "r.ScopeOfWork", "m"))]
    head_h = y + 96
    hdr = card("cdH" + K, "Job card / invoice header", head_h, kids)

    # material lines (editable)
    lrow = [lbl("lSr" + K, "ThisItem.Sr", 0, 0, 36, 40, size=11, color="cInk3"),
            inp("lPn" + K, 40, 4, 220, 32, default="ThisItem.PartNo", font=MONO, size=11,
                onchange="Patch(colInvLines, ThisItem, {PartNo: Self.Text, Description: Coalesce(LookUp(nfParts, "
                         "PN = Upper(Trim(Self.Text))).Description, ThisItem.Description), UnitCost: If(ThisItem.UnitCost = 0, "
                         "Coalesce(LookUp(nfParts, PN = Upper(Trim(Self.Text))).UnitCost, 0), ThisItem.UnitCost)})"),
            lbl("lDs" + K, "ThisItem.Description", 270, 0, 380, 40, size=11, color="cInk2"),
            inp("lQ" + K, 660, 4, 110, 32, default="Text(ThisItem.Qty)", number=True, size=11,
                onchange="Patch(colInvLines, ThisItem, {Qty: Coalesce(Value(Self.Text), 0)})"),
            inp("lC" + K, 780, 4, 120, 32, default="Text(ThisItem.UnitCost)", number=True, size=11,
                onchange="Patch(colInvLines, ThisItem, {UnitCost: Coalesce(Value(Self.Text), 0)})"),
            lbl("lT" + K, num("ThisItem.Qty * ThisItem.UnitCost", 2), 910, 0, 120, 40, size=12, align="Right", bold=True),
            icon("lX" + K, 1036, 5, 30, 30, "Cancel", color="cStop", onselect="Remove(colInvLines, ThisItem)"),
            rect("lSp" + K, 0, 39, "Parent.TemplateWidth", 1, "cLine")]
    mat = card("cdM" + K, '"Material (BOM) — " & CountRows(colInvLines) & " lines · " & ' + inr("Sum(colInvLines, Qty * UnitCost)"),
               330, [lbl("mh%d%s" % (i, K), q(tc(t)), 16 + x, 52, w, 18, size=10, color="cJcb", bold=True,
                         align=a) for i, (t, x, w, a) in enumerate([("Sr", 0, 36, "Left"), ("PART NUMBER (A)", 40, 220, "Left"),
                         ("DESCRIPTION", 270, 380, "Left"), ("QTY (B)", 660, 110, "Left"), ("COST / UNIT (C)", 780, 120, "Left"),
                         ("COST (B×C)", 910, 120, "Right")])] + [
                     gallery("mg" + K, 16, 72, "Parent.Width - 32", 240, "colInvLines", 40, lrow)],
               right=[btn("ma" + K, '"+ Add row"', "Parent.Width - 112", 9, 96, 28,
                          'Collect(colInvLines, {Sr: Coalesce(Max(colInvLines, Sr), 0) + 1, PartNo: "", Description: "", '
                          'Qty: 1, UnitCost: 0})', kind="secondary", size=10)], title_is_formula=True)
    C = cost("IfError(Value(NoOfCircuits%s.Text), 0)" % K, "Sum(colInvLines, Qty * UnitCost)")
    calc_rows = [("Harness assembly hours", 'Text(%s.hours, "0.00") & " h  (" & %s.ckt & " circuits ÷ 7.5)"' % (C, C)),
                 ("Machine utilisation", num("%s.mach" % C, 2)), ("Manpower", num("%s.man" % C, 2)),
                 ("Electricity", num("%s.elec" % C, 2)), ("Harness assembly cost", num("%s.asm" % C, 2)),
                 ("Material cost (BOM)", num("%s.mat" % C, 2)), ("Transport (flat)", num("%s.trn" % C, 2)),
                 ("TOTAL COST (INR)", inr("%s.tot" % C))]
    calc = card("cdC" + K, "Calculated cost (Finance-locked formula)", 330,
                kv("cv" + K, calc_rows, 16, 58, 700, kw=260, row_h=32))
    # photos
    shots_one = "CountRows(colShots) = 1"
    ph = card("cdP" + K, "Harness label photos", 380, [
        Ctl("am" + K, ADDMEDIA, {"X": 16, "Y": 60, "Width": 260, "Height": 160, "Fill": "cInput", "Color": "cInputInk",
                                 "BorderColor": "cJcb", "BorderThickness": 2, "OnChange": (
            'If(!IsBlank(Self.Media), Collect(colShots, {Name: Substitute(Coalesce(no%s.Text, "invoice"), "/", "-") & "-" & '
            'Text(Now(), "yyyymmddhhmmss") & "-" & (CountRows(colShots) + 1) & ".jpg", Img: Self.Media}); '
            'Notify("Photo " & CountRows(colShots) & " attached. It uploads when you press Save Invoice.", '
            'NotificationType.Success))' % K)}),
        lbl("amN" + K, 'CountRows(colShots) & " photo(s) attached. Click the box (on a phone it opens the camera) for each '
                       'photo; it is attached straight away and uploads to the lab photo folder when you press '
                       'Save Invoice."', 16, 232, 260, 96, size=10, color="cInk2", wrap=True, valign="Top"),
        btn("amClr" + K, '"Remove All Photos"', 16, 334, 170, 32, "Clear(colShots)", kind="danger", size=9,
            visible="CountRows(colShots) > 0"),
        img("one" + K, 300, 60, "Parent.Width - 316", 300, "First(colShots).Img", visible=shots_one,
            extra={"BorderColor": "cLine", "BorderThickness": 1}),
        gallery("thm" + K, 300, 60, "Parent.Width - 316", 300, "colShots", 150, [
            img("thI" + K, 4, 4, 180, 140, "ThisItem.Img", extra={"BorderColor": "cLine", "BorderThickness": 1}),
            icon("thX" + K, 156, 4, 28, 28, "Cancel", color="cStop", onselect="Remove(colShots, ThisItem)")],
            visible="CountRows(colShots) > 1", extra={"WrapCount": 4})])
    save = (
        'With({no: Trim(no%(K)s.Text), c: %(C)s}, If(IsBlank(no), Notify("Invoice number is required.", NotificationType.Error), '
        'IsBlank(Trim(ToName%(K)s.Text)), Notify("To is required.", NotificationType.Error), '
        'Set(gBusy, true); '
        'With({up: ForAll(colShots As S, IfError(OneDriveForBusiness.CreateFile("/EDS Lab Portal Photos", S.Name, S.Img).Path, '
        '"ERR " & FirstError.Message))}, '
        'With({paths: Concat(Filter(up, !StartsWith(Value, "ERR ")), Value, ";"), '
        'perr: First(Filter(up, StartsWith(Value, "ERR "))).Value}, '
        'With({rec: {InvoiceNo: no, InvoiceDate: %(D1)s, ToName: ToName%(K)s.Text, '
        'CCName: CCName%(K)s.Text, FromName: FromName%(K)s.Text, FromExt: FromExt%(K)s.Text, FromMobile: FromMobile%(K)s.Text, '
        'HarnessPartNos: HarnessPartNos%(K)s.Text, JobDescription: JobDescription%(K)s.Text, BusinessUnit: BusinessUnit%(K)s.Text, '
        'BUContact: BUContact%(K)s.Text, CostCentre: CostCentre%(K)s.Text, ApplicationDesc: ApplicationDesc%(K)s.Text, '
        'DetailsOfRequest: DetailsOfRequest%(K)s.Text, NoOfCircuits: c.ckt, DCContact: DCContact%(K)s.Text, '
        'DCMobile: DCMobile%(K)s.Text, JobReceived: %(D2)s, StartDate: %(D3)s, CompletionDate: %(D4)s, '
        'MaterialCost: Round(c.mat, 2), AssemblyCost: Round(c.asm, 2), TransportCost: c.trn, TotalCost: Round(c.tot, 2), '
        'RefRequest: RefRequest%(K)s.Text, ImagePath: Concat(Filter(Table({v: Coalesce(%(E)s.ImagePath, "")}, {v: paths}), '
        '!IsBlank(v)), v, ";"), Status: Upper(st%(K)s.Selected.Value), Notes: Notes%(K)s.Text}}, If(IsBlank(LookUp(tblInvoice, Text(InvoiceNo) = no)), '
        'Collect(tblInvoice, rec), Patch(tblInvoice, LookUp(tblInvoice, Text(InvoiceNo) = no), rec))); '
        'Set(gInvEdit, no); Set(gBusy, false); '
        'If(IsBlank(perr), Clear(colShots); Notify(no & " saved" & If(IsBlank(paths), ".", '
        '" with its photos."), NotificationType.Success), '
        'Notify(no & " saved, but a photo did not upload: " & Mid(perr, 5) & ". The photos are still attached here; '
        'see About > Photo Storage Check, then save again.", NotificationType.Warning))))))'
        % {"K": K, "C": C, "E": E, "D1": noon("InvoiceDate%s.SelectedDate" % K), "D2": noon("JobReceived%s.SelectedDate" % K),
           "D3": noon("StartDate%s.SelectedDate" % K), "D4": noon("CompletionDate%s.SelectedDate" % K)})
    bar = sec("bar" + K, 50, [
        btn("new" + K, '"New blank invoice"', 0, 6, 180, 38,
            'Set(gInvEdit, ""); Set(gInvReq, ""); Clear(colInvLines); Clear(colShots); Reset(fr%s)' % K, kind="secondary"),
        btn("sv" + K, '"Save invoice"', "Parent.Width - 360", 6, 160, 38, save, disabled=BUSY),
        btn("pr" + K, '"Print / PDF"', "Parent.Width - 190", 6, 190, 38,
            'If(IsBlank(gInvEdit), Notify("Save the invoice first, then print it.", NotificationType.Warning), '
            'Set(gPrintKind, "invoice"); Navigate(scrPrint, ScreenTransition.None))', kind="secondary")])
    content = [head(K, '"CREATE INVOICE"', '"Job card for a finished harness. Costs use the Finance-locked formula; only the '
                                           'circuit count is an input."'), hdr, mat, calc, ph, bar]
    shell(K, "scrInvoice", "invoice", content)


def scr_invlist():
    K = "Il"
    items = ('With({s: Upper(Trim(q%s.Text)), f: st%s.Selected.Value}, Sort(Filter(nfInv, (f = "All" || Status = Upper(f)) && '
             '(IsBlank(s) || s in Upper(InvoiceNo & " " & BusinessUnit & " " & HarnessPartNos & " " & RefRequest & " " & '
             'ToName))), InvoiceDate, SortOrder.Descending))' % (K, K))

    def acts(n, x, w, rh):
        return [btn(n, '"Open"', x, 8, 56, 28, 'Set(gInvEdit, ThisItem.InvoiceNo); Set(gInvReq, ThisItem.RefRequest); '
                                               'Set(gPrintKind, "invoice"); Navigate(scrPrint, ScreenTransition.None)',
                    kind="secondary", size=10),
                btn(n + "e", '"Edit"', x + 60, 8, 50, 28, 'Set(gInvEdit, ThisItem.InvoiceNo); Set(gInvReq, ""); '
                                                          'Clear(colInvLines); Navigate(scrInvoice, ScreenTransition.None)',
                    kind="secondary", size=10, visible=ADMIN),
                btn(n + "i", '"Issue"', x + 114, 8, 56, 28,
                    'Patch(tblInvoice, LookUp(tblInvoice, Text(InvoiceNo) = ThisItem.InvoiceNo), {Status: "ISSUED"})',
                    size=10, visible='%s && ThisItem.Status = "DRAFT"' % ADMIN)]
    cols = [Col("Invoice", 160, "ThisItem.InvoiceNo", "mono"),
            Col("Date", 96, fdate("ThisItem.InvoiceDate"), "mono"),
            Col("Business unit", 110, "ThisItem.BusinessUnit"),
            Col("Harness", 120, "ThisItem.HarnessPartNos", "mono"),
            Col("Request", 120, "ThisItem.RefRequest", "mono"),
            Col("Circuits", 60, num("ThisItem.NoOfCircuits"), align="Right"),
            Col("Total", 110, inr("ThisItem.TotalCost"), align="Right", bold=True),
            Col("", 10, '""'),
            Col("Status", 90, "ThisItem.Status", "pill"),
            Col("", None, None, "custom", make=acts)]
    t = tiles("ti" + K, [("g", "Invoices", "CountRows(nfInv)", '"all periods"'),
                         ("a", "Billed value", inrs("nfRevTotal"), '"sum of TotalCost"'),
                         ("b", "This financial year", 'CountRows(Filter(nfInv, StartsWith(InvoiceNo, nfInvPrefix)))',
                          '"numbered " & nfInvPrefix & "…"'),
                         ("w", "Drafts", 'CountRows(Filter(nfInv, Status = "DRAFT"))', '"not yet issued"')])
    content = [head(K, '"Invoices"', '"Every job invoice the lab has raised"',
                    right=[btn("new" + K, '"+ Create invoice"', "Parent.Width - 160", 8, 150, 30,
                               'Set(gInvEdit, ""); Set(gInvReq, ""); Clear(colInvLines); Navigate(scrInvoice, ScreenTransition.None)',
                               visible=ADMIN, size=10)]),
               t,
               sec("flt" + K, 36, [dd("st" + K, 0, 0, 180, 36, '["All", "Draft", "Issued"]'),
                                   inp("q" + K, 194, 0, 420, 36, hint="Search invoice, BU, harness, request or recipient")]),
               sec("tb" + K, 520, table("iv" + K, items, cols, y=0, h=520, row_h=44, empty="No invoices yet",
                                        empty_sub="Create one from a released request."), fill="cPanel", border="cLine", thick=1)]
    shell(K, "scrInvList", "invlist", content)


# =====================================================================  COST SHEET
ASSUME = [("Cost of Machine (Stripping cutting + Pull force)", "kMachineCost"), ("Depreciation PA", "kDepPA"),
          ("Proto Harness Per Hrs", "kProtoHrs"), ("NO of HRS / Day", "kHrsDay"), ("Days / Month", "kDaysMonth"),
          ("Month PA", "kMonthsPA"), ("Total Standard Available Hrs PA", "kStdHrsPA"),
          ("No. of Employees / Technicians", "kTechs"), ("Per Hour Rate (INR)", "kRateHr"), ("No. of kWh per Hour", "kKwhHr"),
          ("Rate / KWH", "kRateKwh"), ("Total KWH PA", "kKwhPA"), ("Electricity total cost PA", "kElecPA"),
          ("AMC Per Hours (shown, NOT in total)", "kAmcHr"), ("Transportation cost (flat)", "kTransport"),
          ("Circuits per hour", "kCktPerHr")]


def scr_cost():
    K = "Cs"
    R = "LookUp(nfReq, RequestNo = gCostReq)"
    job = card("cdJ" + K, "Job details", 200, [
        lbl("frLb" + K, '"Fill from a Request"', 16, 58, 300, 16, size=10, color="cInk2", semibold=True),
        dd("fr" + K, 16, 76, 300, 34, prepend('"— Choose —"', "ForAll(Sort(nfReq, DateRaised, SortOrder.Descending), RequestNo)"),
           onchange='If(Self.Selected.Value <> "— Choose —", Set(gCostReq, Self.Selected.Value); '
                    'ClearCollect(colCostLines, ForAll(Filter(nfLines, RequestNo = gCostReq) As L, {Sr: L.Sr, PartNo: L.PartNo, '
                    'Description: L.Description, Qty: If(L.QtyReleased > 0, L.QtyReleased, L.QtyRequested), '
                    'UnitCost: If(L.UnitCost > 0, L.UnitCost, Coalesce(LookUp(nfParts, PN = L.PN).UnitCost, 0))})))')]
        + kv("jk" + K, [("Request / Job No", 'Coalesce(gCostReq, "—")'), ("Harness part no", '%s.HarnessPartNo' % R),
                        ("Machine / variant", "%s.Machine" % R)], 340, 58, 360, kw=150)
        + kv("jk2" + K, [("Business unit", "%s.BusinessUnit" % R), ("Requested by", "%s.RaisedByName" % R),
                         ("Date", 'Text(Today(), "dd-mmm-yyyy")')], 720, 58, 360, kw=130))
    C = cost("IfError(Value(ckt%s.Text), 0)" % K, "Sum(colCostLines, Qty * UnitCost)")
    inp_ = card("cdI" + K, "Input", 170, [
        pill("only" + K, "Parent.Width - 210", 12, 194, '"the only field you may change"'),
        lbl("cktLb" + K, '"No. of Circuits *"', 16, 58, 300, 16, size=10, color="cInk2", semibold=True),
        inp("ckt" + K, 16, 76, 260, 52, default='If(IsBlank(gCostReq), "200", Text(%s.NoOfCircuits))' % R, number=True,
            size=22, extra={"Color": "cJcb", "FontWeight": "FontWeight.Bold"}),
        lbl("hrs" + K, '"→ Harness assembly hours: " & Text(%s.hours, "0.00") & " Hours  (" & %s.ckt & " circuits ÷ 7.5)"'
            % (C, C), 16, 132, 700, 26, size=12, color="cInk2")])
    crow = [lbl("cSr" + K, "ThisItem.Sr", 0, 0, 36, 38, size=11, color="cInk3"),
            inp("cPn" + K, 40, 3, 260, 32, default="ThisItem.PartNo", font=MONO, size=11,
                onchange="Patch(colCostLines, ThisItem, {PartNo: Self.Text, UnitCost: If(ThisItem.UnitCost = 0, "
                         "Coalesce(LookUp(nfParts, PN = Upper(Trim(Self.Text))).UnitCost, 0), ThisItem.UnitCost)})"),
            inp("cQ" + K, 620, 3, 110, 32, default="Text(ThisItem.Qty)", number=True, size=11,
                onchange="Patch(colCostLines, ThisItem, {Qty: Coalesce(Value(Self.Text), 0)})"),
            inp("cC" + K, 740, 3, 130, 32, default="Text(ThisItem.UnitCost)", number=True, size=11,
                onchange="Patch(colCostLines, ThisItem, {UnitCost: Coalesce(Value(Self.Text), 0)})"),
            lbl("cT" + K, num("ThisItem.Qty * ThisItem.UnitCost", 2), 880, 0, 140, 38, size=12, align="Right", bold=True),
            icon("cX" + K, 1030, 4, 30, 30, "Cancel", color="cStop", onselect="Remove(colCostLines, ThisItem)"),
            rect("cSp" + K, 0, 37, "Parent.TemplateWidth", 1, "cLine")]
    paste_rows = ('With({raw: Filter(ForAll(Split(Substitute(bp%(K)s.Text, Char(13), ""), Char(10)) As L, '
                  'With({t: TrimEnds(Substitute(Substitute(Substitute(L.Value, Char(9), " "), ",", " "), ";", " "))}, '
                  'With({c3: Last(Split(t, " ")).Value}, With({t2: TrimEnds(Left(t, Len(t) - Len(c3)))}, '
                  'With({c2: Last(Split(t2, " ")).Value}, With({pn0: Upper(TrimEnds(Left(t2, Len(t2) - Len(c2))))}, '
                  '{PN: If(IsBlank(pn0), Upper(c2), pn0), Q: If(IsBlank(pn0), IfError(Value(c3), 0), IfError(Value(c2), 0)), '
                  'C: If(IsBlank(pn0), 0, IfError(Value(c3), 0))})))))), !IsBlank(PN) && Q > 0)}, '
                  'ForAll(Sequence(CountRows(raw)) As I, With({b: Index(raw, I.Value), p: LookUp(nfParts, PN = Index(raw, I.Value).PN)}, '
                  '{Sr: I.Value, PartNo: Coalesce(p.PartNo, b.PN), Description: Coalesce(p.Description, ""), Qty: b.Q, '
                  'UnitCost: If(b.C > 0, b.C, Coalesce(p.UnitCost, 0))})))' % {"K": K})
    mat = card("cdM" + K, '"Material Cost (BOM) — " & ' + inr("Sum(colCostLines, Qty * UnitCost)"), 520, [
        *[lbl("mh%d%s" % (i, K), q(tc(t)), 16 + x, 52, w, 18, size=10, color="cJcb", bold=True, align=a)
          for i, (t, x, w, a) in enumerate([("Sr", 0, 36, "Left"), ("PART NUMBER (A)", 40, 260, "Left"),
                                            ("QTY (B)", 620, 110, "Left"), ("COST / UNIT (C)", 740, 130, "Left"),
                                            ("COST (B×C)", 880, 140, "Right")])],
        gallery("mg" + K, 16, 72, "Parent.Width - 32", 260, "colCostLines", 38, crow),
        lbl("bpLb" + K, '"Upload BOM: paste Part Number (A), Qty (B), Cost / Unit (C), one line per part"', 16, 342, 900, 16,
            size=9, color="cInk3", font=MONO),
        inp("bp" + K, 16, 360, "Parent.Width - 230", 140, mode="multi", font=MONO, hint="405/F8525	2	1250"),
        btn("bpGo" + K, '"Load these lines"', "Parent.Width - 200", 360, 184, 36,
            "ClearCollect(colCostLines, %s); Reset(bp%s)" % (paste_rows, K))],
        right=[btn("ma" + K, '"+ Add row"', "Parent.Width - 112", 9, 96, 28,
                   'Collect(colCostLines, {Sr: Coalesce(Max(colCostLines, Sr), 0) + 1, PartNo: "", Description: "", Qty: 1, '
                   'UnitCost: 0})', kind="secondary", size=10)], title_is_formula=True)
    rows = [("Material cost (BOM)", num("%s.mat" % C, 2)), ("Machine utilisation", num("%s.mach" % C, 2)),
            ("Manpower", num("%s.man" % C, 2)), ("Electricity", num("%s.elec" % C, 2)),
            ("Harness assembly cost (Finance assumptions)", num("%s.asm" % C, 2)),
            ("Transportation cost (at actual)", num("%s.trn" % C, 2)), ("TOTAL COST", inr("%s.tot" % C))]
    calc = card("cdC" + K, "Calculated", 300, kv("cv" + K, rows, 16, 58, 760, kw=360, row_h=32))
    asm_rows = [(t, 'Text(%s, "#,##0.##")' % v) for t, v in ASSUME]
    half = (len(asm_rows) + 1) // 2
    asm = card("cdA" + K, "Assumptions (Finance-locked, read only)", 340,
               kv("av" + K, asm_rows[:half], 16, 58, 520, kw=380, row_h=32) +
               kv("aw" + K, asm_rows[half:], 560, 58, 510, kw=370, row_h=32))
    bar = sec("bar" + K, 50, [
        btn("pr" + K, '"Print assumptions + cost sheet"', "Parent.Width - 280", 6, 280, 38,
            'Set(gPrintKind, "cost"); Set(gPrintCkt, IfError(Value(ckt%s.Text), 0)); Navigate(scrPrint, ScreenTransition.None)' % K)])
    content = [head(K, '"COST SHEET & ASSUMPTIONS"', '"Finance owns every assumption below. The only figure the lab enters is '
                                                     'the circuit count."'), job, inp_, mat, calc, asm, bar]
    shell(K, "scrCost", "cost", content)


# =====================================================================  PRINT (white, Excel-coloured tables)
def h_td(text, style="", colspan=1):
    cs = (' colspan=\'%d\'' % colspan) if colspan > 1 else ""
    return '"<td%s style=\'border:1px solid #8A8A8A;padding:4px 6px;%s\'>" & %s & "</td>"' % (cs, style, text)


GRN = "background:#22B14C;color:#fff;font-weight:bold;text-align:center;"
ORG = "background:#E8A33D;font-weight:bold;"
ROSE = "background:#E8B4B8;font-weight:bold;"
LTY = "background:#FAF4A0;font-weight:bold;"
BRN = "background:#7A6B3A;color:#fff;font-weight:bold;"
YEL = "background:#FFF200;"
R_ = "text-align:right;"


def html_table(rows, style="width:100%;border-collapse:collapse;margin-top:10px"):
    body = ' & '.join('"<tr>" & %s & "</tr>"' % " & ".join(r) for r in rows)
    return '"<table style=\'%s\'>" & %s & "</table>"' % (style, body)


def scr_print():
    K = "Pr"
    T = lambda s: q(s)
    N0 = lambda x: 'Text(%s, "#,##0")' % x
    N2 = lambda x: 'Text(%s, "#,##0.00")' % x
    C = cost("gPrintCkt", "Sum(colCostLines, Qty * UnitCost)")
    R = "LookUp(nfReq, RequestNo = gCostReq)"
    meta = '"Job " & Coalesce(gCostReq, "—") & " · Harness " & Coalesce(%s.HarnessPartNo, "—") & " · " & Text(Today(), "dd-mmm-yyyy")' % R
    assume = html_table([
        [h_td(T("Assumptions"), GRN, 6)],
        [h_td(T("Cost of Machine / Per hr rate"), ORG, 2), h_td('""', ORG), h_td(T("Inputs"), ORG, 2), h_td('""', ORG)],
        [h_td(T("Cost of Machine (Stripping cutting + Pull force)"), "", 2), h_td(N0("kMachineCost"), R_),
         h_td(T("No. of circuits"), "", 2), h_td(N0("%s.ckt" % C), R_ + "background:#FFF2CC;font-weight:bold")],
        [h_td(T("Depreciation PA"), "", 2), h_td(N0("kDepPA"), R_), h_td(T("Harness assembly Hours"), "", 2),
         h_td('Text(%s.hours, "0.00")' % C, R_)],
        [h_td(T("Proto Harness Per Hrs"), "background:#F4CCCC", 2), h_td("Text(kProtoHrs)", R_ + "background:#F4CCCC"),
         h_td('""', "", 2), h_td('""')],
        [h_td(T("NO of HRS / Day"), YEL, 2), h_td("Text(kHrsDay)", R_ + YEL), h_td('""', "", 2), h_td('""')],
        [h_td(T("Days / Month"), YEL, 2), h_td("Text(kDaysMonth)", R_ + YEL), h_td('""', "", 2), h_td('""')],
        [h_td(T("Month PA"), YEL, 2), h_td("Text(kMonthsPA)", R_ + YEL), h_td(T("Electricity"), ORG, 2), h_td('""', ORG)],
        [h_td(T("Total Standard Available Hrs PA"), YEL + "font-weight:bold", 2), h_td(N0("kStdHrsPA"), R_ + YEL),
         h_td(T("No. of kWh per Hour"), "", 2), h_td("Text(kKwhHr)", R_)],
        [h_td(T("Manpower Cost"), ORG, 2), h_td('""', ORG), h_td(T("No. of Std Hours PA"), "", 2), h_td(N0("kStdHrsPA"), R_)],
        [h_td(T("No. of Employees / Technicians"), "", 2), h_td("Text(kTechs)", R_), h_td(T("Total KWH PA"), "", 2),
         h_td(N0("kKwhPA"), R_)],
        [h_td(T("Per hour rate 1236 INR"), "", 2), h_td("Text(kRateHr)", R_), h_td(T("Rate / KWH"), "", 2),
         h_td("Text(kRateKwh)", R_)],
        [h_td(T("Total Manpower cost"), "background:#F4CCCC", 2), h_td(N0("%s.man" % C), R_ + "background:#F4CCCC;font-weight:bold"),
         h_td(T("Total cost"), "", 2), h_td(N0("kElecPA"), R_)],
        [h_td(T("AMC Per Hours"), YEL + "color:#C00000", 2), h_td("Text(kAmcHr)", R_ + YEL + "color:#C00000"),
         h_td(T("Cost of machine Utilisation"), "", 2), h_td(N2("%s.mach" % C), R_)],
        [h_td('""', YEL, 2), h_td('""', YEL), h_td(T("Manpower Cost"), "", 2), h_td(N0("%s.man" % C), R_)],
        [h_td('""', "", 2), h_td('""'), h_td(T("Electricity"), "", 2), h_td(N2("%s.elec" % C), R_)],
        [h_td(T("Harness Assembly Cost"), BRN + "text-align:center", 4), h_td(N2("%s.asm" % C), BRN + R_), h_td(T("INR"), BRN)],
        [h_td(T("Transportation cost"), BRN + "text-align:center", 4), h_td("Text(kTransport)", BRN + R_), h_td(T("INR"), BRN)]])
    lines = ('If(CountRows(colCostLines) = 0, "<tr><td colspan=\'5\' style=\'border:1px solid #8A8A8A;padding:4px;'
             'text-align:center\'>— no material lines —</td></tr>", Concat(colCostLines, "<tr>" & %s & %s & %s & %s & %s & "</tr>"))'
             % (h_td("Text(Sr)", "text-align:center"), h_td("PartNo"), h_td(N0("Qty"), R_), h_td(N2("UnitCost"), R_),
                h_td(N2("Qty * UnitCost"), R_)))
    sheet = (html_table([[h_td(T("Request / Job No"), LTY), h_td('Coalesce(gCostReq, "")'),
                          h_td(T("Business Unit"), LTY), h_td('Coalesce(%s.BusinessUnit, "")' % R)],
                         [h_td(T("Harness Part No"), LTY), h_td('Coalesce(%s.HarnessPartNo, "")' % R),
                          h_td(T("Requested by"), LTY), h_td('Coalesce(%s.RaisedByName, "")' % R)],
                         [h_td(T("Machine / Variant"), LTY), h_td('Coalesce(%s.Machine, "")' % R),
                          h_td(T("No. of circuits"), LTY), h_td(N0("%s.ckt" % C) + ' & " Nos"', "font-weight:bold")]])
             + ' & "<table style=\'width:100%;border-collapse:collapse;margin-top:10px\'><tr>" & ' + h_td(T("Material Cost"), ORG + "text-align:center", 5)
             + ' & "</tr><tr>" & ' + " & ".join([h_td(T("Sr"), ROSE), h_td(T("Part Number (A)"), ROSE), h_td(T("Qty (B)"), ROSE + R_),
                                                 h_td(T("Cost / Unit (C)"), ROSE + R_), h_td(T("Cost (B×C)"), ROSE + R_)])
             + ' & "</tr>" & ' + lines + ' & "<tr>" & ' + h_td(T("Total Material Cost"), LTY, 4) + ' & ' + h_td(N2("%s.mat" % C), LTY + R_)
             + ' & "</tr></table>" & '
             + html_table([[h_td(T("Summary"), GRN, 2)],
                           [h_td(T("Material cost (BOM)")), h_td(N2("%s.mat" % C), R_ + "width:180px")],
                           [h_td(T("Harness assembly cost (as per Finance assumptions)")), h_td(N2("%s.asm" % C), R_)],
                           [h_td(T("Transportation cost (at actual)")), h_td(N2("%s.trn" % C), R_)],
                           [h_td(T("TOTAL COST"), BRN), h_td(N2("%s.tot" % C), BRN + R_)]]))
    sig = lambda a, b: ('"<table style=\'width:100%;margin-top:34px\'><tr><td style=\'padding-top:26px\'><div style=\'border-top:1px solid #000;'
                        'width:220px;padding-top:3px\'>' + a + '</div></td><td style=\'padding-top:26px\'><div style=\'border-top:1px solid #000;'
                        'width:220px;padding-top:3px\'>' + b + '</div></td></tr></table>"')
    doc_style = "font-family:Calibri,Segoe UI,Arial,sans-serif;font-size:12px;color:#000;background:#fff"
    cost_html = ('"<div style=\'%s\'><p style=\'font-size:17px;font-weight:bold;margin:0 0 3px\'>Harness Assembly Cost — Assumptions</p>'
                 '<p style=\'font-size:11px;color:#444;margin:0 0 8px\'>JCB India · EDS Lab · " & %s & "</p>" & %s & '
                 '"<p style=\'font-size:10px;color:#444\'>AMC is shown above and is deliberately not included in the Harness Assembly Cost, '
                 'matching the Finance workbook. Assembly hours = circuits ÷ 7.5.</p>" & %s & '
                 '"<p style=\'page-break-before:always;font-size:17px;font-weight:bold;margin:24px 0 3px\'>Harness Cost Sheet</p>'
                 '<p style=\'font-size:11px;color:#444;margin:0 0 8px\'>JCB India · EDS Lab · " & %s & "</p>" & %s & %s & "</div>"'
                 % (doc_style, meta, assume, sig("Prepared by (Lab Incharge)", "Checked by (Finance)"), meta, sheet,
                    sig("Prepared by (Lab Incharge)", "Approved by (Finance)")))
    V = "LookUp(nfInv, InvoiceNo = gInvEdit)"
    ilines = ('If(CountRows(Filter(nfLines, RequestNo = %s.RefRequest)) = 0, "<tr><td colspan=\'5\' style=\'border:1px solid #8A8A8A;'
              'padding:4px;text-align:center\'>— material cost " & Text(%s.MaterialCost, "#,##0.00") & " (lines not stored) —</td></tr>", '
              'Concat(Filter(nfLines, RequestNo = %s.RefRequest), "<tr>" & %s & %s & %s & %s & %s & "</tr>"))'
              % (V, V, V, h_td("Text(Sr)", "text-align:center"), h_td("PartNo"),
                 h_td(N0("If(QtyReleased > 0, QtyReleased, QtyRequested)"), R_), h_td(N2("UnitCost"), R_),
                 h_td(N2("If(QtyReleased > 0, QtyReleased, QtyRequested) * UnitCost"), R_)))
    fd = lambda x: 'If(IsBlank(%s), "", Text(%s, "dd-mmm-yyyy"))' % (x, x)
    inv_html = ('"<div style=\'%s\'><p style=\'font-size:17px;font-weight:bold;margin:0 0 3px\'>EDS Lab — Job Invoice</p>'
                '<p style=\'font-size:11px;color:#444;margin:0 0 8px\'>JCB India · Pune · Design Centre</p>" & '
                % doc_style
                + html_table([[h_td('"<b>To:</b> " & %s.ToName & "<br><br><b>Cc:</b> " & %s.CCName' % (V, V), "width:56%", 2),
                               h_td('"<b>From</b> : " & %s.FromName & "<br><b>Ext No</b> : " & %s.FromExt & "<br><b>Mobile</b> : " & %s.FromMobile'
                                    % (V, V, V), "", 2)]])
                + ' & ' + html_table([
                    [h_td(T("Job No"), LTY + "width:20%"), h_td("%s.InvoiceNo" % V, "font-weight:bold;color:#C00000;width:36%"),
                     h_td(T("DC Contact"), LTY + "width:22%"), h_td("%s.DCContact" % V, "font-weight:bold")],
                    [h_td(T("Harness Part Nos."), LTY), h_td("%s.HarnessPartNos" % V), h_td(T("Job Received"), LTY),
                     h_td(fd("%s.JobReceived" % V), R_)],
                    [h_td(T("Job Description"), LTY), h_td("%s.JobDescription" % V), h_td(T("Start Date"), LTY),
                     h_td(fd("%s.StartDate" % V), R_)],
                    [h_td(T("Business Unit"), LTY), h_td("%s.BusinessUnit" % V), h_td(T("Completion Date"), LTY),
                     h_td(fd("%s.CompletionDate" % V), R_)],
                    [h_td(T("Business Unit Contact"), LTY), h_td("%s.BUContact" % V), h_td(T("No. of circuits"), LTY),
                     h_td(N0("%s.NoOfCircuits" % V), R_ + "font-weight:bold")],
                    [h_td(T("Cost Centre / BU"), LTY), h_td("%s.CostCentre" % V), h_td(T("Invoice Date"), LTY),
                     h_td(fd("%s.InvoiceDate" % V), R_)],
                    [h_td(T("Application description"), LTY), h_td("%s.ApplicationDesc" % V, "", 3)],
                    [h_td(T("Details of request"), LTY), h_td("%s.DetailsOfRequest" % V, "", 3)]])
                + ' & "<table style=\'width:100%;border-collapse:collapse;margin-top:10px\'><tr>" & '
                + h_td(T("Material Cost (BOM)"), ORG + "text-align:center", 5) + ' & "</tr><tr>" & '
                + " & ".join([h_td(T("Sr"), ROSE), h_td(T("Part Number (A)"), ROSE), h_td(T("Qty (B)"), ROSE + R_),
                              h_td(T("Cost / Unit (C)"), ROSE + R_), h_td(T("Cost (B×C)"), ROSE + R_)])
                + ' & "</tr>" & ' + ilines + ' & "</table>" & '
                + html_table([[h_td(T("Description"), GRN, 2)],
                              [h_td(T("Harness Assembly")), h_td(N2("%s.AssemblyCost" % V), R_ + "width:180px")],
                              [h_td(T("BOM COST")), h_td(N2("%s.MaterialCost" % V), R_)],
                              [h_td(T("Transport Cost"), ORG), h_td(N2("%s.TransportCost" % V), ORG + R_)],
                              [h_td(T("Total Cost (INR)"), BRN), h_td(N2("%s.TotalCost" % V), BRN + R_)]])
                + ' & "<p style=\'margin:12px 0 0;font-weight:bold;background:#CDE3F0;border:1px solid #8A8A8A;padding:4px;'
                  'text-align:center\'>Harness label Images</p></div>"')
    paths = 'Filter(ForAll(Split(Coalesce(%s.ImagePath, ""), ";") As S, {P: Trim(S.Value)}), !IsBlank(P))' % V
    kids = [
        rect("bg" + K, 0, 0, 1366, 768, "RGBA(255, 255, 255, 1)"),
        box("tb" + K, 0, 0, 1366, 48, [
            btn("bk" + K, '"‹ Back"', 12, 8, 100, 32,
                'If(gPrintKind = "cost", Navigate(scrCost, ScreenTransition.None), Navigate(scrInvList, ScreenTransition.None))',
                kind="secondary"),
            btn("pp" + K, '"Print / Save as PDF"', 124, 8, 200, 32, "Set(gPrinting, true)"),
            lbl("tbN" + K, '"Choose \'Save as PDF\' in the print dialog to get a file. This toolbar is hidden while printing."',
                340, 8, 900, 32, size=11, color="cInk3")], fill="cBg", border="cLine", visible="!gPrinting"),
        Ctl("htm" + K, "HtmlViewer", {"X": 40, "Y": "If(gPrinting, 10, 58)", "Width": 1286,
                                      "Height": 'If(gPrintKind = "invoice" && CountRows(%s) > 0, 520, If(gPrinting, 750, 700))' % paths,
                                      "HtmlText": 'If(gPrintKind = "invoice", %s, %s)' % (inv_html, cost_html),
                                      "Color": "RGBA(0, 0, 0, 1)", "Size": 11, "PaddingTop": 0, "PaddingLeft": 0}),
        gallery("ph" + K, 40, 580, 1286, 180, paths, 176, [
            img("phI" + K, 4, 4, 300, 168, "OneDriveForBusiness.GetFileContentByPath(ThisItem.P)",
                extra={"BorderColor": "RGBA(153,153,153,1)", "BorderThickness": 1})],
            visible='gPrintKind = "invoice" && CountRows(%s) > 0' % paths, extra={"WrapCount": 4, "ShowScrollbar": "false"}),
        Ctl("tm" + K, TIMER, {"X": 1300, "Y": 0, "Width": 10, "Height": 10, "Visible": "false", "Duration": 600,
                              "Start": "gPrinting", "AutoStart": "false", "Repeat": "false",
                              "OnTimerEnd": "Print(); Set(gPrinting, false)"}),
    ]
    root = box("root" + K, 0, 0, 1366, 768, kids, fill="RGBA(255, 255, 255, 1)", border="RGBA(255, 255, 255, 1)", thick=0)
    SCREENS.append(("scrPrint", "", root))


# =====================================================================  PROCUREMENT
PROC_STAGES = '["PR RAISED", "APPROVED", "PO RAISED", "GRN IN PROGRESS", "DELIVERED (CLOSED)", "REJECTED"]'
PROCF = [("PRNumber", "PR number", "t"), ("Department", "Department", "t"), ("Summary", "Summary", "t"),
         ("ServiceType", "Service type", "dd:[\"MATERIAL\", \"SERVICE\", \"TOOL\", \"LICENSE\", \"COMPONENTS\"]"),
         ("Qty", "Quantity", "n"), ("DateRaised", "Date raised", "d"), ("RaisedBy", "Raised by", "t"),
         ("ApprovedBy", "Approved by", "t"), ("ApprovedDate", "Approved date", "d"), ("PONumber", "PO number", "t"),
         ("Vendor", "Vendor", "vendor"), ("POAmount", "PO amount (INR)", "n"), ("Stage", "Stage", "dd:" + PROC_STAGES),
         ("PODate", "PO date", "d"), ("DeliveredDate", "Delivered date", "d"), ("PRAmount", "PR amount (INR)", "n"),
         ("InvestmentType", "Investment type", "dd:[\"Capex\", \"Opex\", \"AMC\", \"\"]"),
         ("POApprovedDate", "PO approved date", "d"), ("Ownership", "Ownership", "t"),
         ("POCopyPath", "PO copy (SharePoint / OneDrive link)", "t"), ("Notes", "Notes", "t")]


def scr_proc():
    K = "Pc"
    E = "LookUp(nfProc, PRNumber = gEditPr)"
    nxt = ('Switch(ThisItem.Stage, "PR RAISED", If(gRole = "Manager", "Approve PR", "Mark Approved"), "APPROVED", "Raise PO", '
           '"PO RAISED", "Mark GRN in Progress", "GRN IN PROGRESS", "Mark Delivered / Closed", "")')
    adv = ('Switch(ThisItem.Stage, '
           '"PR RAISED", Patch(tblProc, LookUp(tblProc, Text(PRNumber) = ThisItem.PRNumber), {Stage: "APPROVED", ApprovedBy: gMeName, '
           'ApprovedDate: %(N)s}), '
           '"APPROVED", Set(gEditPr, ThisItem.PRNumber); Set(gPanel, "proc"); Notify("Fill in the PO number, vendor, amount and date, '
           'set Stage = PO RAISED, then Save.", NotificationType.Information), '
           '"PO RAISED", Patch(tblProc, LookUp(tblProc, Text(PRNumber) = ThisItem.PRNumber), {Stage: "GRN IN PROGRESS"}), '
           '"GRN IN PROGRESS", Patch(tblProc, LookUp(tblProc, Text(PRNumber) = ThisItem.PRNumber), {Stage: "DELIVERED (CLOSED)", '
           'DeliveredDate: %(N)s}))' % {"N": noon()})

    def acts(n, x, w, rh):
        return [btn(n, nxt, x, 8, 150, 28, adv, kind="secondary", size=9,
                    visible='(%s && !IsBlank(%s)) || (%s && ThisItem.Stage = "PR RAISED")' % (ADMIN, nxt, MGR)),
                btn(n + "e", '"Edit"', x + 156, 8, 50, 28, 'Set(gEditPr, ThisItem.PRNumber); Set(gPanel, "proc")',
                    kind="secondary", size=9, visible=ADMIN),
                btn(n + "r", '"Reject"', x + 212, 8, 58, 28,
                    'Patch(tblProc, LookUp(tblProc, Text(PRNumber) = ThisItem.PRNumber), {Stage: "REJECTED"})',
                    kind="danger", size=9, visible='(%s && !(ThisItem.Stage in ["DELIVERED (CLOSED)", "REJECTED"])) || '
                                                   '(%s && ThisItem.Stage = "PR RAISED")' % (ADMIN, MGR))]
    items = ('With({s: Upper(Trim(q%s.Text)), f: st%s.Selected.Value}, Sort(Filter(nfProc, (f = "All Stages" || Stage = Upper(f)) && '
             '(IsBlank(s) || s in Upper(PRNumber & " " & Summary & " " & PONumber & " " & Vendor & " " & ServiceType))), '
             'DateRaised, SortOrder.Descending))' % (K, K))
    cols = [Col("PR number", 110, "ThisItem.PRNumber", "mono"),
            Col("Summary", 160, "ThisItem.Summary", sub='ThisItem.ServiceType & " · qty " & ThisItem.Qty'),
            Col("Raised", 100, fdate("ThisItem.DateRaised"), "mono",
                sub='If(IsBlank(ThisItem.DateRaised), "", DateDiff(ThisItem.DateRaised, Today(), TimeUnit.Days) & "d old")'),
            Col("Approved by", 90, 'Coalesce(ThisItem.ApprovedBy, "—")'),
            Col("PO", 100, 'Coalesce(ThisItem.PONumber, "—")', "mono", sub="ThisItem.Vendor"),
            Col("PO amount", 84, 'If(ThisItem.POAmount > 0, %s, "—")' % inr("ThisItem.POAmount"), align="Right"),
            Col("", 10, '""'),
            Col("Stage", 130, "ThisItem.Stage", "pill"),
            Col("", None, None, "custom", make=acts)]
    # edit / new panel
    kids = []
    for i, (fld_, label, kind) in enumerate(PROCF):
        x, y = 16 + (i % 4) * 268, 58 + (i // 4) * 62
        n = "pf" + fld_ + K
        cur = "%s.%s" % (E, fld_)
        if kind == "t":
            mk = lambda n_, x_, y_, w, h, cur=cur, fld_=fld_: inp(n_, x_, y_, w, h, default=(
                'If(IsBlank(gEditPr), If("%s" = "Department", "EDS", "%s" = "RaisedBy", gMeName, ""), %s)' % (fld_, fld_, cur)),
                font=MONO if fld_ in ("PRNumber", "PONumber") else UI)
        elif kind == "n":
            mk = lambda n_, x_, y_, w, h, cur=cur: inp(n_, x_, y_, w, h, number=True,
                                                       default='If(IsBlank(gEditPr), "", Text(%s))' % cur)
        elif kind == "d":
            mk = lambda n_, x_, y_, w, h, cur=cur, fld_=fld_: date(n_, x_, y_, w, h, default=(
                'If(IsBlank(gEditPr), If("%s" = "DateRaised", Today(), Blank()), %s)' % (fld_, cur)))
        elif kind == "vendor":
            mk = lambda n_, x_, y_, w, h, cur=cur: inp(n_, x_, y_, w, h, default='If(!IsBlank(gVendorPick), gVendorPick, '
                                                                                  'IsBlank(gEditPr), "", %s)' % cur)
        else:
            opts = kind[3:]
            mk = lambda n_, x_, y_, w, h, cur=cur, opts=opts: dd(n_, x_, y_, w, h, disp_list(opts),
                                                                 default='If(IsBlank(gEditPr), First(%s).Value, %s)'
                                                                         % (disp_list(opts), DISP(cur)))
        kids += field(n, label, x, y, 256, mk, req=fld_ in ("PRNumber", "Summary"))
    vy = 58 + ((len(PROCF) + 3) // 4) * 62
    kids += [lbl("vpL" + K, '"Pick A Vendor Used Before"', 16, vy, 300, 16, size=10, color="cInk2", semibold=True),
             dd("vp" + K, 16, vy + 18, 300, 34, prepend('"—"', "Sort(Distinct(Filter(nfProc, !IsBlank(Vendor)), Vendor), Value)"),
                onchange='If(Self.Selected.Value <> "—", Set(gVendorPick, Self.Selected.Value); Reset(pfVendor%s))' % K)]
    vals = ", ".join(
        "%s: %s" % (f, ("Coalesce(IfError(Value(pf%s%s.Text), 0), 0)" % (f, K)) if k == "n" else
                    noon("pf%s%s.SelectedDate" % (f, K)) if k == "d" else
                    ("Upper(pf%s%s.Selected.Value)" % (f, K)) if k.startswith("dd:") else ("Trim(pf%s%s.Text)" % (f, K)))
        for f, _, k in PROCF)
    save = ('With({no: Trim(pfPRNumber%(K)s.Text)}, If(IsBlank(no) || IsBlank(Trim(pfSummary%(K)s.Text)), '
            'Notify("PR number and summary are required.", NotificationType.Error), '
            'IsBlank(gEditPr) && !IsBlank(LookUp(tblProc, Text(PRNumber) = no)), Notify("A PR with that number already exists.", '
            'NotificationType.Error), '
            'With({rec: {%(V)s}}, If(IsBlank(gEditPr), Collect(tblProc, rec), Patch(tblProc, LookUp(tblProc, Text(PRNumber) = gEditPr), rec))); '
            'Notify(no & " saved.", NotificationType.Success); Set(gEditPr, ""); Set(gVendorPick, ""); Set(gPanel, "")))'
            % {"K": K, "V": vals})
    kids += [btn("pfNo" + K, '"Cancel"', "Parent.Width - 300", vy + 18, 120, 36,
                 'Set(gEditPr, ""); Set(gVendorPick, ""); Set(gPanel, "")', kind="secondary"),
             btn("pfGo" + K, '"Save PR / PO"', "Parent.Width - 170", vy + 18, 154, 36, save)]
    panel = card("cdF" + K, 'If(IsBlank(gEditPr), "New PR / PO Entry", "Edit " & gEditPr)', vy + 80, kids,
                 visible='gPanel = "proc"', title_is_formula=True)
    receipts = 'Filter(nfMoves, Type = "RECEIPT" && !IsBlank(Reference))'
    legacy0 = ('ForAll(Distinct(%s, Reference) As G, With({rr: Filter(%s, Reference = G.Value)}, {Ref: G.Value, '
               'FOC: Sum(rr, UnitCost) = 0, Supplier: LookUp(nfParts, PN = First(rr).PN).Supplier, D: Max(rr, Date), '
               'N: CountRows(rr), Amt: Sum(rr, Qty * UnitCost)}))' % (receipts, receipts))
    legacy = "Sort(%s, D, SortOrder.Descending)" % legacy0
    open_ = 'CountRows(Filter(nfProc, !(Stage in ["DELIVERED (CLOSED)", "REJECTED"])))'
    t = tiles("ti" + K, [("w", "PRs / POs in progress", open_, '"across all stages"'),
                         ("", "Purchase orders", 'CountRows(Filter(%s, !FOC))' % legacy0, '"legacy paid references"'),
                         ("b", "FOC receipts", 'CountRows(Filter(%s, FOC))' % legacy0, '"free of charge"'),
                         ("a", "Committed value", inrs("Sum(nfProc, POAmount)"), '"PO amount on the PR/PO tracker"')])
    shortc = card("cdS" + K, "Shortages waiting for a purchase requisition", 300, table("sh" + K, "nfShortBook", [
        Col("Part", 200, "ThisItem.PartNo", "mono"), Col("Description", 360, "ThisItem.Description"),
        Col("Qty short", 100, num("ThisItem.Qty"), align="Right", bold=True, color="cStop"),
        Col("", 20, '""'), Col("Requests", None, "ThisItem.Requests", "mono")], h=254, row_h=36,
        empty="Nothing outstanding", empty_sub="No reserved request is currently short of material."))
    legc = card("cdG" + K, "Legacy purchase references (receipts in Movements)", 360, table("lg" + K, legacy, [
        Col("Reference", 170, "ThisItem.Ref", "mono"), Col("Type", 90, 'If(ThisItem.FOC, "FOC", "PO")'),
        Col("Supplier", 300, 'Coalesce(ThisItem.Supplier, "—")'), Col("Date", 110, fdate("ThisItem.D"), "mono"),
        Col("Lines", 70, "ThisItem.N", align="Right"),
        Col("Value", None, 'If(ThisItem.Amt > 0, %s, "—")' % inr("ThisItem.Amt"), align="Right")], h=314, row_h=34))
    content = [head(K, '"PROCUREMENT (PR / PO)"', '"Every requisition raised from this lab, its stage, and legacy purchase references"',
                    right=[btn("new" + K, '"+ New PR / PO entry"', "Parent.Width - 180", 8, 170, 30,
                               'Set(gEditPr, ""); Set(gVendorPick, ""); Set(gPanel, "proc")', visible=ADMIN, size=10)]),
               t, panel,
               sec("flt" + K, 36, [dd("st" + K, 0, 0, 230, 36, disp_list(PROC_STAGES, "All Stages")),
                                   inp("q" + K, 244, 0, 420, 36, hint="Search PR, summary, PO, vendor")]),
               card("cdT" + K, 'If(%s, "PR / PO Tracker: Click a Stage Button to Move a Requisition Forward", "PR / PO Tracker (Read Only)")'
                    % ADMIN, 470, table("pc" + K, items, cols, h=424, row_h=48, empty="Nothing raised yet"), title_is_formula=True),
               shortc, legc]
    shell(K, "scrProc", "proc", content)


# =====================================================================  ONGOING PURCHASE
PURCH_STAGES = '["REQUIRED", "PR RAISED", "PO RAISED", "IN TRANSIT", "RECEIVED"]'


def scr_purch():
    K = "Pu"
    E = "LookUp(nfPurch, PartNo = gEditPurch && RequestNo = gEditPurchReq)"
    addrow = ('If(IsBlank(LookUp(tblPurch, Upper(Trim(Text(PartNo))) = %(S)s.PN && Text(RequestNo) = %(S)s.Requests)), '
              'Collect(tblPurch, {PartNo: %(S)s.PartNo, Description: %(S)s.Description, QtyRequired: %(S)s.Qty, QtyConfirmed: 0, '
              'RequestNo: %(S)s.Requests, RaisedBy: gMeName, PRNumber: "", SupplierNo: "", SupplierName: "", Stage: "REQUIRED", '
              'DateRaised: %(N)s, Notes: %(S)s.Who & " waiting"}); true, false)')
    book = card("cdB" + K, "Shortfall across every open request", 330, table("bk" + K, "nfShortBook", [
        Col("Part", 170, "ThisItem.PartNo", "mono", sub='If(ThisItem.NewPart, "NEW PART", "")'),
        Col("Description", 240, "ThisItem.Description"),
        Col("Short by", 80, num("ThisItem.Qty"), align="Right", bold=True, color="cStop"),
        Col("", 14, '""'),
        Col("Requests", 160, "ThisItem.Requests", "mono"),
        Col("Who is waiting", 170, "ThisItem.Who"),
        Col("Already raised", 110, 'Coalesce(Concat(Filter(nfPurch, PN = ThisItem.PN && !IsBlank(PRNumber)), PRNumber, ", "), "—")',
            "mono"),
        Col("", None, None, "custom", make=lambda n, x, w, rh: [btn(n, '"Add"', x, 8, 56, 28,
            'If(%s, Notify("Added to the purchase list.", NotificationType.Success), Notify("That part is already on the '
            'purchase list.", NotificationType.Warning))' % (addrow % {"S": "ThisItem", "N": noon()}), kind="secondary", size=10,
            visible=ADMIN)])], h=284, row_h=44, empty="Nothing is short", empty_sub="Every open request can be met from stock."),
        right=[btn("pull" + K, '"Add All Shortfalls to the Purchase List"', "Parent.Width - 300", 9, 284, 28,
                   'ForAll(nfShortBook As SB, %s); Notify("Shortfall lines added (existing ones skipped).", NotificationType.Success)'
                   % (addrow % {"S": "SB", "N": noon()}), kind="secondary", size=10, visible=ADMIN)])

    def acts(n, x, w, rh):
        return [btn(n, '"Edit"', x, 8, 56, 28, 'Set(gEditPurch, ThisItem.PartNo); Set(gEditPurchReq, ThisItem.RequestNo); '
                                               'Set(gPanel, "purch")', kind="secondary", size=10, visible=ADMIN)]
    items = ('With({s: Upper(Trim(q%s.Text)), f: st%s.Selected.Value}, Filter(nfPurch, (f = "All Stages" || Stage = Upper(f)) && '
             '(IsBlank(s) || s in Upper(PartNo & " " & Description & " " & RequestNo & " " & PRNumber & " " & SupplierName))))' % (K, K))
    tab = card("cdT" + K, "Purchase List: What Is on Order", 470, table("pt" + K, items, [
        Col("Part", 160, "ThisItem.PartNo", "mono", sub="ThisItem.Description"),
        Col("Required", 70, num("ThisItem.QtyRequired"), align="Right"),
        Col("Confirmed", 76, num("ThisItem.QtyConfirmed"), align="Right",
            color="If(ThisItem.QtyConfirmed < ThisItem.QtyRequired, cWarn, cOk)"),
        Col("", 10, '""'),
        Col("Request", 130, 'Coalesce(ThisItem.RequestNo, "—")', "mono"),
        Col("PR number", 100, 'Coalesce(ThisItem.PRNumber, "—")', "mono"),
        Col("Supplier", 150, 'Coalesce(ThisItem.SupplierName, "—")', sub="ThisItem.SupplierNo"),
        Col("Stage", 110, "ThisItem.Stage", "pill"),
        Col("Expected", 100, fdate("ThisItem.ExpectedDate"), "mono"),
        Col("", None, None, "custom", make=acts)], h=424, row_h=46, empty="Nothing on the purchase list yet",
        empty_sub="Add a shortfall above, then fill in the PR number and supplier once purchasing issues them."))
    f = []
    f += field("pe0" + K, "Part number", 16, 58, 256, lambda n, x, y, w, h: inp(n, x, y, w, h, font=MONO,
               default='If(IsBlank(gEditPurch), "", %s.PartNo)' % E, disabled='!IsBlank(gEditPurch)'), req=True)
    f += field("pe1" + K, "Description", 284, 58, 524, lambda n, x, y, w, h: inp(n, x, y, w, h, default='%s.Description' % E))
    f += field("pe2" + K, "Quantity required", 820, 58, 256, lambda n, x, y, w, h: inp(n, x, y, w, h, number=True,
               default='Text(%s.QtyRequired)' % E))
    f += field("pe3" + K, "Quantity confirmed", 16, 120, 256, lambda n, x, y, w, h: inp(n, x, y, w, h, number=True,
               default='Text(%s.QtyConfirmed)' % E))
    f += field("pe4" + K, "PR number", 284, 120, 256, lambda n, x, y, w, h: inp(n, x, y, w, h, font=MONO,
               default='%s.PRNumber' % E))
    f += field("pe5" + K, "Supplier number", 552, 120, 256, lambda n, x, y, w, h: inp(n, x, y, w, h, default='%s.SupplierNo' % E))
    f += field("pe6" + K, "Supplier name", 820, 120, 256, lambda n, x, y, w, h: inp(n, x, y, w, h, default='%s.SupplierName' % E))
    f += field("pe7" + K, "Stage", 16, 182, 256, lambda n, x, y, w, h: dd(n, x, y, w, h, disp_list(PURCH_STAGES),
               default=DISP('Coalesce(%s.Stage, "REQUIRED")' % E)))
    f += field("pe8" + K, "Expected date", 284, 182, 256, lambda n, x, y, w, h: date(n, x, y, w, h, default='%s.ExpectedDate' % E))
    f += field("pe9" + K, "Notes", 552, 182, 524, lambda n, x, y, w, h: inp(n, x, y, w, h, default='%s.Notes' % E))
    f += field("peA" + K, "Request no", 16, 244, 256, lambda n, x, y, w, h: inp(n, x, y, w, h, font=MONO,
               default='If(IsBlank(gEditPurch), "", gEditPurchReq)', disabled='!IsBlank(gEditPurch)'))
    rec = ('{PartNo: Trim(pe0%(K)s.Text), Description: pe1%(K)s.Text, QtyRequired: IfError(Value(pe2%(K)s.Text), 0), '
           'QtyConfirmed: IfError(Value(pe3%(K)s.Text), 0), RequestNo: Trim(peA%(K)s.Text), PRNumber: Trim(pe4%(K)s.Text), '
           'SupplierNo: Trim(pe5%(K)s.Text), SupplierName: Trim(pe6%(K)s.Text), Stage: Upper(pe7%(K)s.Selected.Value), '
           'ExpectedDate: If(IsBlank(pe8%(K)s.SelectedDate), Blank(), %(ETA)s), Notes: pe9%(K)s.Text}'
           % {"K": K, "ETA": noon("pe8%s.SelectedDate" % K)})
    save = ('If(IsBlank(Trim(pe0%(K)s.Text)), Notify("Part number is required.", NotificationType.Error), '
            'If(IsBlank(gEditPurch), Collect(tblPurch, Patch(%(REC)s, {RaisedBy: gMeName, DateRaised: %(N)s})), '
            'Patch(tblPurch, LookUp(tblPurch, Trim(Text(PartNo)) = gEditPurch && Text(RequestNo) = gEditPurchReq), %(REC)s)); '
            'Notify(Trim(pe0%(K)s.Text) & " saved.", NotificationType.Success); Set(gEditPurch, ""); Set(gPanel, ""))'
            % {"K": K, "REC": rec, "N": noon()})
    f += [btn("peNo" + K, '"Cancel"', "Parent.Width - 300", 262, 120, 36, 'Set(gEditPurch, ""); Set(gPanel, "")', kind="secondary"),
          btn("peGo" + K, '"Save"', "Parent.Width - 170", 262, 154, 36, save)]
    panel = card("cdE" + K, 'If(IsBlank(gEditPurch), "New Purchase Line", "Purchase Line — " & gEditPurch)', 320, f,
                 visible='gPanel = "purch"', title_is_formula=True)
    book_qty = "Sum(nfShortBook, Qty)"
    t = tiles("ti" + K, [("r", "Parts short right now", "CountRows(nfShortBook)", '"across all open requests"'),
                         ("a", "On the Purchase List", "CountRows(nfPurch)",
                          'CountRows(Filter(nfPurch, Stage <> "RECEIVED")) & " still open"'),
                         ("w", "Total shortfall qty", num(book_qty), '"units to be bought"')])
    content = [head(K, '"ONGOING PURCHASE / REQUIRED"', 'If(%s, "What the lab is short of, and what has been raised against it. '
                                                        'Fill in the PR number and supplier as they are issued.", "What the lab is '
                                                        'short of, and what has been raised against it.")' % ADMIN,
                    right=[btn("new" + K, '"+ New purchase line"', "Parent.Width - 180", 8, 170, 30,
                               'Set(gEditPurch, ""); Set(gEditPurchReq, ""); Set(gPanel, "purch")', visible=ADMIN, size=10)]),
               t, panel, book,
               sec("flt" + K, 36, [dd("st" + K, 0, 0, 200, 36, disp_list(PURCH_STAGES, "All Stages")),
                                   inp("q" + K, 214, 0, 420, 36, hint="Search part, request, PR or supplier")]),
               tab]
    shell(K, "scrPurch", "purch", content)


# =====================================================================  SOFTWARE LICENSES
def scr_lic():
    K = "Lc"
    canact = ADMIN

    def cell(fld_, number=False, w_off=8):
        def mk(n, x, w, rh):
            cur = "Text(ThisItem.%s)" % fld_ if number else "ThisItem.%s" % fld_
            return [inp(n, x, 7, w - w_off, 32, default=cur, number=number, size=11, visible=canact),
                    lbl(n + "r", cur, x, 0, w - 8, rh, size=11, visible="!(%s)" % canact,
                        align="Right" if number else "Left")]
        return mk

    def exp(n, x, w, rh):
        return [date(n, x, 7, w - 8, 32, default="ThisItem.ExpiryDate", visible=canact, extra={"Size": 10}),
                lbl(n + "r", fdate("ThisItem.ExpiryDate"), x, 0, w - 8, rh, size=11, font=MONO, visible="!(%s)" % canact)]

    def save(n, x, w, rh):
        return [icon(n, x, 8, 32, 32, "Save", color="cJcb", visible=canact, tooltip="Save this license row",
                     onselect='Patch(tblLicenses, LookUp(tblLicenses, Text(SoftwareName) = ThisItem.SoftwareName), '
                              '{Vendor: lcC1.Text, LicenseType: lcC2.Text, SeatsTotal: IfError(Value(lcC3.Text), 0), '
                              'SeatsInUse: IfError(Value(lcC4.Text), 0), ExpiryDate: %s, AnnualCost: IfError(Value(lcC6.Text), 0), '
                              'Notes: lcC8.Text}); Notify(ThisItem.SoftwareName & " saved.", NotificationType.Success)'
                              % noon("lcC5.SelectedDate"))]
    cols = [Col("Software", 170, "ThisItem.SoftwareName", bold=True),
            Col("Vendor", 120, None, "custom", make=cell("Vendor")),
            Col("Type", 120, None, "custom", make=cell("LicenseType")),
            Col("Seats", 64, None, "custom", make=cell("SeatsTotal", True)),
            Col("In use", 64, None, "custom", make=cell("SeatsInUse", True)),
            Col("Expiry", 140, None, "custom", make=exp),
            Col("Annual cost", 100, None, "custom", make=cell("AnnualCost", True)),
            Col("Status", 120, "ThisItem.Status", "pill"),
            Col("Notes", 130, None, "custom", make=cell("Notes")),
            Col("", None, None, "custom", make=save)]
    tbl = table("lc", "Sort(nfLic, ExpiryDate)", cols, h=400, row_h=46, empty="No licenses tracked yet")
    attn = 'CountRows(Filter(nfLic, Status in ["EXPIRED", "EXPIRING SOON"]))'
    t = tiles("ti" + K, [("a", "Licenses tracked", "CountRows(nfLic)", '"products"'),
                         ("If(%s > 0, cStop, cLine2)" % attn, "Need attention", attn, '"expired or within 45 days"'),
                         ("b", "Seats in use", 'Sum(nfLic, SeatsInUse) & " / " & Sum(nfLic, SeatsTotal)', '"across all products"'),
                         ("g", "Annual spend", inrs("Sum(nfLic, AnnualCost)"), '"sum of AnnualCost"')])
    add = []
    specs = [("SoftwareName", "Software name", False), ("Vendor", "Vendor", False), ("LicenseType", "License type", False),
             ("SeatsTotal", "Seats total", True), ("SeatsInUse", "Seats in use", True), ("AnnualCost", "Annual cost", True),
             ("Notes", "Notes", False)]
    for i, (f_, label, nm) in enumerate(specs):
        add += field("la%s%s" % (f_, K), label, 16 + (i % 4) * 268, 58 + (i // 4) * 62, 256,
                     lambda n, x, y, w, h, nm=nm: inp(n, x, y, w, h, number=nm), req=f_ == "SoftwareName")
    add += field("laExp" + K, "Expiry date", 16 + 3 * 268, 120, 256, lambda n, x, y, w, h: date(n, x, y, w, h))
    rec = ", ".join("%s: %s" % (f_, ("IfError(Value(la%s%s.Text), 0)" if nm else "Trim(la%s%s.Text)") % (f_, K))
                    for f_, _, nm in specs)
    add += [btn("laGo" + K, '"Add license"', "Parent.Width - 170", 190, 154, 36,
                'If(IsBlank(Trim(laSoftwareName%(K)s.Text)), Notify("Software name is required.", NotificationType.Error), '
                '!IsBlank(LookUp(tblLicenses, Text(SoftwareName) = Trim(laSoftwareName%(K)s.Text))), Notify("Already tracked.", '
                'NotificationType.Error), Collect(tblLicenses, {%(R)s, ExpiryDate: %(E)s}); Notify("License added.", '
                'NotificationType.Success); Set(gPanel, ""))' % {"K": K, "R": rec, "E": noon("laExp%s.SelectedDate" % K)})]
    addc = card("cdA" + K, "Add a license", 240, add, visible='gPanel = "lic" && %s' % ADMIN)
    content = [head(K, '"SOFTWARE LICENSES"', 'If(%s, "Edit a row and press its save icon; it is '
                                              'saved straight away.", "Every software license the lab pays for.")' % ADMIN,
                    right=[btn("new" + K, '"+ Add license"', "Parent.Width - 150", 8, 140, 30, 'Set(gPanel, "lic")',
                               visible=ADMIN, size=10)]),
               t, addc, card("cdT" + K, "Licenses", 450, tbl)]
    shell(K, "scrLic", "lic", content)


# =====================================================================  TEAM ACCESS
def scr_team():
    K = "Tm"

    def ed(fld_, font=UI):
        def mk(n, x, w, rh):
            return [inp(n, x, 6, w - 8, 30, default="Text(ThisItem.%s)" % fld_, size=11, font=font)]
        return mk

    ROLES = '["Engineer", "Lab Admin", "Lab Lead", "Manager", "Engineer, Manager", "Pending", "Disabled"]'

    def role(n, x, w, rh):
        return [dd(n, x, 6, w - 8, 30, ROLES,
                   default='With({r: Trim(Text(ThisItem.Role))}, Coalesce(LookUp(%s As RO, Lower(RO.Value) = Lower(r)).Value, %s))'
                           % (ROLES, role_canon("r")), extra={"Size": 11})]

    def save(n, x, w, rh):
        temp = ('With({code: Text(RandBetween(100000, 999999)), u: ThisItem}, Patch(tblUsers, ThisItem, {Password: %s, '
                'PasswordSetOn: ""}); Set(gTempCode, "Temporary password for " & ThisItem.Username & ": " & code); '
                'Notify(gTempCode & ". Tell them in person. It works once, then they choose their own.", '
                'NotificationType.Information))' % hash_fx("code", "Lower(Trim(Text(u.Username)))", "t1$"))
        return [icon(n, x, 6, 30, 30, "Save", color="cJcb", tooltip="Save this person",
                     onselect='Patch(tblUsers, ThisItem, {FullName: tmC1.Text, Role: tmC2.Selected.Value, BusinessUnit: tmC3.Text, '
                              'Email: Lower(Trim(tmC4.Text))}); Notify(ThisItem.Username & " saved.", NotificationType.Success)'),
                btn(n + "t", '"Temp Password"', x + 36, 7, 116, 28, temp, kind="secondary", size=9)]
    items = ('With({s: Lower(Trim(q%s.Text))}, Sort(Filter(tblUsers, !IsBlank(Username) && (IsBlank(s) || s in Lower(Text(Username) & " " & '
             'Text(FullName) & " " & Text(Role) & " " & Text(BusinessUnit) & " " & Text(Email)))), Text(Username)))' % K)
    pw = ('With({st: Trim(Text(ThisItem.Password)), rk: %s}, If(rk = "Pending", "PENDING APPROVAL", '
          'StartsWith(st, "p1$"), "SET", StartsWith(st, "t1$"), "TEMPORARY", "NOT SET"))'
          % role_canon('Trim(First(Split(Text(ThisItem.Role), ",")).Value)'))
    cols = [Col("Username", 150, "Text(ThisItem.Username)", "mono"),
            Col("Full name", 170, None, "custom", make=ed("FullName")),
            Col("Role", 150, None, "custom", make=role),
            Col("Business unit", 110, None, "custom", make=ed("BusinessUnit")),
            Col("Email", 170, None, "custom", make=ed("Email", MONO)),
            Col("Password", 120, pw, "pill"),
            Col("", None, None, "custom", make=save)]
    add = []
    for i, (f_, label) in enumerate([("Username", "Username (email before @)"), ("FullName", "Full name"),
                                     ("BusinessUnit", "Business unit"), ("Email", "Email (optional)")]):
        add += field("ta%s%s" % (f_, K), label, 16 + i * 268, 58, 256, lambda n, x, y, w, h: inp(n, x, y, w, h),
                     req=f_ in ("Username", "FullName"))
    add += field("taRole" + K, "Role", 16, 120, 256, lambda n, x, y, w, h: dd(n, x, y, w, h, ROLES), req=True)
    add += [btn("taGo" + K, '"Add person"', "Parent.Width - 170", 138, 154, 36,
                'If(IsBlank(Trim(taUsername%(K)s.Text)) || IsBlank(Trim(taFullName%(K)s.Text)), Notify("Username and full name '
                'are required.", NotificationType.Error), !IsBlank(LookUp(tblUsers, Lower(Trim(Text(Username))) = '
                'Lower(Trim(taUsername%(K)s.Text)))), Notify("That username already exists.", NotificationType.Error), '
                'Collect(tblUsers, {Username: Lower(Trim(taUsername%(K)s.Text)), FullName: Trim(taFullName%(K)s.Text), '
                'Role: taRole%(K)s.Selected.Value, BusinessUnit: Trim(taBusinessUnit%(K)s.Text), Email: Lower(Trim(taEmail%(K)s.Text))}); '
                'Notify("Added. Now give them a temporary password (Temp Password on their row) so they can log in.", '
                'NotificationType.Success); '
                'Set(gPanel, ""))' % {"K": K})]
    addc = card("cdA" + K, "Add a person", 200, add, visible='gPanel = "team"')
    content = [head(K, '"Team Access"', '"Approve access requests, set roles, and give a temporary password when someone '
                                        'forgets theirs."',
                    right=[btn("new" + K, '"+ Add person"', "Parent.Width - 150", 8, 140, 30, 'Set(gPanel, "team")', size=10)]),
               addc,
               sec("flt" + K, 36, [inp("q" + K, 0, 0, 420, 36, hint="Search name, username, role, BU or email"),
                                   lbl("cnt" + K, 'CountRows(tmGal.AllItems) & " people  ·  " & CountRows(Filter(tblUsers, '
                                                  'Lower(Trim(Text(Role))) = "pending")) & " waiting for approval"',
                                       436, 0, 230, 36, size=11, color="cInk3"),
                                   lbl("tmp" + K, "gTempCode", 670, 0, 420, 36, size=11, bold=True, color="cJcb",
                                       align="Right")]),
               sec("tb" + K, 560, table("tm", items, cols, y=0, h=560, row_h=42), fill="cPanel", border="cLine", thick=1)]
    shell(K, "scrTeam", "team", content)


# =====================================================================  WELCOME / LOGIN / ABOUT
def topbar(K, right=None):
    return [img("tbLogo" + K, 40, 26, 46, 46, "imgLogo"),
            lbl("tbT1" + K, '"EDS Lab Material Portal"', 96, 26, 420, 28, size=17, bold=True, color="cInk"),
            lbl("tbT2" + K, '"JCB India  ·  " & tLabName', 96, 52, 420, 20, size=10, semibold=True, color="cJcb")] + \
        (right or [])


def scr_welcome():
    K = "Wl"
    hero = box("hero" + K, 60, 160, 620, 440, [
        lbl("eyb" + K, '"Electrical Development Lab  ·  Material Management"', 40, 34, 540, 24, size=10, bold=True,
            color="cOrange"),
        lbl("h1" + K, '"Welcome to the"', 40, 66, 540, 34, size=20, color="cInk2"),
        lbl("h2" + K, '"EDS Lab Material Portal"', 40, 100, 560, 52, size=30, bold=True, color="cInk"),
        img("hl" + K, 40, 158, 300, 4, "imgLine", extra={"ImagePosition": "ImagePosition.Stretch"}),
        lbl("p" + K, '"Live stock, BOM checks in seconds, and every material request from submission to release, '
                     'in one place."', 40, 178, 540, 64, size=13, color="cInk2", wrap=True, valign="Top"),
        lbl("ch1" + K, '"✓  Live Stock"', 40, 256, 150, 32, size=10, bold=True, color="cJcb", fill="cJcbWash",
            align="Center"),
        lbl("ch2" + K, '"✓  BOM Compare"', 200, 256, 160, 32, size=10, bold=True, color="cJcb", fill="cJcbWash",
            align="Center"),
        lbl("ch3" + K, '"✓  Approvals and Release"', 370, 256, 210, 32, size=10, bold=True, color="cJcb",
            fill="cJcbWash", align="Center"),
        btn("go" + K, '"Log In   ›"', 40, 330, 250, 52, 'Set(gLoginMode, "login"); Set(gLoginMsg, ""); '
            'Navigate(scrLogin, ScreenTransition.Fade)', size=14, radius=26),
        btn("rg" + K, '"Request Access"', 306, 330, 250, 52, 'Set(gLoginMode, "register"); Set(gLoginMsg, ""); '
            'Navigate(scrLogin, ScreenTransition.Fade)', kind="secondary", size=13, radius=26)],
        fill="cGlass", border="cLine2", radius=24)
    kids = backdrop(K, "RGBA(8, 6, 10, 0.05)") + topbar(K) + [hero,
        lbl("ver" + K, '"Version %s"' % APP_VERSION, 1100, 730, 240, 22, size=9, color="cInk3", align="Right")]
    root = box("root" + K, 0, 0, 1366, 768, kids, fill="cBg", border="cBg", thick=0)
    SCREENS.append(("scrWelcome", "", root))


def pw_rules(p):
    return ('Len(%s) < 6 || CountRows(Filter(Split(%s, ""), Value in "0123456789")) = 0 || Lower(%s) = Upper(%s)'
            % (p, p, p, p))


def scr_login():
    K = "Li"
    from appfx import hash_fx, login_ok, role_canon
    msg = lambda m: 'Set(gLoginMsg, %s)' % m
    LOG, SET, REG = 'gLoginMode = "login"', 'gLoginMode = "setpw"', 'gLoginMode = "register"'
    key = 'Lower(Trim(Text(u.Username)))'
    me_u = 'LookUp(tblUsers, Lower(Trim(Text(Username))) = Lower(Trim(Text(gPend.Username))))'
    login = (
        'With({un: Lower(Trim(usr%(K)s.Text)), pw: pwd%(K)s.Text}, '
        'With({u: LookUp(tblUsers, Lower(Trim(Text(Username))) = un || (!IsBlank(Email) && Lower(Trim(Text(Email))) = un))}, '
        'With({st: Trim(Text(u.Password)), rk: %(RK)s}, '
        'If(IsBlank(un), %(M1)s, IsBlank(pw) && StartsWith(st, "p1$"), %(M2)s, '
        'IsBlank(u), %(M3)s, rk = "Pending", %(M4)s, rk = "Disabled", %(M5)s, '
        'gLoginTries >= 5, %(M6)s, '
        'StartsWith(st, "p1$"), If(%(HP)s = st, %(OK)s, Set(gLoginTries, gLoginTries + 1); %(M7)s), '
        'StartsWith(st, "t1$"), If(%(HT)s = st, Set(gPend, u); Set(gLoginMode, "setpw"); %(M8)s, '
        'Set(gLoginTries, gLoginTries + 1); %(M7)s), '
        'Lower(First(Split(User().Email, "@")).Value) = %(KEY)s || (!IsBlank(u.Email) && Lower(User().Email) = '
        'Lower(Trim(Text(u.Email)))), Set(gPend, u); Set(gLoginMode, "setpw"); %(M9)s, '
        '%(M10)s))))'
        % {"K": K, "RK": role_canon('Trim(First(Split(Text(u.Role), ",")).Value)'), "KEY": key,
           "HP": hash_fx("pw", key, "p1$"), "HT": hash_fx("pw", key, "t1$"), "OK": login_ok("u"),
           "M1": msg('"Type your username."'), "M2": msg('"Type your password."'),
           "M3": msg('"No account with that username. Use Register to ask for access."'),
           "M4": msg('"Your access request is waiting for the Lab Lead\'s approval."'),
           "M5": msg('"This account is switched off. Please ask the Lab Lead."'),
           "M6": msg('"Too many wrong attempts. Close the app and open it again, or ask the Lab Lead."'),
           "M7": msg('"That password is not right."'),
           "M8": msg('"Temporary password accepted. Now choose your own password."'),
           "M9": msg('"First time here: choose your password."'),
           "M10": msg('"This account has no password yet. Ask the Lab Lead for a temporary password."')})
    setpw = (
        'With({p: np1%(K)s.Text, u: %(U)s}, If(%(RULES)s, %(R1)s, p <> np2%(K)s.Text, %(R2)s, '
        'Patch(tblUsers, u, {Password: %(H)s, PasswordSetOn: Text(Today(), "yyyy-mm-dd")}); '
        'Reset(np1%(K)s); Reset(np2%(K)s); %(OK)s))'
        % {"K": K, "U": me_u, "RULES": pw_rules("p"), "H": hash_fx("p", key, "p1$"), "OK": login_ok(me_u),
           "R1": msg('"At least 6 characters, with a letter and a number."'),
           "R2": msg('"The two passwords do not match."')})
    reg = (
        'With({un: Lower(Trim(rgU%(K)s.Text)), nm: Trim(rgN%(K)s.Text), p: rgP1%(K)s.Text}, '
        'If(IsBlank(nm) || IsBlank(un), %(E1)s, '
        '" " in un, %(E2)s, '
        '!IsBlank(LookUp(tblUsers, Lower(Trim(Text(Username))) = un)), %(E3)s, '
        '%(RULES)s, %(E4)s, p <> rgP2%(K)s.Text, %(E5)s, '
        'Collect(tblUsers, {Username: un, FullName: nm, Role: "Pending", BusinessUnit: Trim(rgB%(K)s.Text), '
        'Password: %(H)s, PasswordSetOn: Text(Today(), "yyyy-mm-dd"), Email: Lower(Trim(rgM%(K)s.Text))}); '
        'Reset(rgU%(K)s); Reset(rgN%(K)s); Reset(rgB%(K)s); Reset(rgM%(K)s); Reset(rgP1%(K)s); Reset(rgP2%(K)s); '
        'Set(gLoginMode, "login"); %(OK)s))'
        % {"K": K, "RULES": pw_rules("p"), "H": hash_fx("p", "un", "p1$"),
           "E1": msg('"Full name and username are required."'),
           "E2": msg('"A username cannot contain spaces (for example gaurav.shelke)."'),
           "E3": msg('"That username already exists. Log in, or pick another one."'),
           "E4": msg('"Password: at least 6 characters, with a letter and a number."'),
           "E5": msg('"The two passwords do not match."'),
           "OK": msg('"✓  Request sent. You can log in as soon as the Lab Lead approves it."')})

    def pillrow(n, y, text, ico, ctl, vis):
        return [btn(n + "Pl", q(text), 60, y, 160, 48, "SetFocus(%s)" % ctl.name, size=11, radius=12, align="Left",
                    visible=vis, extra={"PaddingLeft": 44}),
                Ctl(n + "Ic", "Classic/Icon", {"X": 76, "Y": y + 14, "Width": 20, "Height": 20, "Icon": "Icon." + ico,
                                               "Color": "cOnJcb", "OnSelect": "SetFocus(%s)" % ctl.name, "Visible": vis,
                                               "PaddingTop": 0, "PaddingBottom": 0, "PaddingLeft": 0, "PaddingRight": 0}),
                ctl]
    pwmode = {"Mode": "TextMode.Password"}
    kids = [
        lbl("t" + K, 'Switch(gLoginMode, "setpw", "Set Your Password", "register", "Request Access", "User Login")',
            0, 26, 700, 48, size=28, bold=True, color="cOrange", align="Center"),
        lbl("s" + K, 'Switch(gLoginMode, "setpw", "Hi " & Coalesce(gPend.FullName, gPend.Username) & ", choose the '
                     'password you will use every time.", "register", "Ask the Lab Lead for an account. You can log in as '
                     'soon as it is approved.", "Sign in with your lab username and password.")',
            40, 74, 620, 24, size=11, color="cInk2", align="Center")]
    kids += pillrow("u" + K, 124, "Username", "Person",
                    inp("usr" + K, 232, 124, 408, 48, hint="Type your username", size=13, visible=LOG), LOG)
    kids += pillrow("p" + K, 188, "Password", "Lock",
                    inp("pwd" + K, 232, 188, 408, 48, hint="Type your password", size=13, visible=LOG, extra=pwmode), LOG)
    kids += pillrow("n1" + K, 124, "New Password", "Lock",
                    inp("np1" + K, 232, 124, 408, 48, hint="At least 6 characters, a letter and a number", size=13,
                        visible=SET, extra=pwmode), SET)
    kids += pillrow("n2" + K, 188, "Confirm", "Lock",
                    inp("np2" + K, 232, 188, 408, 48, hint="Type it again", size=13, visible=SET, extra=pwmode), SET)
    reg_f = [("rgN", "Full Name", True, 0, 0, "Gaurav Shelke", None), ("rgU", "Username", True, 1, 0, "gaurav.shelke", None),
             ("rgB", "Business Unit", False, 0, 1, "EDS", None), ("rgM", "Email (Optional)", False, 1, 1, "name@jcb.com", None),
             ("rgP1", "Password", True, 0, 2, "At least 6, a letter and a number", pwmode),
             ("rgP2", "Confirm Password", True, 1, 2, "Type it again", pwmode)]
    for nm, label, req, col, row, hint, ex in reg_f:
        x, y = 60 + col * 300, 110 + row * 64
        kids += [lbl(nm + K + "Lb", q(label + (" *" if req else "")), x, y, 280, 18, size=10, semibold=True,
                     color="cInk2", visible=REG),
                 inp(nm + K, x, y + 20, 280, 40, hint=hint, visible=REG, extra=ex)]
    kids += [
        lbl("m" + K, "gLoginMsg", 40, 'If(%s, 304, 246)' % REG, 620, 28, size=11, bold=True, align="Center",
            color='If(StartsWith(gLoginMsg, "✓"), cOk, cStop)'),
        btn("go" + K, '"Login"', 60, 284, 280, 50, login, size=14, radius=12, visible=LOG),
        btn("rg" + K, '"Register"', 360, 284, 280, 50, 'Set(gLoginMode, "register"); Set(gLoginMsg, "")', size=14,
            radius=12, visible=LOG, kind="secondary", extra={"Color": "cJcb", "BorderColor": "cJcb"}),
        btn("sp" + K, '"Save and Log In"', 60, 284, 280, 50, setpw, size=14, radius=12, visible=SET),
        btn("sx" + K, '"Cancel"', 360, 284, 280, 50, 'Set(gLoginMode, "login"); Set(gLoginMsg, ""); Reset(np1%s); '
            'Reset(np2%s)' % (K, K), kind="secondary", size=14, radius=12, visible=SET),
        btn("rs" + K, '"Send Request"', 60, 340, 280, 50, reg, size=14, radius=12, visible=REG),
        btn("rb" + K, '"Back to Login"', 360, 340, 280, 50, 'Set(gLoginMode, "login"); Set(gLoginMsg, "")',
            kind="secondary", size=14, radius=12, visible=REG),
        lbl("f" + K, 'If(gLoginMode = "login", "Forgot your password? The Lab Lead can give you a temporary one.", '
                     '"Your password is stored scrambled; nobody can read it, not even the Lab Lead.")',
            40, 'If(%s, 404, 352)' % REG, 620, 22, size=10, color="cInk3", align="Center")]
    panel = box("pn" + K, 333, 150, 700, 'If(%s, 450, 400)' % REG, kids, fill="cGlass", border="cLine2", radius=24)
    kids = backdrop(K, "RGBA(8, 6, 10, 0.25)") + topbar(K, [
        btn("ck" + K, '"System Check"', 1020, 30, 150, 38, "Navigate(scrCheck, ScreenTransition.Fade)", kind="ghost",
            radius=19),
        btn("bk" + K, '"‹  Back"', 1180, 30, 140, 38, 'Set(gLoginMsg, ""); Navigate(scrWelcome, ScreenTransition.Fade)',
            kind="secondary", radius=19)]) + [panel]
    root = box("root" + K, 0, 0, 1366, 768, kids, fill="cBg", border="cBg", thick=0)
    SCREENS.append(("scrLogin", "", root))


CHECKS = [
    ("Users list", "Text(CountRows(tblUsers)) & \" people\""),
    ("Parts list", "Text(CountRows(tblParts)) & \" rows\""),
    ("Stock movements", "Text(CountRows(tblMoves)) & \" rows\""),
    ("Requests / request lines", "Text(CountRows(tblRequests)) & \" / \" & Text(CountRows(tblReqLines)) & \" rows\""),
    ("Settings", "Text(CountRows(tblSettings)) & \" rows\""),
    ("Formula engine (Power Fx 1.0)", "\"OK \" & First(Distinct(Table({x: 1}), x)).Value"),
    ("Parts read by the app", "Text(CountRows(nfParts)) & \" active parts\""),
    ("Movements read by the app", "Text(CountRows(nfMoves)) & \" movements\""),
    ("On-hand calculation", "Text(CountRows(nfOnHand)) & \" parts with movements\""),
    ("Live stock (Check Stock, BOM)", "Text(CountRows(nfStock)) & \" parts · \" & Text(CountRows(Filter(nfStock, OnHand > 0))) & \" in stock\""),
    ("Example: biggest stock", "With({p: First(Sort(nfStock, OnHand, SortOrder.Descending))}, p.PartNo & \" · on hand \" & Text(p.OnHand))"),
    ("Out of stock / low stock", "Text(CountRows(Filter(nfStock, Status = \"OUT OF STOCK\"))) & \" / \" & Text(CountRows(Filter(nfStock, Status = \"LOW STOCK\")))"),
    ("Requests view", "Text(CountRows(nfReqView)) & \" requests\""),
    ("Row count check", "nfHealthText"),
    ("Last refresh", "Text(gLastSync, \"dd-mmm-yyyy hh:mm:ss\")"),
]


def scr_check():
    """System Check: every link from the data file to the screens, each in its own formula so a broken link
    cannot hide the others. Reachable before login (Login screen) and from About."""
    K = "Ck"
    rows = []
    for i, (name, f) in enumerate(CHECKS):
        y = 118 + i * 33
        v = "v%d%s" % (i, K)
        rows += [lbl("n%d%s" % (i, K), q(name), 40, y, 300, 30, size=11, bold=True, color="cInk"),
                 lbl(v, 'IfError(%s, "Error: " & FirstError.Message)' % f, 350, y, 520, 30, size=11, color="cInk2"),
                 lbl("s%d%s" % (i, K), 'If(IsBlank(%s.Text), "NOT WORKING", StartsWith(%s.Text, "Error"), "ERROR", "OK")'
                     % (v, v), 900, y + 4, 130, 22, size=9, bold=True, align="Center",
                     color='If(IsBlank(%s.Text) || StartsWith(%s.Text, "Error"), cStop, cOk)' % (v, v),
                     extra={"BorderColor": 'If(IsBlank(%s.Text) || StartsWith(%s.Text, "Error"), cStop, cOk)' % (v, v),
                            "BorderThickness": 1}),
                 rect("l%d%s" % (i, K), 40, y + 31, 990, 1, "cLine")]
    panel = box("pn" + K, 158, 50, 1070, 690, [
        lbl("t" + K, '"System Check"', 40, 22, 600, 40, size=24, bold=True, color="cOrange"),
        lbl("s" + K, '"Every link from the data file to the screens. All rows must show OK. If one does not, take a '
                     'screenshot of this page and send it."', 40, 62, 980, 40, size=11, color="cInk2", wrap=True,
            valign="Top")] + rows + [
        btn("rf" + K, '"Refresh All Data"', 40, 628, 200, 40, REFRESH_ALL + '; Notify("Refreshed at " & '
            'Text(Now(), "hh:mm:ss") & ".", NotificationType.Information)', radius=20),
        btn("bk" + K, '"‹  Back"', 256, 628, 140, 40, "Back()", kind="secondary", radius=20)],
        fill="cGlass", border="cLine2", radius=24)
    kids = backdrop(K, "RGBA(8, 6, 10, 0.55)") + [panel]
    root = box("root" + K, 0, 0, 1366, 768, kids, fill="cBg", border="cBg", thick=0)
    SCREENS.append(("scrCheck", "", root))


def scr_about():
    K = "Ab"
    about = card("cdA" + K, "About Us", 250, [
        lbl("t" + K, '"The Electrical Development (EDS) Lab at JCB India, Pune builds and tests prototype wiring harnesses '
                     'and electrical systems for new machines. Every build needs the right connectors, terminals, wire and '
                     'tools on the shelf at the right time."', 16, 58, 1050, 60, size=13, color="cInk", wrap=True, valign="Top"),
        lbl("t2" + K, '"This portal is how the lab runs its material: engineers check stock and raise requests from a BOM, '
                     'the Lab Admin reserves and releases parts, managers approve and follow spend and deliveries."', 16, 124, 1050, 60, size=12,
            color="cInk2", wrap=True, valign="Top"),
        lbl("t3" + K, '"Version 2.0  ·  October 2026"', 16, 200, 800, 30,
            size=10, color="cInk3")])
    feats = tiles("ft" + K, [
        ("a", "Live Stock", '"Sum of Movements"', '"Never typed in, so it can never drift from the ledger"'),
        ("g", "Request to Release", '"Reserve · Release"', '"Shortfalls go straight to Ongoing Purchase"'),
        ("b", "Approvals", '"Admin + Manager"', '"Requests, brand new parts and PRs"'),
        ("w", "Cost and Invoices", '"Finance-Locked"', '"Cost sheet and invoice from the same numbers"')], h=110)
    for c in feats.children:
        for k in c.children:
            if k.name.endswith("V"):
                k.props["Size"] = 14
    hrows = ('Table({Check: "Parts rows", Excel: nXlParts, App: nAppParts, Ok: nXlParts = nAppParts, '
             'Fix: "Data row limit too low, or tblParts not connected"}, '
             '{Check: "Movement rows", Excel: nXlMoves, App: nAppMoves, Ok: nXlMoves = nAppMoves, '
             'Fix: "Set Settings > Data row limit to 2000"}, '
             '{Check: "Stock total (all parts)", Excel: nXlStock, App: nAppStock, Ok: Abs(nXlStock - nAppStock) < 0.001, '
             'Fix: "A movement row was not read, or has a Type the app does not know"})')
    hc = card("cdH" + K, "Data Health: Is the App Reading All of Excel?", 330, [
        lbl("hs" + K, '"The workbook counts its own rows with Excel formulas (Settings tab). The app counts what it '
                      'actually read. Both columns must match; then every stock figure in the app is the same as Excel."',
            16, 54, 1050, 40, size=11, color="cInk2", wrap=True, valign="Top")]
        + table("hl" + K, hrows, [
            Col("Check", 260, "ThisItem.Check", bold=True),
            Col("In Excel", 140, 'If(IsBlank(ThisItem.Excel), "Not set up", ' + num("ThisItem.Excel", 0) + ')',
                align="Right"),
            Col("Read by the App", 160, num("ThisItem.App", 0), align="Right", bold=True),
            Col("", 30, '""'),
            Col("Result", 120, 'If(IsBlank(ThisItem.Excel), "NOT SET UP", ThisItem.Ok, "OK", "ISSUES")', "pill"),
            Col("If Not OK", None, 'If(ThisItem.Ok, "—", ThisItem.Fix)', "muted")], y=100, h=158, row_h=40) + [
        lbl("hsy" + K, '"Last read from Excel at " & Text(gLastSync, "hh:mm:ss") & ". The app re-reads stock every 2 minutes '
                       'and before every BOM compare."', 16, 270, 700, 40, size=11, color="cInk3", wrap=True),
        btn("hck" + K, '"Open System Check"', "Parent.Width - 392", 274, 180, 38, "Navigate(scrCheck, ScreenTransition.Fade)",
            kind="secondary"),
        btn("hrf" + K, '"Re-read Excel Now"', "Parent.Width - 196", 274, 180, 38, REFRESH_ALL + '; Notify(nfHealthText & ".", '
            'If(nfHealthOk, NotificationType.Success, NotificationType.Warning))')])
    P = "LookUp(nfStock, PN = Upper(Trim(pq%s.Text)))" % K
    one = card("cdO" + K, "Check One Part Against Excel", 200, [
        lbl("os" + K, '"Type a part number and compare these figures with the LiveStock tab in Excel."', 16, 54, 700, 22,
            size=11, color="cInk2"),
        inp("pq" + K, 16, 86, 300, 38, hint="Part number, for example 7219/0373", font=MONO),
        lbl("or" + K, 'If(IsBlank(Trim(pq%s.Text)), "", IsBlank(%s), "Not in the catalogue (or retired).", '
                      '%s.PartNo & "  ·  on hand " & %s & "  ·  reserved " & %s & "  ·  available " & %s & "  ·  from " & '
                      'CountRows(Filter(nfMoves, PN = %s.PN)) & " movement rows")'
            % (K, P, P, num(P + ".OnHand", 0), num(P + ".Reserved", 0), num(P + ".Avail", 0), P),
            332, 86, 740, 38, size=12, bold=True, color="cJcb"),
        lbl("on" + K, '"On hand is the sum of the Movements rows for that part: receipts, returns and adjustments up, '
                      'issues, scrap and adjustments down."', 16, 136, 1000, 40, size=10, color="cInk3", wrap=True)])
    photo = card("cdP" + K, "Photo Storage Check", 150, [
        lbl("ps" + K, '"Harness label photos are saved to OneDrive > EDS Lab Portal Photos. Press Test to confirm the '
                      'folder and the OneDrive connection work for you."', 16, 54, 760, 40, size=11, color="cInk2",
            wrap=True, valign="Top"),
        lbl("pr" + K, "gPhotoCheck", 16, 98, 820, 36, size=11, bold=True,
            color='If(StartsWith(gPhotoCheck, "OK"), cOk, cWarn)', wrap=True),
        btn("pt" + K, '"Test Photo Storage"', "Parent.Width - 196", 56, 180, 38,
            'Set(gPhotoCheck, IfError("OK: folder found at " & OneDriveForBusiness.GetFileMetadataByPath('
            '"/EDS Lab Portal Photos").Path & ". Photos will save.", "Problem: " & FirstError.Message & '
            '". Create the folder EDS Lab Portal Photos in your OneDrive and make sure the OneDrive for Business '
            'connection is added (Data panel)."))', kind="secondary")])
    roles = card("cdR" + K, "How Roles Work", 190, [
        lbl("r1" + K, '"Engineer"', 16, 56, 200, 24, size=12, bold=True, color="cJcb"),
        lbl("r1t" + K, '"Checks stock, compares a BOM, raises requests and brand new parts, follows them to release."',
            220, 56, 850, 24, size=11, color="cInk2"),
        lbl("r2" + K, '"Lab Admin / Lab Lead"', 16, 88, 200, 24, size=12, bold=True, color="cJcb"),
        lbl("r2t" + K, '"Approves, reserves and releases material, receives stock, invoices, purchasing, team access. '
                       'Can view every role."', 220, 88, 850, 40, size=11, color="cInk2", wrap=True, valign="Top"),
        lbl("r3" + K, '"Manager"', 16, 136, 200, 24, size=12, bold=True, color="cJcb"),
        lbl("r3t" + K, '"Approves requests, brand new parts and PRs; dashboards for revenue, spend and deliveries. '
                       'Can also work as an Engineer."', 220, 136, 850, 40, size=11, color="cInk2", wrap=True, valign="Top")])
    for c_ in (hc, one, photo):      # back-office checks: Lab Admin / Lab Lead only
        c_.props["Visible"] = ADMIN
    content = [head(K, '"About"', 'If(%s, "Who we are, what this portal does, and checks that the data is complete", '
                                  '"Who we are and what this portal does")' % ADMIN),
               about, feats, hc, one, photo, roles]
    shell(K, "scrAbout", "about", content)


def build_all():
    SCREENS.clear()
    for f in (scr_welcome, scr_login, scr_dash, scr_mgr, scr_stock, scr_bom, scr_newreq, scr_myreq, scr_reqdetail, scr_queue, scr_newpart,
              scr_newpartq, scr_inventory, scr_inward, scr_ledger, scr_demand, scr_invoice, scr_invlist, scr_cost,
              scr_print, scr_proc, scr_purch, scr_lic, scr_team, scr_about, scr_check):
        f()
    return SCREENS
