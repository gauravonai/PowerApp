# How the app is built (read this before you change anything)

## The idea in one paragraph
Exactly like the HTA, **nothing about stock is stored**. The app reads the 12 Excel tables and works
everything else out in **named formulas** (App → *Formulas*). Power Apps recalculates them by itself
whenever a table changes. A button only ever **adds or edits rows** in Excel (`Collect` / `Patch`), and the
screens update because the named formulas recalculate. That's why a release shows the new stock instantly
and the same number appears on every screen.

## The named formulas you'll meet in every screen

| Name | What it is |
|---|---|
| `cBg cPanel cPanel2 cSunk cLine cLine2 cInk cInk2 cInk3 cJcb cJcbDark cJcbWash cOnJcb cSteel cOk cWarn cStop`, `fMono`, `fUI` | The HTA palette and fonts. Change a colour here and every screen follows |
| `nfEmail, nfMeRow, nfMeName, nfRoleCanon` | Signed-in person (Microsoft 365) → Users row → canonical role (HTA rules: admin/store/incharge = Lab Admin, mgr = Manager, anything else = Engineer) |
| `nfParts` | Active parts (Active ≠ No), cleaned |
| `nfMoves` | Movements with a signed quantity `SQty` (+ RECEIPT/RETURN/ADJUST+, − ISSUE/SCRAP/ADJUST-) |
| `nfOnHand`, `nfResv`, **`nfStock`** | On hand = Σ SQty. Reserved = reserved − released on requests that hold stock. **`nfStock`** = every part with OnHand, Reserved, Avail, Status (OUT/LOW/FULLY RESERVED/IN STOCK), StockValue, Quality |
| `nfReq`, `nfLines`, `nfReqView` | Requests, their lines, and the list view with Lines / ShortLines / ShortQty / IsMine |
| `nfShortBook` | Shortfall per part across open, already-reserved requests (requested − max(reserved, released)) |
| `nfPurch nfProc nfLic nfNewPart nfInv nfCalib` | The other tabs, cleaned and typed. `SAMPLE` rows are removed here |
| `nfLedger` | Movements newest first, joined to the request (harness, machine, issued to) |
| `nfNextReqSeq`, `nfNextInvNo`, `nfNextNprSeq`, `nfFY` | Numbering: `REQ/SHT-YYYY-NNNNN`, `IDC EDS/26-27/NNN` (resets 1 April), `NPR-YYYY-NNNNN` |
| `kMachineCost … kCktPerHr` | Finance-locked constants (Assumptions sheet) |
| `nfNav`, `nfPill` | The left menu per role (same groups and labels as the HTA) and the status-pill colours |

Variables set by buttons: `gRole` (current role; admins can change it with *View as*), `gReqNo`
(request being viewed), `gShortSr`, `gInvReq`/`gInvEdit`, `gCostReq`, `gPanel` (which add/edit panel is
open), `gBusy` (disables action buttons while saving). Collections: `colBom` (BOM Compare result),
`colNP` (new-part sheet), `colInvLines`, `colCostLines`, `colShots` (photos).

## Every screen has the same skeleton
```
root<K>                      container 1366 x 768
 ├ hdr…<K>                   header: EDS mark, title, avatar, name, role, View as, Refresh now
 ├ nav…<K> / navGal<K>       left menu (gallery over nfNav, filtered by gRole)
 └ body<K>                   vertical auto-layout container, scrolls, 26 px padding, 16 px gap
     ├ hd<K>                 page title + subtitle (+ right-hand button)
     ├ ti…<K>                tiles row (when the HTA had tiles)
     ├ cd…<K>                cards: 46 px title bar + content
     └ tb…<K>                tables: header strip + gallery
```
`<K>` is a short screen code (Dsh, Mgr, Stk, Bom, Nr, My, Rd, Qu, Np, Nq, Inv, In, Lg, Dm, Iv, Il, Cs, Pr,
Pc, Pu, Lc/lc, Tm/tm, Na), which keeps every control name unique across the app.

Inside a table gallery the cells are named `<prefix>C0`, `C1`, … from left to right. A few formulas refer
to a specific cell: Request detail's **RELEASE** reads `lnRdC9` (the *Release now* box), Software
Licenses' ✓ reads `lcC1…lcC8`, Team access's ✓ reads `tmC1…tmC4`. **Don't rename those.**

## Changing things safely
- **A colour, a label, a width**: select the control in Studio and edit the property. Nothing else depends on it.
- **A business rule** (for example the low-stock %): change it in Excel **Settings** if it's a setting, or
  in App → Formulas (`nfStock`'s `Status`).
- **A new column in Excel**: add it inside the table → Studio **Data → table ⋯ → Refresh** → use it.
  For it to appear on a list, add a label in that table's gallery.
- **Bigger changes**: describe them to me against these names (for example "on scrReqDetail add a Cancel
  button that sets Status to CANCELLED"). Everything is generated from `tools/screens.py`, so I change the
  generator, re-run all checks, and send you new paste files and a new .msapp.
- With **Copilot in Power Apps**, use [08-Copilot-prompt-corrected.md](08-Copilot-prompt-corrected.md) as the
  context. It has the corrected table, column, status and screen names.

## Performance notes
- 23 screens, about 2,000 controls (each screen repeats its header and menu so every screen is self-contained
  for copy/paste). Power Apps loads screens on demand, so only the open screen costs anything.
- Lists are galleries, which draw only the visible rows, so 418 parts or 775 movements scroll smoothly.
- The Excel connector can't filter on the server. Everything works on the first **2000** rows of each
  table (see Troubleshooting §3 for the plan when Movements grows past that).
