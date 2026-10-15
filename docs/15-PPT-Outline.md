# Management deck: EDS Lab Material Portal, Phase 1 walkthrough (draft wording)

16:9, JCB template. 16 main slides + appendix (index slide + one slide per page, 37 in all).
Built as one offline HTML deck: `python3 tools/deck/build_deck.py` → `docs/deck/EDS-Portal-Walkthrough.html`;
wording in `tools/deck/slides.py`; screenshots + PDF: `node tools/deck/shoot_deck.js <html> <pngDir> [pdf]`.
Keys: → / Space next hotspot or slide, ← back, N notes, H home; Appendix button jumps to the index. Every screen slide = app screenshot with numbered yellow callouts on the
buttons + a "Click → What happens → Result" panel. Speaker notes under each slide.

---

## 1 · Title (JCB title master)
**EDS LAB MATERIAL PORTAL**
Sub-heading 1: Phase 1 walkthrough · Engineer to Lab Admin
Sub-heading 2: Gaurav Shelke · EDS Lab, Pune · October 2026
> Notes: Today I'll show every page of the new portal and exactly what happens on each click, using real lab data.

## 2 · Why we built it
- Today: stock checked by hand in Excel, BOMs compared line by line, requests by mail / word of mouth.
- Portal: one place for live stock, BOM check in seconds, and every material request from submission to release.
- Runs on Microsoft Power Apps + the lab's Excel workbook in OneDrive. No new licence, no server.
- Four roles: Engineer · Lab Admin · Lab Lead · Manager. Each sees only their pages.
> Notes: Nothing new to install; it opens in the browser or Teams with the company login.

## 3 · Phase 1 at a glance (flow diagram)
Log In → Check Stock → BOM Compare → Raise Request → My Requests → Lab Admin Queue
Each box shows a small screenshot. Footer: "About 2 minutes from BOM to request."
> Notes: This is the flow management asked for. The next slides walk through each box.

## 4 · Welcome page (01-welcome)
1 **Log In** → opens the login page · 2 **Request Access** → new person asks for an account
Result: nobody sees lab data before logging in.
> Notes: First screen for everyone. The version number bottom right tells us which build is installed.

## 5 · Login (02-login)
1 Username · 2 Password (eye icon shows/hides it) · 3 **Login** → dashboard for your role ·
4 **Forgot Password?** → choose a new one · 5 **Register** → request access · 6 **System Check** → health of the data links
Result: Engineer lands on the Engineer dashboard.
> Notes: Kept simple on purpose: username and password, self-service password reset.

## 6 · Engineer dashboard (03-engineer-dashboard)
1 Greeting + role · 2 Tiles: my open requests, components, low stock, out of stock ·
3 Your Requests (click a row → its detail) · 4 Menu: only engineer pages · 5 Live · Synced (click = refresh now)
Result: an engineer sees their status at a glance.
> Notes: Data refreshes itself every 2 minutes; the green pill shows the last sync.

## 7 · Check Stock (04-check-stock)
1 Search part / description / location · 2 Category and status filters ·
3 Columns: on hand, reserved, available, status pill
Result: live stock for any of the 418 parts in seconds.
> Notes: On hand is calculated from every stock movement, so it can't drift from the store records.

## 8 · BOM Compare · paste and compare (05-bom-compare) ★ sample
1 Paste the BOM rows from Excel · 2 **Compare Against Stock** · 3 Summary line ·
4 Result tiles · 5 Status per line · 6 **Raise Part Request ›**
Result: in seconds the engineer knows what the store can supply and what must be bought.
> Notes: Copy straight from the harness BOM in Excel: Sr, description and units are understood.
> New Part means the lab has never stocked it, different from out of stock.

## 9 · New Request (06-new-request-filled)
1 Project information (machine, project code, harness, stage, BU, contacts, circuits, required by, scope) ·
2 BOM lines carried over from the comparison · 3 **Submit Request**
Result: request number REQ-YYYY-NNNNN created, lines saved, green confirmation.
> Notes: Mandatory fields are checked before saving; nothing half-saved.

## 10 · My Requests (07-my-requests)
1 Green banner "REQ-… is with the store" · 2 The new request at the top, status Submitted ·
3 Click the row → full detail
Result: the engineer can track every request without asking the store.

## 11 · Request detail, engineer view (08-engineer-request-detail)
1 Header facts · 2 Line-by-line: requested, available, reserved, released, short · 3 History log
Result: full transparency for the requester.

## 12 · Lab Admin dashboard (09-lab-admin-dashboard)
1 Needs Your Action list (the new request) · 2 Request Queue badge = 1 · 3 Stock and purchase tiles
Result: the store sees new work the moment it is submitted.

## 13 · Request Queue → Request detail (10 + 11)
1 Queue with filters · 2 Open the request · 3 **Approve** / **Reject** · 4 **Reserve Available Stock** · 5 Short column
Result: the Lab Admin can act immediately; shortfalls go to the purchase list.
> Notes: Phase 1 ends here. Release, invoice and procurement are already built (next slides).

## 14 · Other pages (1/2) · thumbnail grid ★ sample
Component Inventory · Material Inward · Stock Transactions · High Demand Parts · Brand New Purchase Part · New Purchase Parts queue
(one line each: what it is for)

## 15 · Other pages (2/2) · thumbnail grid
Create Invoice · Invoices · Cost Sheet · Procurement (PR/PO) · Ongoing Purchase · Software Licenses · Team Access · Manager Dashboard · System Check

## 16 · Next steps
- Phase 1 pilot with 3 engineers + Lab Admin (2 weeks).
- Phase 2: reserve → release → invoice live; manager dashboards.
- Later: move data from Excel to a SharePoint list for more users and rows.
- Ask: approval to pilot.

## 17 · Appendix index (click a page to jump)
## 18–37 · One slide per page
Register · Set or reset password · System Check · Request Queue · Component Inventory · Material Inward ·
Stock Transactions · High Demand Parts · Brand New Purchase Part · New Purchase Parts · Create Invoice · Invoices ·
Cost Sheet · Procurement · Ongoing Purchase · Software Licenses · Team Access · Manager Dashboard ·
About / Data Health · Print / PDF. Same layout: screenshot, numbered hotspots, Click → What happens, Result.
