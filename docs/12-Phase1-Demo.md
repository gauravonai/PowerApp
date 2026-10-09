# Phase 1 demo: Engineer → BOM → Stock → Request → Lab Admin

What management sees: an engineer checks a harness BOM against live stock and raises a request in under two
minutes, and the Lab Admin has it immediately. Screenshots of every step: [`preview/phase1/`](preview/phase1).

This exact flow is run automatically on the real workbook before every release (`fxsim phase1`, 15 checks).

## Before the meeting (10 minutes, once)
1. Import `EDS-Lab-Portal-v2.0.7.msapp` into a **new** app, connect the 12 tables (plain names), Data row limit 2000.
2. Play → Login → **System Check**: all 18 rows OK.
3. Pick a demo engineer (any Users row with Role = Engineer) and a Lab Admin. Give each a password: on the Login
   page type the username and press **Forgot Password?** (or Login, if their Password cell is empty) and choose one.
   Quickest: type a password straight into their Password cell in the Users sheet.
4. In Excel, copy a real harness BOM (rows with Sr, part number, description, qty; units like `NOS` are fine).

## The demo (2 minutes)
| # | Who | Do | Show |
|---|---|---|---|
| 1 | Engineer | Welcome → **Log In**, type username + password | Dashboard greets them; menu has only engineer pages |
| 2 | Engineer | **Check Stock**, type part of a part number | Live on hand / reserved / available from the Movements sheet |
| 3 | Engineer | **BOM Compare** → paste the Excel rows → **Compare Against Stock** | Every line: Available / Shortage / Out of Stock / New Part, and the lines-read summary |
| 4 | Engineer | **Raise Part Request** → fill project details → **Submit Request** | Green banner "REQ-… is with the store", lands on My Requests |
| 5 | Lab Admin | **Log Out** → log in as the Lab Admin | Dashboard **Needs Your Action** lists the request; Request Queue badge = 1 |
| 6 | Lab Admin | Open the request | All lines with live availability, what is short, Approve / Reject / Reserve |

Optional: open the workbook in Excel Online next to the app: the new rows appear in **Requests** and
**RequestLines** as soon as the engineer submits.

## If something looks wrong
- Lists empty → System Check screenshot (usually duplicate `_1` tables or Power Fx 1.0 off).
- BOM line shows **New Part** for a part you know exists → the part number in Excel differs (extra character);
  Check Stock with part of the number shows the exact spelling.
