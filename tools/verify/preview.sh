#!/usr/bin/env bash
# Render every screen after the workflow simulation and screenshot it (tools/out/png).
set -uo pipefail
cd "$(dirname "$0")/../.."
O=tools/out; rm -rf $O/render $O/html $O/png
dotnet tools/verify/fxsim/bin/Release/net8.0/fxsim.dll render $O/data.json $O/bind.json $O/render > $O/sim.log 2>&1
grep -E "FAIL|workflow simulation|rendered" $O/sim.log
python3 tools/verify/draw_html.py $O/render $O/html && node tools/verify/shoot.js $O/html $O/png ${FULL:-}
