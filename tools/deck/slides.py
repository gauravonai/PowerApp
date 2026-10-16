"""Wording of the management deck (docs/15-PPT-Outline.md): 16 main slides + appendix with every page.

Screen slides: image key "p1:<file>" = Phase 1 walkthrough shots (tools/out/p1png, controls in tools/out/phase1),
"all:<screen>" = per-screen shots (tools/out/png, controls in tools/out/render).
Spot = (where, heading, text). where = control name, (name, n-th match), (x, y, w, h) in app pixels, or None
(item listed without a dot, e.g. a button further down the page).
"""

MAIN = "EDS Lab Material Portal · Phase 1"


def screen(title, kicker, img, spots, result, notes, y0=60, x0=224, x1=1366, step=None, wide=False):
    return {"wide": wide, "kind": "screen", "title": title, "kicker": kicker, "img": img, "spots": spots, "result": result,
            "notes": notes, "y0": y0, "x0": x0, "x1": x1, "step": step}


SLIDES = [
    # ------------------------------------------------------------------ 1
    {"kind": "title", "title": "EDS Lab Material Portal", "sub": "Phase 1 walkthrough · Engineer to Lab Admin",
     "who": "Gaurav Shelke · EDS Lab, Pune", "when": "October 2026",
     "notes": "Today I will show every page of the new portal and exactly what happens on each click, using real lab data."},
    # ------------------------------------------------------------------ 2
    {"kind": "bullets", "title": "Why we built it", "kicker": "The problem and the answer",
     "cols": [("Today", ["Stock checked by hand in the Excel sheet.",
                         "Harness BOMs compared with stock line by line.",
                         "Requests by mail or word of mouth; no status for the engineer.",
                         "Nobody sees at a glance what is short and what is on order."]),
              ("With the portal", ["One place for live stock, calculated from every movement.",
                                   "Paste a BOM and see the gaps in seconds.",
                                   "Every request tracked from submission to release.",
                                   "Each role sees only its own pages: Engineer, Lab Admin, Lab Lead, Manager."])],
     "banner": "Runs in Power Apps on the lab's existing workbook. No new licence, no server; opens in the browser or Teams.",
     "notes": "Nothing new to install; it opens in the browser or Teams with the company login."},
    # ------------------------------------------------------------------ 3
    {"kind": "flow", "kicker": "Phase 1 · the flow", "title": "Phase 1 at a glance", "lead": "Engineer to Lab Admin in about 2 minutes, on live lab stock.",
     "steps": [("Log In", "02-login-engineer.png", "Username and password"),
               ("Check Stock", "04-check-stock.png", "Live on hand for every part"),
               ("BOM Compare", "05-bom-compare.png", "Paste the Excel BOM, see the gaps"),
               ("Raise Request", "06-new-request-filled.png", "Project details and BOM lines"),
               ("My Requests", "07-my-requests.png", "Track status any time"),
               ("Lab Admin", "10-lab-admin-queue.png", "Store sees it instantly")],
     "banner": "Tested end to end on the lab's real data before every release: login, stock search, BOM paste, "
               "request saved, Lab Admin sees it.",
     "notes": "This is the flow management asked for. The next slides walk through each step."},
    # ------------------------------------------------------------------ 4
    screen("Welcome page", "Start · everyone", "p1:01-welcome.png", [
        ("goWl", "Log In", "Opens the login page."),
        ("rgWl", "Request Access", "A new person asks for an account; the Lab Admin gives the role."),
        ("ch1Wl", "What the portal does", "Live stock, BOM compare and request tracking, in one line.")],
        "Nobody sees lab data before logging in.",
        "First screen for everyone. The version number bottom right tells us which build is installed.",
        y0=0, x0=0, x1=1366, wide=True),
    # ------------------------------------------------------------------ 5
    screen("Login page", "Step 1 of 6 · Engineer", "p1:02-login-engineer.png", [
        ((630, 306, 360, 48), "Username", "The name the Lab Admin set up, e.g. akshay.kakde."),
        ((630, 366, 360, 48), "Password", "Eye icon shows or hides it. Empty password? You choose one on first login."),
        ("goLi", "Login", "Opens the dashboard for your role."),
        ("fgLi", "Forgot Password?", "Type your username and set a new password. No waiting for anyone."),
        ("rgLi", "Register", "New user fills name, username and password; role starts as Pending."),
        ("ckLi", "System Check", "18 health checks of the data links, for support.")],
        "The engineer lands on the Engineer dashboard.",
        "Kept simple on purpose: username and password, self-service password reset.",
        y0=0, x0=0, x1=1366, step=1, wide=True),
    # ------------------------------------------------------------------ 6
    screen("Engineer dashboard", "Step 1 of 6 · Engineer", "p1:03-engineer-dashboard.png", [
        ("hdTDsh", "Greeting", "Good morning plus the person's name and role."),
        ("tiCDsh", "Tiles", "My open requests, parts in catalogue, low stock, out of stock."),
        ("cdReqDsh", "Your Requests", "Each row opens the request detail. Open All lists everything."),
        ((10, 100, 204, 340), "Menu", "Only the pages an engineer needs."),
        ("hdrSyncDsh", "Live · Synced", "Data refreshes itself; click to refresh now."),
        ("hdrOutDsh", "Log Out", "Back to the login page.")],
        "An engineer sees their status at a glance.",
        "Data refreshes itself every 2 minutes; the green pill shows the last sync.",
        y0=0, x0=0, x1=1366, step=1),
    # ------------------------------------------------------------------ 7
    screen("Check Stock", "Step 2 of 6 · Engineer", "p1:04-check-stock.png", [
        ("qStk", "Search", "Part number, description or store location; results as you type."),
        ("cStk", "Category filter", "Wires, connectors, relays and so on."),
        ("sStk", "Status filter", "In stock, low, out of stock."),
        ((888, 227, 204, 120), "On hand · Reserved · Available", "Available = on hand minus what is reserved for requests."),
        ("stStkH8", "Status pill", "Green in stock, amber low, red out of stock.")],
        "Live stock for any of the 418 parts in seconds.",
        "On hand is calculated from every stock movement, so it cannot drift from the store records.",
        y0=70, step=2),
    # ------------------------------------------------------------------ 8
    screen("BOM Compare", "Step 3 of 6 · Engineer", "p1:05-bom-compare.png", [
        ("txtBom", "Paste the BOM",
         "Copy the rows straight from the Excel BOM: Sr, part number, description, qty. Units like NOS are fine."),
        ("goBom", "Compare Against Stock", "The app re-reads the latest stock and checks every line of the BOM."),
        ((826, 365, 500, 48), "Summary line", "How many lines were read, parts compared, found in stock and new parts."),
        ("tiBom", "Result tiles", "Available today, short, new parts and the estimated material value."),
        ((1150, 606, 170, 160), "Status per line", "Available · Shortage · Out of Stock · New Part, with on hand, reserved and short."),
        ("reqBom", "Raise Part Request ›", "Opens New Request with these lines already filled in.")],
        "In seconds the engineer knows what the store can supply and what must be bought.",
        "Copy straight from the harness BOM in Excel. New Part means the lab has never stocked it; "
        "that is different from out of stock.", y0=80, step=3),
    # ------------------------------------------------------------------ 9
    screen("New Request", "Step 4 of 6 · Engineer", "p1:06-new-request-filled.png", [
        ((266, 240, 1060, 360), "Project information", "Machine, project code, harness, stage, BU, cost centre, contacts, circuits, scope."),
        ("stageNr", "Drop-downs", "Stage and business unit are picked, not typed, so reports stay clean."),
        ("cdBNr", "BOM lines", "Carried over from BOM Compare; the title says how many need purchasing."),
        ("editNr", "Edit BOM", "Back to BOM Compare to change lines."),
        ("subNr", "Submit Request", "Mandatory fields checked, request number REQ-YYYY-NNNNN created, lines saved.")],
        "Request saved with all lines; green confirmation and the engineer lands on My Requests.",
        "Mandatory fields are checked before saving; nothing is half-saved.", y0=200, step=4),
    # ------------------------------------------------------------------ 10
    screen("My Requests", "Step 5 of 6 · Engineer", "p1:07-my-requests.png", [
        ("stMy", "Status filter", "Submitted, approved, ready, released, completed."),
        ("qMy", "Search", "Request, harness, machine or requester."),
        (("rlMyGo", 0), "The new request", "At the top, status Submitted, with lines and short count. Click → full detail."),
        ("navCntMy", "Badge", "How many of my requests are still open.")],
        "The engineer can track every request without asking the store.",
        "A green banner confirms REQ-... is with the store as soon as it is saved.", y0=70, x0=0, step=5),
    # ------------------------------------------------------------------ 11
    screen("Request detail · engineer view", "Step 5 of 6 · Engineer", "p1:08-engineer-request-detail.png", [
        ("stPRd", "Status", "Where the request is now: Submitted, Approved, Ready, Released."),
        ((266, 263, 1050, 240), "Header facts", "Requester, harness, project, BU, contacts, required-by date, scope."),
        ((606, 577, 290, 330), "Line by line", "Requested, available, reserved, released and short per part."),
        ("lnRdH8", "Line status", "Available, Partial, Shortage or New Part."),
        ("bkRd", "Back", "Returns to My Requests.")],
        "Full transparency for the requester: no calls to the store needed.",
        "The engineer sees exactly the same numbers the store sees, read-only.", y0=80, step=5),
    # ------------------------------------------------------------------ 12
    screen("Lab Admin dashboard", "Step 6 of 6 · Lab Admin", "p1:09-lab-admin-dashboard.png", [
        ("tiADsh", "Store tiles", "Open requests, ready to release, purchase required, out of stock, low stock."),
        ("tiBDsh", "Purchase and money", "PRs and POs in progress, licenses needing attention, stock value."),
        ("cdReqDsh", "Needs Your Action", "The engineer's new request is here the moment it is saved."),
        ("navCntDsh", "Request Queue badge", "Shows 1: one request waiting."),
        ("hdrAsDsh", "View as", "People with two roles switch view here.")],
        "The store sees new work the moment it is submitted.",
        "Same login page; the role decides which dashboard and menu appear.", y0=0, x0=0, x1=1366, step=6),
    # ------------------------------------------------------------------ 13
    screen("Request detail · Lab Admin", "Step 6 of 6 · Lab Admin", "p1:11-lab-admin-request-detail.png", [
        ("rejRd", "Reject", "Closes it with a reason in the history; the engineer still sees the record."),
        ("aprRd", "Approve", "Moves to Approved; the store can now reserve and release."),
        ("resRd", "Reserve Available Stock", "Holds what is free for this request; what is short goes to Ongoing Purchase."),
        ("lnRdH6", "Short column", "What the store cannot supply today."),
        (("lnRdC8b", 0), "Request Separately", "Splits a shortfall into its own request so the rest can be released."),
        ("circSvRd", "Save circuits", "Lab Admin corrects the circuit count used for the cost.")],
        "The Lab Admin can act immediately; shortfalls go to the purchase list automatically.",
        "Phase 1 ends here. Release, invoice and procurement are already built: see the next slides and the appendix.",
        y0=200, step=6),
    # ------------------------------------------------------------------ 14
    {"kind": "grid", "kicker": "Already built · store", "title": "Other pages (1 of 2)", "foot": "Store pages · already built",
     "items": [("Component Inventory", "scrInventory.png", "Full catalogue with store locations; Lab Admin edits locations."),
               ("Material Inward", "scrInward.png", "Book goods received (PO, FOC, return, scrap); stock updates at once."),
               ("Stock Transactions", "scrLedger.png", "Every movement with date, reference and who issued it."),
               ("High Demand Parts", "scrDemand.png", "Most-issued parts for the chosen period, to plan buying."),
               ("Brand New Purchase Part", "scrNewPart.png", "Engineer asks the lab to buy a part it has never stocked."),
               ("New Purchase Parts", "scrNewPartQ.png", "Lab Admin and Manager approve or reject those requests.")],
     "notes": "These pages are built and tested; they roll out after Phase 1. Each one is in the appendix in detail."},
    # ------------------------------------------------------------------ 15
    {"kind": "grid", "kicker": "Already built · money and admin", "title": "Other pages (2 of 2)", "foot": "Money, purchasing and admin · already built",
     "items": [("Create Invoice", "scrInvoice.png", "Job card for a released request; finance-locked cost formula."),
               ("Invoices", "scrInvList.png", "Every invoice raised; open, edit or issue."),
               ("Cost Sheet", "scrCost.png", "Quote a harness job: paste part, qty, cost."),
               ("Procurement (PR/PO)", "scrProc.png", "PR to PO to delivery, one click per stage."),
               ("Ongoing Purchase", "scrPurch.png", "All shortfalls in one list; what is on order."),
               ("Software Licenses", "scrLic.png", "Seats, renewal dates and yearly cost."),
               ("Team Access", "scrTeam.png", "Roles, new people, password reset."),
               ("Manager Dashboard", "scrMgrDash.png", "Approvals, revenue, purchases, projects."),
               ("System Check", "scrCheck.png", "18 health checks of the data links.")],
     "notes": "Second half of the app. Ask me to open any one; the appendix has a slide per page."},
    # ------------------------------------------------------------------ 16
    {"kind": "bullets", "title": "Next steps", "kicker": "What we ask today",
     "cols": [("Plan", ["Phase 1 pilot: 3 engineers + Lab Admin, 2 weeks.",
                        "Phase 2: reserve → release → invoice live; manager dashboard.",
                        "Later: move the data from Excel to a SharePoint list for more users and rows."]),
              ("Ask", ["Approval to start the Phase 1 pilot.",
                       "Names of the 3 pilot engineers.",
                       "Review meeting at the end of the 2 weeks."])],
     "banner": "Appendix: one slide for every page of the app, for questions.",
     "notes": "Close here. Use the appendix only when someone asks about a page."},
]

