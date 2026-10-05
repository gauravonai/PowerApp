# Step 2, Route B: build the app by pasting code (about 1–2 hours, no typing)

Use this route if Route A's `.msapp` won't open, or if you'd rather build it screen by screen.
It uses Power Apps Studio's documented **Copy code / Paste code** feature: you copy a block of YAML text,
click a screen, press **Ctrl+V**, and Studio creates all the controls with their formulas.

Every file in `paste/` is plain text. Open it in **Notepad**, press **Ctrl+A** then **Ctrl+C**, then paste
into Studio.

> **Use a NEW blank app.** Every control has a fixed name (`rootDsh`, `subNr`, `lnRdGal`…) and the formulas
> refer to those names. If your 50%-built app already has a control with the same name, Studio renames the
> pasted one (`subNr_1`) and the formulas that point at it stop working.

## B.1 Create the app and its settings (5 min)

1. make.powerapps.com → **+ Create** → **Blank app** → **Blank canvas app** → name *JCB EDS Lab Material Portal*,
   Format **Tablet** → **Create**.
2. **Settings** (gear) → **General**:
   - **Data row limit** = **2000**
   - Under **Display**: Screen size **16:9 (default)**, *Scale to fit* **On**, *Lock aspect ratio* **On**
     (the screens are drawn for 1366 × 768, like the HTA window).
3. Close Settings.

## B.2 Connect the data (5 min)

Same as Route A step 2.2:
- **Data → Add data → Excel Online (Business)** → your `EDS-Lab-Data-PowerApps.xlsx` → tick **all 12 tables** → Connect.
  The names must be exactly `tblParts`, `tblMoves`, `tblUsers`, `tblSettings`, `tblProc`, `tblLicenses`,
  `tblNewPart`, `tblInvoice`, `tblPurch`, `tblCalib`, `tblRequests`, `tblReqLines`.
- **Add data → OneDrive for Business** (for invoice photos).

## B.3 Paste the three app formulas (5 min)

In the **Tree view**, select **App**. At the top left there's a **property dropdown** (it usually shows
`OnStart`), with the formula bar next to it.

| Property (pick it in the dropdown) | Paste the whole content of | What it is |
|---|---|---|
| **Formulas** | `paste/00-App.Formulas.txt` | Theme colours, who is signed in, live stock, request views, numbering. About 90 *named formulas* |
| **OnStart** | `paste/01-App.OnStart.txt` | Session variables and empty collections |
| **StartScreen** | `paste/02-App.StartScreen.txt` | Opens Dashboard, Manager Dashboard or the "not set up" screen |

Click into the formula bar, select everything already there, delete it, then **Ctrl+V**. Some red
underlines in *StartScreen* will remain until the screens exist (B.4). That's expected.

## B.4 Create the 23 screens, then paste one file into each

For **each row below**:
1. **+ New screen → Blank**.
2. Rename the screen (double-click its name in the Tree view) to **exactly** the name in the first column.
   Capital letters matter.
3. Set the screen's **Fill** property to `cBg` (for `scrPrint` use `RGBA(255,255,255,1)`).
   It's only seen for a moment while loading.
4. Open the file in Notepad, **Ctrl+A**, **Ctrl+C**. In Studio, **click the screen in the Tree view**,
   then **Ctrl+V**, or right-click the screen → **Paste** / **Paste code**.
5. A container named like the second column appears and fills the screen. Done. Next row.

| Screen name (rename to) | Paste file | Root control it creates | Size |
|---|---|---|---|
| `scrDash` | `10-scrDash.yaml` | rootDsh | 106 KB |
| `scrMgrDash` | `11-scrMgrDash.yaml` | rootMgr | 88 KB |
| `scrStock` | `12-scrStock.yaml` | rootStk | 40 KB |
| `scrBom` | `13-scrBom.yaml` | rootBom | 67 KB |
| `scrNewReq` | `14-scrNewReq.yaml` | rootNr | 63 KB |
| `scrMyReq` | `15-scrMyReq.yaml` | rootMy | 38 KB |
| `scrReqDetail` | `16-scrReqDetail.yaml` | rootRd | 100 KB |
| `scrQueue` | `17-scrQueue.yaml` | rootQu | 40 KB |
| `scrNewPart` | `18-scrNewPart.yaml` | rootNp | 46 KB |
| `scrNewPartQ` | `19-scrNewPartQ.yaml` | rootNq | 43 KB |
| `scrInventory` | `20-scrInventory.yaml` | rootInv | 74 KB |
| `scrInward` | `21-scrInward.yaml` | rootIn | 51 KB |
| `scrLedger` | `22-scrLedger.yaml` | rootLg | 47 KB |
| `scrDemand` | `23-scrDemand.yaml` | rootDm | 41 KB |
| `scrInvoice` | `24-scrInvoice.yaml` | rootIv | 113 KB |
| `scrInvList` | `25-scrInvList.yaml` | rootIl | 57 KB |
| `scrCost` | `26-scrCost.yaml` | rootCs | 95 KB |
| `scrPrint` | `27-scrPrint.yaml` | rootPr | 34 KB |
| `scrProc` | `28-scrProc.yaml` | rootPc | 134 KB |
| `scrPurch` | `29-scrPurch.yaml` | rootPu | 100 KB |
| `scrLic` | `30-scrLic.yaml` | rootLc | 80 KB |
| `scrTeam` | `31-scrTeam.yaml` | rootTm | 46 KB |
| `scrNoAccess` | `32-scrNoAccess.yaml` | rootNa | 5 KB |

**Tips**
- **The first paste asks for clipboard permission** in Edge or Chrome. Allow it. If nothing happens, add
  `https://make.powerapps.com` to the browser's allowed sites for clipboard (Microsoft's own advice).
- Big files take a few seconds. Wait for the controls to appear before you do anything else.
- **Errors while screens are still missing are normal.** Every screen's left menu can jump to every other
  screen, so the red marks disappear once all 23 exist. Open the **App checker** only at the end.
- Delete the original empty **Screen1** at the end. Order of screens in the Tree view doesn't matter.

## B.5 Finish

1. Select **App** → **⋯ → Run OnStart**.
2. Open **App checker** (stethoscope). There should be **no formula errors**. Yellow *delegation*
   warnings are expected with Excel (see Troubleshooting §3).
3. **F5** to preview. Then **Save**, **Publish**, **Share** exactly as in Route A steps 2.4–2.5.
4. Run the [test checklist](04-Test-checklist.md).

## If a paste is refused
Studio checks the YAML before creating anything. If it says the code isn't valid:
- Make sure you copied the **whole** file (Ctrl+A in Notepad). The first line starts with `- root…:`.
- If the message names a **control type** (for example `AddMedia`) or a **property** it doesn't know,
  send me the exact message. I can regenerate all 23 files without that property in minutes. Meanwhile,
  for `AddMedia` only: delete the `- amIv:` block (8 lines) from `24-scrInvoice.yaml` in Notepad, paste,
  then insert **Media → Add picture** on the Create Invoice photos card yourself and rename its *Add
  picture* control to `amIv`.
