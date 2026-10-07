# EDS Lab Material Portal (Power Apps) — rules learned from real Studio imports

Generator: `tools/*.py` → `app/Src/*.pa.yaml`, `paste/*`, `app/EDS-Lab-Portal.msapp`. Never hand-edit generated files.

## Studio import rules (each one broke a real import; the build now refuses them)
1. **No control versions.** Write `GroupContainer`, `Classic/Button`… never `@1.4.0` (PA2105). Studio uses its current version.
2. **Classic/DatePicker** accepts no `CalendarHeaderFill`, `HoverColor`, `HoverFill`, `HoverBorderColor`, `HoverDateFill`,
   `PressedColor`, `PressedFill`, `PressedBorderColor`, `SelectedDateFill` (PA2108). TextInput/DropDown DO accept Hover*/Pressed*.
3. Microsoft template manifests (`tools/verify/control_props.json`) can be older than Studio: a property listed there can
   still be rejected. When Studio reports a PA2108, remove it in `pa.py`, in `control_props.json`, and add it to `tools/fix_src.py`.
4. **Power Fx 1.0 must be ON** in the packed app (`AppPreviewFlagsMap.powerfxv1 = true`, set in make_msapp.py).
   The base sample had it off; v2.0.2 opened fine but every list was empty (Distinct/Split semantics differ from the
   V1 engine all formulas are tested with). Studio shows no import error for this: only System Check reveals it.
5. `tools/fix_src.py` repairs any old .msapp/folder; `check()` is the build guard (build.py + make_msapp.py).

## Every release
- Bump `APP_VERSION` in `tools/screens.py` (shown on Welcome) and send the msapp as `EDS-Lab-Portal-v<version>.msapp`
  (same file name as an older build caused the user to import the wrong one).
- Run `tools/verify/run_all.sh`: schema, serializer, property names, parse, bind = 0 errors; simulation all pass;
  smoke test 0 runtime errors; pack prints the import guards line.
- v2.0.2 imports in the user's Studio but showed no data (Power Fx 1.0 off). v2.0.3 = fix + System Check screen
  (Login → System Check) + docs/10 hand-built live test. Ask for the System Check screenshot first when data looks wrong.

## Product decisions (agreed with the user)
- Login = username + password from Users (scrambled `p1$`, temp codes `t1$`); first password only if the PC's M365 user
  is that person, otherwise Lab Lead's Temp Password; Register → Role "Pending"; multi-role via comma list; View as; Log Out.
- No backend words (Excel/OneDrive/Microsoft) on screens ordinary users see; Data Health + Photo check are admin-only.
- Title Case for titles/buttons/headers/labels/pills (`pa.tc`); statuses stay UPPERCASE in Excel, display via `nfPill.D`.
- Clickable things are buttons/icons (hand cursor), never labels (`lbl(onselect=)` raises).
- Inputs light with dark text in every state. Named formulas never use variables.
- Communication: user likes terse replies (caveman), asks questions only when blocked.
