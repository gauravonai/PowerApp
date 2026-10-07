"""Formulas for the 10-minute hand-built Live Data Test (docs/10). They read the Excel tables directly,
without any of the app's named formulas, so they prove the live link on their own. tools/verify checks them."""
SIGN = ('Switch(Upper(Trim(Text(Type))), "RECEIPT", 1, "RETURN", 1, "ADJUST+", 1, "ISSUE", -1, "SCRAP", -1, '
        '"ADJUST-", -1, 0) * Abs(Value(Text(Qty)))')
PARTS = '"Parts: " & CountRows(tblParts)'
MOVES = '"Movements: " & CountRows(tblMoves)'
ONHAND = ('"On hand: " & Sum(Filter(tblMoves, Upper(Trim(Text(PartNo))) = Upper(Trim(txtPart.Text))), %s)' % SIGN)
BOM = ('ForAll(Filter(Split(txtBom.Text, Char(10)), !IsBlank(Trim(Value))) As L, '
       'With({pn: Upper(Trim(First(Split(Trim(Substitute(Substitute(L.Value, Char(9), " "), Char(13), "")), " ")).Value))}, '
       '{Part: pn, OnHand: Sum(Filter(tblMoves, Upper(Trim(Text(PartNo))) = pn), %s)}))' % SIGN)
BOMROW = 'ThisItem.Part & "   →   on hand " & ThisItem.OnHand'
REFRESH = 'Refresh(tblParts); Refresh(tblMoves)'
