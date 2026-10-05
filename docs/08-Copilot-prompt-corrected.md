# Corrected context for Copilot in Power Apps (paste when asking Copilot to change the app)

Copy everything between the lines into Copilot (in Power Apps Studio) **before** your request. It
describes the app as it actually is, so Copilot's suggestions use the right names.

---
This is the "JCB EDS Lab Material Portal" canvas app (1366×768, dark theme). Data comes from an Excel
workbook through Excel Online (Business). Table names are fixed: tblParts, tblMoves, tblUsers, tblSettings,
tblProc, tblLicenses, tblNewPart, tblInvoice, tblPurch, tblCalib, tblRequests, tblReqLines.
Rows whose first column starts with "SAMPLE" are type-placeholder rows and must be ignored and never deleted.

Stock is never stored. tblMoves.Type is one of RECEIPT, RETURN, ADJUST+ (add) or ISSUE, SCRAP, ADJUST- (subtract),
and Qty is always positive. Releases are written as Type "ISSUE" with Reference = RequestNo and EntryId = "TXN-" & GUID.
Named formula nfStock gives every active part with OnHand, Reserved, Avail and Status (OUT OF STOCK / LOW STOCK /
FULLY RESERVED / IN STOCK; low = OnHand <= RefQty * % where % comes from Settings LowStockPct_Connector /
LowStockPct_Terminal / LowStockPct_Default keyed on SubCategory).

Request statuses: SUBMITTED, ADMIN REVIEW, PURCHASE REQUIRED, RESERVED, READY FOR RELEASE, PARTIALLY RELEASED,
RELEASED, COMPLETED, CANCELLED, REJECTED. Line statuses: AVAILABLE, PARTIAL, SHORTAGE, NEW PART, RELEASED.
Shortfall of a line = QtyRequested - Max(QtyReserved, QtyReleased). Every state change appends a JSON event
{t, by, a} to tblRequests.History (append, never overwrite). Request numbers REQ-YYYY-NNNNN, split shortfalls
SHT-YYYY-NNNNN (Kind SHORTAGE, ParentRequest set), new parts NPR-YYYY-NNNNN, invoices IDC EDS/{FY}/{NNN}.
Procurement stages: PR RAISED, APPROVED, PO RAISED, GRN IN PROGRESS, DELIVERED (CLOSED), REJECTED.
Ongoing purchase stages: REQUIRED, PR RAISED, PO RAISED, IN TRANSIT, RECEIVED.

Cost (Finance-locked): hours = circuits / 7.5; machine = 41800/3600*hours; manpower = 1239*hours;
electricity = 10*hours; assembly = machine+manpower+electricity; total = material + assembly + 200 transport.
AMC 50/h is shown but excluded.

Roles come from tblUsers.Role via nfRoleCanon: Lab Lead, Lab Admin, Manager, Engineer (unknown = Engineer).
The current role is in variable gRole. Admin-only controls use Visible = gRole in ["Lab Admin","Lab Lead"].
Theme colours are named formulas: cBg, cPanel, cPanel2, cSunk, cLine, cLine2, cInk, cInk2, cInk3, cJcb (#f2b01e),
cJcbDark, cJcbWash, cOnJcb, cSteel, cOk, cWarn, cStop. Fonts fMono and fUI. Status pills take colour from
LookUp(nfPill, K = Upper(status)).C.

Screens: scrDash, scrMgrDash, scrStock, scrBom, scrNewReq, scrMyReq, scrReqDetail, scrQueue, scrNewPart,
scrNewPartQ, scrInventory, scrInward, scrLedger, scrDemand, scrInvoice, scrInvList, scrCost, scrPrint, scrProc,
scrPurch, scrLic, scrTeam, scrNoAccess. Each has root<K> > body<K> (vertical auto-layout) > cards.
Write dates at noon: DateAdd(<date>, 12, TimeUnit.Hours). Never write a stock quantity anywhere.
Keep control names unique and keep the existing names; formulas refer to them.
---

Then ask, for example:
- *"On scrReqDetail add a danger button 'Cancel request' next to Reject, visible for admins when Status is
  SUBMITTED, that sets Status to CANCELLED and appends a History event."*
- *"On scrStock add a filter dropdown for Supplier."*
