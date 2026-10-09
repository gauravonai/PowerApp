# Version 2: what changed and why

Everything on your handwritten list, with the decision taken for each point. Previews of every screen are in
[`docs/preview/v2/`](preview/v2) and [`docs/preview/`](preview).

## 1. Login: username + password (decided with you)

**Why not Microsoft 365 sign-in alone?** On a shared lab PC, one Windows/M365 account is often signed in
while several people use the app. A username + password lets the engineer, the manager and you each log in
as yourselves on the same PC.

| Situation | What happens |
|---|---|
| **Welcome** screen | **Log In** or **Request Access**. Nothing about the data or its storage is shown before login. |
| **User Login** | Username + Password, **Login**, **Register** and **Forgot Password?** |
| First time | If the person's Password cell is empty, the app asks them to choose a password. |
| Forgot password | Type your username, press **Forgot Password?**, choose a new password (at least 4 characters). Done. |
| Admin rescue | Type a password straight into the person's Password cell in the Users sheet: it works as typed. |
| **Register** | Full name, username, business unit, email (optional), password. Creates a Users row with **Role = Pending**; the Lab Lead sets a real role in Team Access. |
| How passwords are stored | Passwords chosen in the app are scrambled (`p1$…`). Kept deliberately simple: the real protection is the permission on the workbook's folder. |
| Several roles, one person | Put them in the **Role** cell separated by commas, e.g. `Engineer, Manager`. The first one is where the app opens. |
| Switching role | Header **View as**: only the roles you hold. Lab Lead / Lab Admin can view all three; a Manager can also work as Engineer. |
| **Log Out** | Header, top right. Clears the session and returns to the login page, ready for the next person. |

## 2. The text cursor on buttons
v1 made table rows and menu items clickable *labels*, which show the text cursor. In v2 every clickable item is a
real button (the hand cursor): menu items are pill buttons with icons, and table rows have an invisible button on
top that also highlights the row on hover. Labels can no longer be made clickable by mistake: the generator refuses it.

## 3. Typed text invisible (black on black)
The v1 text boxes set only the normal text colour, so while typing or hovering Power Apps fell back to black on
the dark box. v2 inputs, dropdowns and date pickers are light with dark text, and the colour is set for every
state (normal, hover, typing, disabled).

## 4. Stock "not linked to Excel in real time"
Stock is still calculated from every Movements row, and v2 adds three things:
- **Auto refresh**: every screen re-reads Parts, Movements, Requests and Settings every **2 minutes**.
  The header shows **● Live · Synced hh:mm**. Click it to refresh everything immediately (this replaces the old
  *Refresh now* button, so you can still force it after someone else edits the workbook).
- **BOM Compare re-reads the data first**, then compares. The toast says *as of hh:mm:ss*.
- **Data Health** (About page, Lab Admin/Lead only): Excel counts its own rows with formulas, the app counts
  what it read, and the two are shown side by side (parts, movements, total stock). If they differ, the
  usual cause is **Settings → Data row limit** below 2000. That is the likeliest cause of *"BOM shows no
  on hand"* in v1; this check proves it either way on your tenant.
  **If you already uploaded the v1 workbook**, add these 3 rows at the bottom of the **Settings** table (Key / Value):

  | Key | Value (type exactly, including `=`) |
  |---|---|
  | `ExcelPartRows` | `=ROWS(tblParts)` |
  | `ExcelMovementRows` | `=ROWS(tblMoves)` |
  | `ExcelStockTotal` | `=SUMPRODUCT((tblMoves[Type]="RECEIPT")+(tblMoves[Type]="RETURN")+(tblMoves[Type]="ADJUST+")-(tblMoves[Type]="ISSUE")-(tblMoves[Type]="SCRAP")-(tblMoves[Type]="ADJUST-"),ABS(tblMoves[Qty]))` |

  Or upload the new `excel/EDS-Lab-Data-PowerApps.xlsx` (it already has them).

## 5. Brand New Purchase Part
Rebuilt as **one labelled form per part** (labels above every box, mandatory ones marked *), **Add to List**,
then **Submit to Store** for the whole list. Rows in the list can be edited or removed. HSN must be exactly 8 digits.
A third card shows *Your New Part Requests* with their approval status. Any save error now shows the real
reason instead of failing silently.

## 6. Spelling, capitals and wording
- Titles, buttons, column headers, field labels, menu items and status pills: **Title Case** everywhere
  (`Purchase Required`, not `PURCHASE REQUIRED`). Sentences stay in sentence case.
- Acronyms stay capital: BOM, PR, PO, UOM, HSN, GRN. One spelling: **Licenses**.
- Status values are still stored in capitals in Excel (so the HTA and old rows keep working). Only the display changed.
- No screen an ordinary user sees mentions Excel, OneDrive or Microsoft 365.

## 7. Harness label photos
- Click the photo box (a phone opens the camera) and the photo is **attached immediately**. There's no separate *Add this photo* step.
- Photos upload when you press **Save Invoice**. If an upload fails, the invoice still saves, the photos stay
  attached, and the message gives the real reason.
- **About → Photo Storage Check** (Lab Admin) tests the OneDrive folder and connection in one click.

## 8. Approvals
| Who | Approves |
|---|---|
| Lab Admin / Lab Lead | Material requests (Approve / Reject, then Reserve / Release), brand new parts, PR stages |
| Manager | Material requests (Approve / Reject), brand new parts, PRs (**Approve PR** / Reject) |

The Manager dashboard opens with a **Waiting for Your Approval** card: requests, brand new parts and PRs,
each one click away.

## 9. Look and feel
InnoSphere-style palette: dark glass panels over a backlit backhoe-loader sunset photo, gold and orange
accents, orange card headings, rounded bold buttons, icon pill menu, Log Out button. The name stays your own:
**EDS Lab Material Portal**. There's an **About** page (About Us, what the portal does, how roles work).

**Background picture**: `app/media/bg-backhoe.jpg` (rendered and photo-graded, no AI and no stock photo). To use
a real company photo: Studio → **Media** → upload it → App → Formulas → change `imgBg = ...` to `imgBg = YourPhotoName;`.

## 10. Tested
| Check | Result |
|---|---|
| Microsoft schema + serializer, every property name, every formula parsed and type-checked | 0 errors |
| Workflow simulation on your workbook (login flows, approvals, reserve/release, invoice, new parts…) | **108 / 108 pass** |
| "Click every button": every OnSelect / OnChange / timer outside lists, and every menu item, run in the engine | **188 pressed, 0 runtime errors** |
| Screenshots of every screen reviewed for overlap, clipping and casing | done |
