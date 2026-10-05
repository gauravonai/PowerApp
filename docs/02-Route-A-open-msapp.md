# Step 2, Route A: open the ready-made app file (about 15 minutes)

`app/EDS-Lab-Portal.msapp` contains all 23 screens, the app formulas and the theme. It was built with
Microsoft's own Power Platform CLI (`pac canvas pack`), which marks the file so Power Apps Studio
**builds every screen from the source code inside it** when you open it.

> That packing mode is a *preview* feature of `pac`. Microsoft's packer accepted the file and the round
> trip is byte-identical, but I couldn't open it in your tenant. If step 2.1 shows an error instead of the
> app, go straight to **Route B** ([03-Route-B-paste-screens.md](03-Route-B-paste-screens.md)). It uses the
> same screens and only takes longer.

## 2.1 Open the file

**Way 1, from the maker portal (newer menus):**
1. Go to **make.powerapps.com**. Top right: check the **Environment** is the one your company uses
   (usually *(default)*).
2. Left menu **Apps** → top bar **Import app** (or **Import canvas app**) → **From file (.msapp)**.
3. Pick `EDS-Lab-Portal.msapp`. Power Apps Studio opens with the app.

**Way 2, from inside Studio (works in every version):**
1. make.powerapps.com → **+ Create** → **Blank app** → **Blank canvas app** → Format **Tablet** → Create.
2. In Studio: **File** (or the **⋯ / Back** menu, depending on your Studio version) → **Open** → **Browse** →
   pick `EDS-Lab-Portal.msapp`.

You'll see lots of **red errors** at first. That's expected, because the app doesn't know your Excel file yet.

## 2.2 Connect the Excel tables (removes almost every error)

1. Left rail: **Data** (cylinder icon) → **+ Add data** → search **Excel Online (Business)** → select it
   (sign in / **Connect** if asked).
2. **Location**: *OneDrive for Business*, or *SharePoint Site URL* if you used a Teams/SharePoint library.
   Then **Document Library** → browse to `EDS-Lab-Data-PowerApps.xlsx`.
3. **Tick all 12 tables**: `tblCalib, tblInvoice, tblLicenses, tblMoves, tblNewPart, tblParts, tblProc,
   tblPurch, tblReqLines, tblRequests, tblSettings, tblUsers` → **Connect**.
   If Studio asks which column is the unique identifier, keep the suggested **`__PowerAppsId__`** for each table.
4. Check the names in the Data panel are **exactly** `tblParts`, `tblMoves`, and so on, with no `_1`
   suffixes. If one has a suffix, remove it and add it again.
5. **+ Add data** again → search **OneDrive for Business** → add it. (It's used only to save and show
   invoice photos.)

## 2.3 Settings (one-time)

1. **Settings** (gear, top bar) → **General** → **Data row limit**: set **2000**.
   The file already asks for 2000. Check it, because Movements has 775 rows today and the default is 500.
2. Close Settings.

## 2.4 Run the start-up formula and look around

1. Left rail **Tree view** → select **App** → top bar **⋯ → Run OnStart** (or right-click App → Run OnStart).
2. Press **F5** (Preview). You should land on **Dashboard** as yourself. Your name and role come from the
   Users tab, matched on your Microsoft 365 email.
   - Not in Users? You'll see *"You're not set up yet"*. Add yourself in Excel (Users tab) and press **Check again**.
3. Admins see a **"View as"** box in the header. Use it to preview the Engineer and Manager menus without
   changing anything in Excel.

## 2.5 Save, publish, share

1. **File → Save as** → name **JCB EDS Lab Material Portal** → Save. Then **Publish**.
2. **Share** (from make.powerapps.com → Apps → ⋯ → Share): add the lab team. Each person also needs
   **Edit** access to the Excel file (automatic in a Teams/SharePoint library).
3. People run it from make.powerapps.com, from the Power Apps mobile app, or from a link / Teams tab.

## 2.6 Then test

Go to [04-Test-checklist.md](04-Test-checklist.md). It takes 20 minutes and proves the important rules on
your own tenant.

### If something is red after 2.2
Open **App checker** (stethoscope icon) → **Formulas**. The message almost always names the problem:
a table name with a suffix, or a column the connector typed differently. See
[05-Troubleshooting.md](05-Troubleshooting.md), or copy the messages to me and I'll send fixed files.
