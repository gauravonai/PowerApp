# Optional: HTA v8.1 (shortfall fix only)

`EDS-Lab-Portal-v8.1.hta` = your v8 HTA with one formula changed in 5 places:
shortfall = requested − max(reserved, released) instead of requested − reserved − released.
See `shortfall-fix.diff` and `../docs/06-Differences-and-HTA-bug.md` §2 for the proof.

To use it: keep a copy of your current `EDS-Lab-Portal.hta`, then put this file next to `EDS-Lab-Data.xlsx`
and rename it to `EDS-Lab-Portal.hta`. Nothing else (workbook, _pending folder) changes.
