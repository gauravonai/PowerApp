# Step 3: test checklist (about 25 minutes)

The same scenario I ran automatically (108 checks plus a 188-button smoke test, all passing) against your real
workbook. Do it once on your tenant to prove the Excel connector behaves the same way. Do it on a **copy** of
the workbook if you don't want test rows in the real one.

Tip: use the header's **View as** box to switch between the roles you hold (Lab Lead: all three).

## A. Login and stock (5 min)
| # | Do | Expect |
|---|---|---|
| A1 | Open the app | **Welcome** screen → **Log In** |
| A2 | Type your username (e.g. `gaurav.shelke`), leave the password empty → Login | First time on your own PC: **Set Your Password** |
| A3 | Choose `abc` | Refused: *at least 6 characters, with a letter and a number* |
| A4 | Choose a proper password twice → **Save and Log In** | Dashboard. Your name and initials top right, *Lab Lead view*. Excel **Users** › your row › Password starts with `p1$`, not your password |
| A5 | **Log Out** → log in with a wrong password | *That password is not right.* |
| A6 | Team Access → someone's row → **Temp Password** | A 6-digit code appears. Log Out, log in as them with the code → they must choose their own password |
| A7 | Login page → **Register** → fill the form → Send Request | Users gets a row with Role **Pending**. Logging in as them says *waiting for the Lab Lead's approval* until you set a role |
| A8 | Dashboard tiles | **Out of Stock 10**, **Low Stock 37** (same as the HTA with this workbook) |
| A9 | Check Stock → search `7213/0024` | On hand **40** (the sum of its Movements rows) |
| A10 | About → **Data Health** | Parts 418 / 418, Movements 775 / 775, stock total equal → all **OK** |

## B. The manager's case: asked 50, only 40 available (8 min)
| # | Do | Expect |
|---|---|---|
| B1 | View as **Engineer** → BOM Compare → paste `7213/0024` *tab* `50` → Compare | Status **Shortage**, Short **10**. Toast: *…live stock as of hh:mm:ss* |
| B2 | Raise part request › → fill every field (circuits **48**, Required by a future date) → leave circuits empty first and Submit | Refused: *"No. of circuits is required…"* |
| B3 | Fill circuits → Submit | Toast `REQ-2026-0000x is with the store`. My Requests shows it as **Submitted**. Excel **Requests** has the row, **RequestLines** has the line(s) |
| B4 | View as **Manager** → Dashboard → *Waiting for Your Approval* → open it → **Approve** → status **Approved**. Then View as **Lab Admin** → Request Queue → open it → **Reserve Available Stock** | Line: Req 50, Resv **40**, Short **10**, status **Partial**. Request **Purchase Required**. Ongoing Purchase has a **Required** row for 10. **On hand still 40** (reserving doesn't move stock) |
| B5 | Type **999** in *Release now* → **RELEASE** | Refused. Nothing added to Movements |
| B6 | Put back **40** → **RELEASE** | Movements gains an **ISSUE** row of **40** with Reference = the request no. On hand for 7213/0024 → **0**. Line Rel 40, **Short still 10**. Request **Partially Released** |
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
- **Brand New Purchase Part**: fill the form without HSN → Add to List → *Please fill in 8-Digit HSN*. HSN `8536` → *exactly 8 digits*. Fix it → Add to List → Submit to Store → `NPR-2026-00001`, listed under *Your New Part Requests*. Manager → New Purchase Parts → **Approve**.
- **Procurement**: + New PR / PO entry → save → row at **PR Raised** → **Mark Approved** → **Approved**, Approved by = you. As Manager the button reads **Approve PR**.
- **Software Licenses**: change *In use*, press the ✓ → value saved in Excel. Status shows Expired / Expiring Soon / Active.
- **Team access**: change someone's Role → ✓ → Excel Users updated.
- **Manager** (View as Manager): Waiting for Your Approval, revenue pie by BU, PR/PO bars, deliveries, projects, calibration. Approve/Reject only; no stock actions.
- **Typing**: in every text box the text you type is dark on a light box, also while the mouse is over it.

When everything matches, delete the test rows from Excel (Requests, RequestLines, Movements, OngoingPurchase,
Invoice, NewPartRequest, Procurement). **Keep the `SAMPLE` rows.**

---
### What the automatic run checked (for reference)
Login flows (first password, rules, wrong password, temporary code, single-use code, register → pending → approved, multi-role, log out) · password scramble identical to the reference implementation · role mapping (12 spellings) · Data Health counts equal · stock = movement sum for all 418 parts · 10 out / 37 low ·
BOM parse (tab, double space, comma) and NEW PART / OUT OF STOCK / AVAILABLE · mandatory circuits ·
`REQ-YYYY-NNNNN` numbering · reserve 40 of 50 → PURCHASE REQUIRED, stock unchanged, purchase line of 10 ·
over-release refused · release posts one ISSUE per line with EntryId, stock −40, shortfall 10 kept,
PARTIALLY RELEASED · ledger join · split request `SHT-…` with parent, requester and history · inward
RECEIPT, scrap guards · Finance figures 16,808.15 / 33,616.30 · invoice `IDC EDS/26-27/001 → 002` and
total · new-part mandatory columns and `NPR-…` · PR save and stage advance · all list screens evaluate ·
pie SVG renders. Full log: run `tools/verify/run_all.sh` (output in `tools/out/sim.log`).
