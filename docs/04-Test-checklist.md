# Step 3: test checklist (about 20 minutes)

The same scenario I ran automatically (79 checks, all passing) against your real workbook. Do it once on
your tenant to prove the Excel connector behaves the same way. Do it on a **copy** of the workbook if you
don't want test rows in the real one. Every test row is easy to spot (`REQ-…` you just raised).

Tip: use the header's **View as** box (admins only) to switch between Engineer, Lab Admin and Manager.

## A. Sign-in and stock (2 min)
| # | Do | Expect |
|---|---|---|
| A1 | Open the app | Dashboard, your name and initials top right, role from the Users tab (Gaurav → **LAB LEAD**) |
| A2 | Dashboard tiles | **Out of stock 10**, **Low stock 37** (same as the HTA with this workbook) |
| A3 | Check Stock → search `7213/0024` | On hand **40** (the sum of its Movements rows) |
| A4 | Pick any part in Excel, add up its Movements by hand (RECEIPT/RETURN/ADJUST+ minus ISSUE/SCRAP/ADJUST−) | Same number as On hand in the app |

## B. The manager's case: asked 50, only 40 available (8 min)
| # | Do | Expect |
|---|---|---|
| B1 | View as **Engineer** → BOM Compare → paste `7213/0024` *tab* `50` → Compare | Status **SHORTAGE**, Short **10** |
| B2 | Raise part request › → fill every field (circuits **48**, Required by a future date) → leave circuits empty first and Submit | Refused: *"No. of circuits is required…"* |
| B3 | Fill circuits → Submit | Toast `REQ-2026-0000x is with the store`. My Requests shows it as **SUBMITTED**. Excel **Requests** has the row, **RequestLines** has the line(s) |
| B4 | View as **Lab Admin** → Request Queue → open it → **Reserve available stock** | Line: Req 50, Resv **40**, Short **10**, status **PARTIAL**. Request **PURCHASE REQUIRED**. Ongoing Purchase has a **REQUIRED** row for 10. **On hand still 40** (reserving doesn't move stock) |
| B5 | Type **999** in *Release now* → **RELEASE** | Refused. Nothing added to Movements |
| B6 | Put back **40** → **RELEASE** | Movements gains an **ISSUE** row of **40** with Reference = the request no. On hand for 7213/0024 → **0**. Line Rel 40, **Short still 10**. Request **PARTIALLY RELEASED** |
| B7 | Stock Transactions → top row | The release shows Harness, Machine, **Issued to** = requester |
| B8 | On the short line → **Request separately** → qty 10 → Submit | New `SHT-2026-0000x` request (Kind SHORTAGE, parent = original, requester = original engineer). Original's History shows 4 events |

## C. Inward and guards (3 min)
| # | Do | Expect |
|---|---|---|
| C1 | Material Inward → `7213/0024`, qty 25, type **PO**, ref `4700012345` → Record | Toast *Stock is now 25*. Movements **RECEIPT 25** |
| C2 | Type **SCRAP**, qty 5, no reason | Refused (*reason required*) |
| C3 | Scrap qty 500 with a reason | Refused (*only 25 in store*) |
| C4 | Scrap 5 with a reason | Movements **SCRAP 5**, on hand **20** |

## D. Costing and invoice (4 min)
| # | Do | Expect |
|---|---|---|
| D1 | Cost Sheet → circuits **100** | Harness assembly cost **16,808.15** |
| D2 | circuits **200** | **33,616.30**. TOTAL = material + assembly + **200** transport |
| D3 | Print assumptions + cost sheet | White Excel-coloured sheets with signature lines. Print dialog → *Save as PDF* works |
| D4 | Create Invoice → number box | **IDC EDS/26-27/001** (first of the FY; restarts every 1 April) |
| D5 | Fill from a request → Load BOM → add a photo → Save invoice | Invoice row in Excel, TotalCost = material + assembly + 200. Photo saved in OneDrive › EDS Lab Portal Photos. ImagePath holds its path |
| D6 | Invoices → Open | Printable invoice with photo(s) under it |

## E. The rest (3 min)
- **Brand New Purchase Part**: leave HSN empty on a row with a part name → *Row 1 is missing 8-Digit HSN*. Fill it → `NPR-2026-00001`.
- **Procurement**: + New PR / PO entry → save → row at **PR RAISED** → **Mark approved** → **APPROVED**, Approved by = you.
- **Software Licenses**: change *In use*, press the ✓ → value saved in Excel. Status shows EXPIRED / EXPIRING SOON / ACTIVE.
- **Team access**: change someone's Role → ✓ → Excel Users updated.
- **Manager** (View as Manager): revenue pie by BU, PR/PO bars, deliveries, projects, calibration message. No action buttons anywhere.

When everything matches, delete the test rows from Excel (Requests, RequestLines, Movements, OngoingPurchase,
Invoice, NewPartRequest, Procurement). **Keep the `SAMPLE` rows.**

---
### What the automatic run checked (for reference)
Sign-in and role mapping (10 role spellings) · stock = movement sum for all 418 parts · 10 out / 37 low ·
BOM parse (tab, double space, comma) and NEW PART / OUT OF STOCK / AVAILABLE · mandatory circuits ·
`REQ-YYYY-NNNNN` numbering · reserve 40 of 50 → PURCHASE REQUIRED, stock unchanged, purchase line of 10 ·
over-release refused · release posts one ISSUE per line with EntryId, stock −40, shortfall 10 kept,
PARTIALLY RELEASED · ledger join · split request `SHT-…` with parent, requester and history · inward
RECEIPT, scrap guards · Finance figures 16,808.15 / 33,616.30 · invoice `IDC EDS/26-27/001 → 002` and
total · new-part mandatory columns and `NPR-…` · PR save and stage advance · all list screens evaluate ·
pie SVG renders. Full log: run `tools/verify/run_all.sh` (output in `tools/out/sim.log`).
