# Troubleshooting

When something is wrong, Power Apps' **App checker** (stethoscope icon) lists every formula error, with the
control name. Each fix below is matched to the message you'll see. For anything not listed, copy the
App checker message (control name + text) and send it to me with this repo. I fix the generator and
re-issue every affected file.

## 1. "Name isn't valid. 'tblParts' isn't recognized" (or another tbl… name)
The Excel table isn't connected, or it was connected under another name (`tblParts_1`).
Fix: **Data** panel → remove the oddly named one → **Add data** → Excel Online (Business) → same file →
tick the table again. The names must be exactly the Excel table names.

## 2. Errors on Patch / Collect such as "expects a Date value" / "Number expected" / "The type of this argument does not match"
The connector typed an Excel column differently from what the app writes. This happens when a column was
empty when the data source was added.
Fix: in Excel make sure the table has its **SAMPLE row** with a real number or date in that column
(docs/01 §1.2) → in Studio **Data** panel → table **⋯ → Refresh**. If it still complains, remove and
re-add that one table.

## 3. Yellow triangles: "Delegation warning … may not work correctly on large data sets"
Expected. The Excel connector never filters on the server; Power Apps downloads up to the **Data row limit**
(set it to **2000**, the maximum) and works on that. Today: Parts 418, Movements 775. **Movements will reach
2000 rows in roughly 3–4 years at the current rate.** Before that, move Movements (and later the other tabs)
to a SharePoint list or Dataverse. Formulas only need the table name changing, because the column names
stay the same. Ask me when you get there.

## 4. Login messages
| Message | Meaning / fix |
|---|---|
| *No account with that username* | Not in **Users**. Use **Register** (then the Lab Lead approves), or the Lab Lead adds you in Team Access. |
| *This account has no password yet. Ask the Lab Lead for a temporary password* | First login from a PC signed in as someone else. Lab Lead → Team Access → **Temp Password** on your row. |
| *Your access request is waiting for the Lab Lead's approval* | Role is **Pending**. Lab Lead sets a real role in Team Access (or in the Users tab). |
| *That password is not right* / *Too many wrong attempts* | Retry, or close and reopen the app after 5 tries. Forgotten → Temp Password from the Lab Lead. |
| *This account is switched off* | Role is **Disabled**. |

## 5. Everyone else can't log in or can't save
- They must be in **Users** with a role that is not Pending (Team Access, or in Excel).
- They must have **Edit** access to the Excel file. Keep it in a Teams/SharePoint library everyone in
  the lab can use, not in one person's OneDrive.
- The app must be **shared** with them (Apps → ⋯ → Share).

## 6. "The file is locked for shared use / the workbook is in use"
Someone has the workbook open in **desktop Excel** without AutoSave. Close it, or use Excel for the web.
The HTA's _pending journal doesn't exist in Power Apps: a failed save shows a red message and nothing
is written, so try again after closing the file.

## 7. A date is one day early in Excel
The app writes every date at 12:00 noon local time so the connector's UTC conversion (IST = UTC+5:30)
can't move it to the previous day. If you still see it, check the **time zone** of your OneDrive/SharePoint
(regional settings). It should be (UTC+05:30) Chennai, Kolkata, Mumbai, New Delhi.

## 8. Pasting code does nothing
- Allow clipboard access for make.powerapps.com in the browser (Edge: Settings → Cookies and site
  permissions → Clipboard → Allow).
- Click the **screen in the Tree view** first, then Ctrl+V.
- Copy the whole file (Ctrl+A in Notepad).

## 9. Pasted controls got a `_1` at the end of their names
A control with that name already existed. Formulas refer to the original name, so delete the old
control (or the whole old screen) and paste again. Always paste into a **new blank app** (docs/03).

## 10. The .msapp won't open
Use Route B. The screens are identical.

## 11. Invoice photos: "OneDriveForBusiness isn't recognized" or the save fails
Add the **OneDrive for Business** data source (Data → Add data) and create the folder
**EDS Lab Portal Photos** in the root of the OneDrive that the signed-in person uses. If your tenant
blocks that connector, photos still show while you're on the screen. Only the upload part fails, and
the invoice row still saves if no photo is attached.

## 12. The app feels slow when it opens
Stock, reservations, the ledger and the request views are calculated from the Excel tables when first
needed, about 418 parts × 775 movements. Expect 1–3 seconds on the first screen and instant after that.
If it's much slower:
- Make sure **Data row limit = 2000**, not more tables than needed.
- Use **Refresh now** only after somebody else has changed Excel.

## 13. Fonts or sizes look different from the HTA
Power Apps sizes text in points, so text is a little larger than the HTA's pixels. Everything was laid
out for 1366 × 768 with *Scale to fit*. If a long description is cut off in a table cell, widen that
column (select the label in the gallery template → Width) or send me the screen name.

## 14. Printing
**Print / Save as PDF** hides the toolbar, prints the current screen through the browser's print dialog,
then brings the toolbar back. If your browser blocks the dialog, press Ctrl+P while on the print screen.
For the cleanest PDF choose *Margins: None* and *Background graphics: On* in the print dialog.

## 15. Import errors like "PA2108 Unknown property" or "PA2105 GroupContainer@1.4.0 … older than the current version"
Both came from the **first (v1) .msapp**. Every build since has neither, and the build now **refuses** to produce
a file that has either one (checked on the sources, the paste files and the finished .msapp).

- **Check which file you imported:** the v2 Welcome screen shows *Version 2.0.1 · 07-Oct-2026* bottom right.
  If you see `scrNoAccess` in the warnings, it is the old v1 file. Use `EDS-Lab-Portal-v2.0.1.msapp`.
- **Repairing any old file or folder yourself** (machine with Python):
  `python3 tools/fix_src.py OldApp.msapp` writes `OldApp-fixed.msapp`; `python3 tools/fix_src.py app/Src` fixes a folder.
  It removes `CalendarHeaderFill` lines and the `@1.4.0`-style version from every control, so Studio uses its
  current version. That is better than writing `@1.5.0`, which would warn again at Microsoft's next update.

## 16. Stock looks wrong, or BOM Compare shows no on hand
Log in as Lab Admin → **About → Data Health**. If *Movement rows* shows fewer in the app than in Excel, set
**Settings → General → Data row limit = 2000** and reopen the app. If it says *Not set up*, add the three
`Excel…` rows to the Settings tab ([09-v2-whats-new.md](09-v2-whats-new.md) §4).

## 17. Photos don't save
About → **Photo Storage Check → Test Photo Storage**. It names the exact problem (no OneDrive for Business
connection, or the folder **EDS Lab Portal Photos** is missing in the OneDrive root).

## 18. PA2108 on the Add picture control (`OnChange`)
If Studio rejects `OnChange` on the photo box (the one property I could not check against a Microsoft template),
delete that property in the error and add a button with the same formula (Collect into colShots). Tell me and I'll ship it.
