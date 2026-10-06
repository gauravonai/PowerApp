#!/usr/bin/env bash
# Rebuild everything and run every check. Needs: python3 (openpyxl, pyyaml, jsonschema), .NET 8 + 10 SDK,
# Power Platform CLI (pac), node + playwright (only for the screenshots).
set -euo pipefail
cd "$(dirname "$0")/../.."
SCHEMA=${SCHEMA:-tools/verify/pa.schema.yaml}
echo "== build";                python3 tools/build.py
echo "== yaml + schema";        python3 tools/verify/schema_check.py "$SCHEMA"
echo "== Microsoft serializer"; dotnet tools/verify/pav/bin/Release/net10.0/pav.dll app/Src paste
echo "== property names";     python3 tools/verify/prop_check.py
echo "== Power Fx parse";       python3 tools/verify/make_parse_list.py && dotnet tools/verify/fxparse/bin/Release/net8.0/fxh.dll parse tools/out/parse.json | tail -1
python3 tools/verify/export_data.py excel/EDS-Lab-Data-PowerApps.xlsx tools/out/data.json >/dev/null
python3 tools/verify/prep_bind.py tools/out/app.json tools/out/bind.json >/dev/null
echo "== Power Fx bind";        dotnet tools/verify/fxsim/bin/Release/net8.0/fxsim.dll bind tools/out/data.json tools/out/bind.json | tail -1
echo "== workflow simulation";  dotnet tools/verify/fxsim/bin/Release/net8.0/fxsim.dll render tools/out/data.json tools/out/bind.json tools/out/render > tools/out/sim.log; grep -E "FAIL|workflow simulation" tools/out/sim.log
echo "== every button";         dotnet tools/verify/fxsim/bin/Release/net8.0/fxsim.dll smoke tools/out/data.json tools/out/bind.json | tail -1
echo "== pack .msapp";          python3 tools/make_msapp.py | tail -2
echo "== screenshots";          python3 tools/verify/draw_html.py tools/out/render tools/out/html && node tools/verify/shoot.js tools/out/html tools/out/png full
