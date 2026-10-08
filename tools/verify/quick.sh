#!/usr/bin/env bash
# Fast loop: build + schema + property names + parse + bind + simulation (no pack, no screenshots).
set -uo pipefail
cd "$(dirname "$0")/../.."
export PLAIN_DS=1
python3 tools/build.py | tail -2 || exit 1
python3 tools/verify/schema_check.py tools/verify/pa.schema.yaml | tail -1
python3 tools/verify/prop_check.py | tail -3
python3 tools/verify/make_parse_list.py && dotnet tools/verify/fxparse/bin/Release/net8.0/fxh.dll parse tools/out/parse.json | tail -5
python3 tools/verify/export_data.py excel/EDS-Lab-Data-PowerApps.xlsx tools/out/data.json >/dev/null
python3 tools/verify/prep_bind.py tools/out/app.json tools/out/bind.json >/dev/null
dotnet tools/verify/fxsim/bin/Release/net8.0/fxsim.dll bind tools/out/data.json tools/out/bind.json | tail -${BINDN:-30}
if [ "${SIM:-1}" = 1 ]; then dotnet tools/verify/fxsim/bin/Release/net8.0/fxsim.dll sim tools/out/data.json tools/out/bind.json > tools/out/sim.log 2>&1; grep -E "FAIL|workflow simulation|Exception|error" tools/out/sim.log | head -20; fi
if [ "${SIM:-1}" = 1 ]; then dotnet tools/verify/fxsim/bin/Release/net8.0/fxsim.dll smoke tools/out/data.json tools/out/bind.json | tail -1; fi
