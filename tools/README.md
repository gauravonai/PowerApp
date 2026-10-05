# Generator and verification (not needed at work)

| File | Purpose |
|---|---|
| `build.py` | Generates `app/Src/*.pa.yaml` and `paste/*` from `screens.py`, `ui.py`, `pa.py`, `appfx.py` |
| `appfx.py` | App.Formulas (named formulas), App.OnStart, App.StartScreen, menu, pill colours |
| `screens.py`, `ui.py`, `pa.py` | Every screen, layout helpers, pa.yaml emitter |
| `prepare_excel.py` | Makes `excel/EDS-Lab-Data-PowerApps.xlsx` from the real workbook |
| `make_msapp.py` | Packs `app/EDS-Lab-Portal.msapp` with `pac canvas pack --layout SourceCode` |
| `msapp-base/AlmTestApp.msapr` | App shell from Microsoft's PowerApps-Tooling test data (MIT licence), stripped of its content by `make_msapp.py` |
| `verify/run_all.sh` | Schema check, Microsoft serializer, Power Fx parse + type-check, 79-check workflow simulation, pack, screenshots |
| `verify/fxsim/` | C# host around Microsoft.PowerFx 1.8.1: binding check (`bind`), workflow simulation (`sim`), layout render (`render`) |
| `verify/hta_shortfall_test.js` | Drives the HTA in Chromium to show the shortfall bug and the v8.1 fix |

Requirements: Python 3 (openpyxl, pyyaml, jsonschema), .NET 8 and 10 SDKs, `pac` 2.12+ (`dotnet tool install -g Microsoft.PowerApps.CLI.Tool`), Node + Playwright for screenshots.