APPENDIX = [
    screen("Register", "Appendix · Login", "all:scrLogin-register.png", [
        ("rgNLi", "Full Name", "Shown on requests and the dashboard greeting."),
        ("rgULi", "Username", "What the person logs in with."),
        ("rgMLi", "Business Unit · Email", "Optional; used on reports."),
        ("rgP1Li", "Password + confirm", "At least 4 characters."),
        ("rsLi", "Send Request", "Adds the person with role Pending; the Lab Admin sets the role in Team Access."),
        ("rbLi", "Back to Login", "Cancels.")],
        "New people get in without a form or a mail chain.",
        "Pending people cannot log in until the Lab Admin gives them a role in Team Access.", y0=100, x0=560, x1=1366),
    screen("Set or reset password", "Appendix · Login", "all:scrLogin-setpw.png", [
        ("np1Li", "New password", "At least 4 characters."),
        ("np2Li", "Confirm", "Must match."),
        ("spLi", "Save and Log In", "Password saved scrambled; the person goes straight in."),
        ("sxLi", "Cancel", "Back to the login box.")],
        "Forgot Password and first login both end here. No waiting for an admin.",
        "Shown after Forgot Password? or when the Password cell is empty.", y0=100, x0=560, x1=1366),
    screen("System Check", "Appendix · Support", "all:scrCheck.png", [
        ((198, 150, 1000, 520), "18 checks", "Every table connected and read, stock calculation, BOM reader test, last refresh."),
        ("s0Ck", "OK per row", "Any row not OK points to the exact problem."),
        ("rfCk", "Refresh All Data", "Re-reads every table now."),
        ("bkCk", "Back", "Returns to the login page.")],
        "One screenshot tells support what is wrong.",
        "Reachable from the login page, before logging in.", y0=60, x0=150, x1=1260),
    screen("Request Queue", "Appendix · Lab Admin", "p1:10-lab-admin-queue.png", [
        ("stQu", "Status filter", "Submitted, approved, ready for release, purchase required…"),
        ("qQu", "Search", "Request, harness, machine or requester."),
        ((250, 257, 1078, 46), "Request row", "Lines, short count, status, date. Click → request detail."),
        ("navCntQu", "Badge", "Requests waiting for action.")],
        "The store's to-do list, oldest first.",
        "Every request from every engineer, in one list.", y0=70, x0=0),
    screen("Component Inventory", "Appendix · Lab Admin", "all:scrInventory.png", [
        ("qInv", "Search", "Part, description or location."),
        ("dqInv", "Data quality filter", "Finds parts with missing or odd data in the sheet."),
        (("stInvC3", 0), "Location", "Lab Admin types the shelf location in the row; saved at once."),
        ("addInv", "+ Add Part", "Part number, description, category, UOM, location, supplier, cost."),
        ("retInv", "Retire Part", "Takes an obsolete part out of the active list.")],
        "The catalogue stays correct without opening Excel.",
        "418 active parts in the current data.", y0=70),
    screen("Material Inward", "Appendix · Lab Admin", "all:scrInward.png", [
        ("pnIn", "Part number", "Checked against the catalogue as you type."),
        ("qtyIn", "Quantity", "Must be more than zero."),
        ("typIn", "Type", "PO, FOC, Return, Adjust+, Adjust−, Scrap."),
        ("refIn", "Reference", "PO number or note."),
        ("rsnIn", "Reason", "Required for adjustments and scrap."),
        ("goIn", "Record Receipt", "Adds a stock movement; on hand updates at once.")],
        "Stock goes up only through this page, so every unit is traceable.",
        "Removing more than is physically in store is refused.", y0=70),
    screen("Stock Transactions", "Appendix · Lab Admin", "all:scrLedger.png", [
        ("qLg", "Search", "Part, harness, machine, person or reference."),
        ("tyLg", "Type filter", "Receipt, release, return, adjustments, scrap."),
        ("clrLg", "Clear", "Resets the filters."),
        ("lgLgGal", "Ledger", "Date, part, quantity, reference, unit cost and who did it.")],
        "Full audit trail of every unit in and out.",
        "This is what on hand is calculated from.", y0=70),
    screen("High Demand Parts", "Appendix · Lab Admin", "all:scrDemand.png", [
        ("pDm", "Period", "Last 90 days, 180 days, 12 months or everything."),
        ("qDm", "Search", "Part or description."),
        ("dmDmGal", "Ranking", "Most-issued parts first, with stock status and last issue date.")],
        "Buy ahead for the parts every build uses.",
        "Opens on the last 12 months.", y0=70),
    screen("Brand New Purchase Part", "Appendix · Engineer", "all:scrNewPart.png", [
        ("cdFNp", "Part details", "Name, category, make, model, UOM, HSN, specs."),
        ("fmAddNp", "Add to List", "Several new parts in one request."),
        ("nlNpGal", "Parts in this request", "Edit or remove before sending."),
        ("goNp", "Submit to Store", "Numbered request goes to the New Purchase Parts queue."),
        ("cdMNp", "Your New Part Requests", "Status of everything you asked for.")],
        "Engineers ask for parts the lab has never stocked, in a fixed format.",
        "Replaces the separate Excel form.", y0=160),
    screen("New Purchase Parts", "Appendix · Lab Admin / Manager", "all:scrNewPartQ.png", [
        ("stNq", "Status filter", "Submitted, approved, rejected, draft."),
        ("qNq", "Search", "Request, requester, part, make or HSN."),
        (("npNqC10", 0), "Approve", "Marked approved; add it to the catalogue once it has a part number."),
        (("npNqC10r", 0), "Reject", "Marked rejected; the engineer sees it.")],
        "Every new-part request is decided in one place.",
        "Manager approval also shows on the Manager dashboard.", y0=70),
    screen("Create Invoice", "Appendix · Lab Admin", "all:scrInvoice.png", [
        ("stIv", "Status", "Draft until it is issued."),
        ("frIv", "Pick the request", "Fills job details from a released request."),
        ("ldIv", "Load BOM from Request", "Material lines with qty and unit cost."),
        ("maIv", "+ Add Row", "Extra material by hand."),
        ("mgIv", "Material lines", "Qty × cost per line, total in the title."),
        (None, "Save Invoice · Print / PDF", "At the bottom: saves with a unique number and prints the job card.")],
        "Job invoice built from what was really released.",
        "The cost formula is finance-locked; only the inputs change.", y0=160),
    screen("Invoices", "Appendix · Lab Admin", "all:scrInvList.png", [
        ("tiIl", "Tiles", "Invoices, billed value, this financial year, drafts."),
        ("stIl", "Status filter", "Draft or issued."),
        ("qIl", "Search", "Invoice, BU, harness, request or recipient."),
        ("ivIlC9", "Open", "Read view and print."),
        ("ivIlC9e", "Edit", "Back to Create Invoice with its lines."),
        ("ivIlC9i", "Issue", "Marks it issued.")],
        "All lab invoices in one list.",
        "A new invoice can never reuse an existing number.", y0=70),
    screen("Cost Sheet", "Appendix · Lab Admin", "all:scrCost.png", [
        ("frCs", "Pick a job", "Request or invoice to cost."),
        ("onlyCs", "Input", "Number of circuits is the only field you change."),
        ("mgCs", "Material cost", "Part, qty, cost per unit, line cost."),
        ("maCs", "+ Add Row", "Extra lines."),
        ("bpCs", "Paste lines", "Part, qty, cost straight from Excel; Load These Lines."),
        (None, "Calculated · Print", "Below: labour and overheads from the finance-locked assumptions; print both.")],
        "A quote for a harness job in minutes.",
        "Assumptions are read-only; finance owns them.", y0=160),
    screen("Procurement (PR / PO)", "Appendix · Lab Admin", "all:scrProc.png", [
        ("tiPc", "Tiles", "PRs/POs in progress, purchase orders, FOC receipts, committed value."),
        ("newPc", "+ New PR / PO Entry", "PR number, summary, vendor, amount."),
        ("stPc", "Stage filter", "PR raised, approved, PO raised, GRN, delivered, rejected."),
        (("pcPcC8", 0), "Stage button", "One click moves it to the next stage."),
        (("pcPcC8r", 0), "Reject", "Closes the PR."),
        ("cdSPc", "Shortages waiting for a PR", "From open requests, so nothing is forgotten.")],
        "Every purchase tracked from PR to delivery.",
        "Manager sees the same stages on the Manager dashboard.", y0=70),
    screen("Ongoing Purchase", "Appendix · Lab Admin", "all:scrPurch.png", [
        ("tiPu", "Tiles", "Parts short now, on the purchase list, total shortfall qty."),
        ("pullPu", "Add All Shortfalls", "Puts every open shortfall on the purchase list."),
        (("bkPuC7", 0), "Add", "One part for one request."),
        ("stPu", "Stage filter", "Required, PR raised, PO raised, in transit, received."),
        (("ptPuC9", 0), "Edit", "Supplier, PR number, stage."),
        ("newPu", "+ New Purchase Line", "Buy something not tied to a request.")],
        "What is short across all requests, and what is already on order.",
        "One purchase row per part and request, so receipts go to the right job.", y0=70),
    screen("Software Licenses", "Appendix · Lab Admin", "all:scrLic.png", [
        ("tiLc", "Tiles", "Licenses tracked, need attention, seats in use, annual spend."),
        ("newLc", "+ Add License", "Name, vendor, seats, expiry, cost."),
        ("lcGal", "List", "Edit seats or dates in the row.")],
        "No renewal is missed.",
        "Seats used against seats bought.", y0=70),
    screen("Team Access", "Appendix · Lab Admin / Lab Lead", "all:scrTeam.png", [
        ("qTm", "Search", "Name, username, role, BU or email."),
        (("tmC2", 0), "Role", "Drop-down incl. combined roles like Engineer, Manager."),
        (("tmC1", 0), "Name · BU · Email", "Edit in the row."),
        (("tmC5", 0), "Password", "Set or Not Set; the password itself is never shown."),
        (("tmC6t", 0), "Reset Password", "Clears it; the person chooses a new one at next login."),
        ("newTm", "+ Add Person", "Creates the user directly.")],
        "Who can see what, managed without opening Excel.",
        "Pending registrations show here for a role.", y0=70),
    screen("Manager Dashboard", "Appendix · Manager", "all:scrMgrDash.png", [
        ("tiMgr", "Tiles", "Materials, licenses, low / out of stock, invoices, calibration due."),
        ("apRMgr", "Approval tabs", "Material requests, brand new parts, PRs."),
        ("apMgrGal", "Waiting for your approval", "Approve or reject in the row."),
        ("cdRevMgr", "Revenue", "Invoice value by business unit."),
        ("cdPrMgr", "Purchases", "PR / PO / delivered bars."),
        ("cdPjMgr", "Projects", "Ongoing and upcoming.")],
        "The manager's whole picture on one page.",
        "Read-only picture of the whole lab, plus the approvals that need a manager.", y0=160),
    screen("About · Data Health", "Appendix · Lab Admin", "all:scrAbout.png", [
        ("ftAb", "How it works", "Live stock, request to release, approvals, cost and invoices in four lines."),
        ("cdHAb", "Data Health", "Rows in the sheet vs rows the app reads."),
        ("hckAb", "Open System Check", "The 18-row check."),
        ("hrfAb", "Re-read Now", "Refresh every table."),
        ("pqAb", "Check one part", "Shows how one part number is read, to catch typing errors."),
        ("ptAb", "Test Photo Storage", "Confirms harness photos can be saved.")],
        "Admins can prove the data is complete without opening the workbook.",
        "Admin-only; ordinary users never see this page.", y0=420),
    screen("Print / PDF", "Appendix · Lab Admin", "all:scrPrint.png", [
        ("bkPr", "Back", "Returns to the invoice or cost sheet."),
        ("ppPr", "Print / Save as PDF", "Browser print: paper or PDF."),
        ((60, 420, 1240, 200), "Printable page", "White page with the job card or cost sheet tables.")],
        "Signed paper copy for the job file.",
        "Same layout as the Excel job card.", y0=0, x0=0, x1=1366),
]
