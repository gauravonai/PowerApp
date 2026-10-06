# What follows the HTA, what differs, and a bug found in the HTA

Rule used throughout: **the working HTA v8 and the real workbook win** over the Copilot prompt text,
because you said the HTA "is perfect and aligns with Excel".

## 1. Where the Copilot prompt did not match the real system

| Topic | Copilot prompt said | Real workbook / HTA (what the app does) |
|---|---|---|
| Movement types | `RECEIPT, RELEASE, RETURN, ADJUST`, releases stored as **negative** Qty | `RECEIPT, RETURN, ADJUST+` add, `ISSUE, SCRAP, ADJUST-` subtract, **Qty always positive** (the LiveStock SUMIFS and the Movements dropdown use exactly these). The app writes `ISSUE` and shows it as "RELEASE", like the HTA |
| LiveStock | read it or replicate it | It isn't an Excel Table, so Power Apps **can't** read it. The app replicates it (verified equal for all 418 parts) |
| Low-stock % | by **Category** | by **SubCategory** (`Connector` 25 %, `Terminal` 20 %, others 20 %), as the HTA does. Note: the Excel LiveStock tab itself uses a flat 20 %, so a *connector* can show LOW in the app but IN STOCK in the Excel tab |
| Request statuses | Raised → In Progress → Short → Closed | `SUBMITTED → (Reserve) READY FOR RELEASE or PURCHASE REQUIRED → (Release) PARTIALLY RELEASED / RELEASED → COMPLETED`, plus `REJECTED` (HTA vocabulary, so both apps read the same rows the same way) |
| Line statuses | Pending/Reserved/Released/Short/Closed | `AVAILABLE, PARTIAL, SHORTAGE, NEW PART, RELEASED` (HTA) with the shortfall quantity always shown on the line |
| Procurement stages | "use what's in the rows" | `PR RAISED → APPROVED → PO RAISED → GRN IN PROGRESS → DELIVERED (CLOSED)`, plus `REJECTED` (exactly the list in the workbook's data validation) |
| Shortfall request number | (not stated) | `SHT-YYYY-NNNNN`, Kind `SHORTAGE`, as the HTA |
| Passwords | ignore | **v2: used.** Username + password login against Users (scrambled `p1$…`; HTA `s1$` hashes can't be checked in Power Apps, so everyone sets a new password once). See 09 §1 |

## 2. A bug in the HTA v8 that the Power Apps version fixes

The HTA works out "how much is still short" as **requested − reserved − released**. A released quantity
has already been reserved, so it's subtracted **twice**. The manager's exact example:

| | Requested | Reserved | Released | HTA shortfall | Correct shortfall |
|---|---|---|---|---|---|
| after **Reserve** | 50 | 40 | 0 | 10 ✔ | 10 |
| after **Release** | 50 | 40 | 40 | **−30 → 0 (lost)** | **10** |

So in the HTA, once the 40 are released, the 10 vanish from the shortfall book, the **Request separately**
button disappears, and the purchase tab is no longer fed. That's precisely the complaint "the shortfall
must be visible and trackable, not silently dropped".

I proved it on your actual HTA file in a browser (demo data, same code path). Request on-hand + 10,
reserve, release:
```
EDS-Lab-Portal.hta       ... "reserved":28,"released":28,"status":"PARTIALLY RELEASED","shortfallInBook":0
EDS-Lab-Portal-v8.1.hta  ... "reserved":28,"released":28,"status":"PARTIALLY RELEASED","shortfallInBook":10
```
- The Power Apps version uses **requested − max(reserved, released)** everywhere (verified in the 79-check run).
- If you keep the HTA, `hta-fix/EDS-Lab-Portal-v8.1.hta` is your v8 with **only that formula changed in 5 places**
  (see `hta-fix/shortfall-fix.diff`). Replace the .hta file next to the workbook; nothing else changes.

## 3. Small, deliberate differences (each one easy to change back)

1. **Shortfall book ignores requests nobody has reserved yet** (`SUBMITTED`, `ADMIN REVIEW`). The HTA counted
   every unreserved line of a new request as "short" before the store had even looked at it.
2. **"Request separately" keeps the original engineer as requester** (the HTA used whoever clicked), so the
   split request appears in that engineer's My Requests. It also notes the split on the original line's Remarks.
3. **Reserve can be pressed again** on `PURCHASE REQUIRED` / `PARTIALLY RELEASED` requests, to top up the
   reservation after new stock arrives. The HTA only allowed Reserve once.
4. **Material Inward** also offers `ADJUST-` (the HTA offered ADJUST in the + direction only). A reason is
   required for ADJUST+/ADJUST-/SCRAP, and you can't remove more than is on hand.
5. **Request numbers** = highest number used this year + 1 (the HTA used "number of requests + 1", which can
   repeat a number after a deletion).
6. **Numbers** use 1,234,567.00 grouping (Power Apps has no lakh grouping). Short money still shows ₹ L / ₹ Cr.
7. **Store location edit** on a request line saves to the line (RequestLines.StoreLocation) **and** the
   Parts tab, so the next request picks it up.
8. **PO copy** is a link (paste a SharePoint/OneDrive link into POCopyPath). Power Apps can't attach a
   PDF to Excel.
9. **Invoice photos** go to OneDrive › *EDS Lab Portal Photos*. `ImagePath` stores their paths separated by `;`.
   Invoice material lines aren't stored (same as the HTA). The printout re-reads the request's lines.
10. **No 10-second auto refresh** (the HTA polled the file). With the Excel connector that would mean every
    user re-downloading 12 tables every 10 seconds. Use **Refresh now** in the header.
11. **View as** (admins only) previews other roles without editing Excel. It's for testing and demos.

## 4. Still open (unchanged from your HTA notes)
- Finance to confirm assembly hours = circuits ÷ 7.5, and that AMC stays out of the total.
- Calibration tab: empty until you fill one row per instrument (the Manager dashboard then lists due/overdue items).
- `BOQ, CSR, PR-PO Status V1.xlsx` was never supplied, so Procurement stands on its own tab.
