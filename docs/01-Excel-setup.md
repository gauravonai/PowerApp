# Step 1: put the workbook where Power Apps can reach it (about 10 minutes)

Power Apps runs in Microsoft's cloud, so it can't open a file on the lab PC. It reads and writes an Excel
file stored in **OneDrive for Business** or a **SharePoint / Teams document library**, through the
*Excel Online (Business)* connector.

## 1.1 Choose where it lives

| Option | Use it when | Notes |
|---|---|---|
| **SharePoint / Teams "Files" of the lab team** (recommended) | More than one person will use the app | Everyone in the team already has access, and the file doesn't depend on one person's OneDrive |
| Your **OneDrive for Business** | You're testing alone, or showing the manager | Every other user must be given **Edit** access to the file, or the app can't save their changes |

## 1.2 Upload the prepared workbook

1. Take `excel/EDS-Lab-Data-PowerApps.xlsx` from this folder.
   It's your v8 `EDS-Lab-Data.xlsx` with only these additions (nothing removed, no formula changed):
   - **Users** has a new **Email** column on the far right. Leave it blank when a person's `Username`
     is the part of their email before `@` (`gaurav.shelke` → `gaurav.shelke@jcb.com`). Fill it only for
     people whose username doesn't match their email.
   - **Requests, RequestLines, Invoice, OngoingPurchase, Calibration, Procurement** each have **one row
     whose key starts with `SAMPLE`**. *Why:* Power Apps decides whether a column holds text, numbers or
     dates from the data it finds. An empty table makes every column "text", and saving a number or a date
     into it then fails. The app ignores every `SAMPLE` row. **Don't delete them.**
   - The NewPartRequest sample row is re-keyed `SAMPLE-NPR-00001` and its date is a real date.
   - A short **POWER APPS** note sheet at the end.
2. Upload it to the place you chose in 1.1. You can rename it, for example to `EDS-Lab-Data.xlsx`.
3. **Open it once in Excel for the web** (click it in OneDrive/SharePoint). Excel recalculates the
   LiveStock and Licenses formulas and saves. Then close the tab.
4. In the **same OneDrive**, create a folder called **`EDS Lab Portal Photos`** in the root. Create
   Invoice saves harness-label photos there.

> Starting from a newer copy of your real workbook instead of mine? Re-create the same additions by hand:
> add the `Email` column inside the Users table (type the header in the first empty column right of the
> table and it extends automatically), then add one `SAMPLE` row to each empty table with a real number in
> every number column and a real date in every date column. Or send me the newer file and I'll regenerate it.

## 1.3 Rules that keep the connector happy

- Keep every tab an **Excel Table** (`tblParts`, `tblMoves`, `tblUsers`, `tblSettings`, `tblProc`,
  `tblLicenses`, `tblNewPart`, `tblInvoice`, `tblPurch`, `tblCalib`, `tblRequests`, `tblReqLines`).
  The app finds them **by these names**.
- **Don't keep the file open in the desktop Excel app** for long periods. Excel for the web co-authoring
  is fine, but a desktop lock can make saves from the app fail with *"file is locked"*.
- The first time Power Apps connects, it adds a hidden column `__PowerAppsId__` to each table.
  That's normal, so leave it.
- The **LiveStock** tab isn't an Excel Table, so Power Apps can't read it. The app calculates exactly the
  same thing itself (sum of Movements by type) and checks it against every part. See docs/06 for the one
  small difference in the "low stock" status.

## 1.4 The HTA and this copy are two different files

The HTA on the lab PC keeps using its own local `EDS-Lab-Data.xlsx`. This cloud copy is a separate file
with the same layout. Changes made in one don't appear in the other. If you later want both apps on one
live file, sync the lab PC's folder with the OneDrive desktop app and point the HTA at the synced copy.
That's a separate step, so do it only after the Power Apps version is accepted.
