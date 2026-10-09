// Phase 1 proof for management: an ENGINEER logs in, pastes a BOM, checks stock, raises a request, and the
// request lands with the LAB ADMIN. Every step runs the app's real formulas on the real workbook and is
// screenshotted (tools/out/phase1/*.json -> draw_html -> png).
using System.Text.Json;
using Microsoft.PowerFx;
using Microsoft.PowerFx.Types;

public static class Phase1 {
  static Host H; static int Fail = 0, Pass = 0, Step = 0; static string Dir;
  static string P(string ctl, string prop) => H.Ctl[ctl].GetProperty("props").GetProperty(prop).GetString();
  static FormulaValue E(string expr) => H.Run(expr, null);
  static string S(string expr) { var v = E(expr); return v is BlankValue ? "" : v is StringValue s ? s.Value : v.ToObject()?.ToString(); }
  static double N(string expr) { var v = E(expr); return v is BlankValue ? 0 : Convert.ToDouble(v.ToObject()); }
  static void Ok(bool c, string what) { if (c) { Pass++; Console.WriteLine("  PASS  " + what); } else { Fail++; Console.WriteLine("  FAIL  " + what); } }
  static void Touch() { foreach (var t in H.TableTypes.Keys) H.Engine.UpdateVariable(t, H.Engine.GetValue(t)); foreach (var c in new[] { "colBom", "colNP", "colInvLines", "colCostLines", "colShots" }) H.Engine.UpdateVariable(c, H.Engine.GetValue(c)); }
  static string Do(string ctl) {
    MockNotify.Log.Clear();
    var r = H.Engine.Eval(P(ctl, "OnSelect"), null, H.Opts);
    if (r is ErrorValue ev) throw new Exception(ctl + ": " + string.Join("; ", ev.Errors.Select(e => e.Message)));
    Touch();
    foreach (var l in MockNotify.Log) Console.WriteLine("        notify " + l);
    return MockNotify.Log.LastOrDefault();
  }
  static void Txt(string c, string v) => H.SetCtl(c, "Text", FormulaValue.New(v));
  static void Sel(string c, string v) => H.SetCtl(c, "Selected", FormulaValue.NewRecordFromFields(new NamedValue("Value", FormulaValue.New(v))));
  static void Dt(string c, DateTime d) => H.SetCtl(c, "SelectedDate", FormulaValue.NewDateOnly(d.Date));
  static void Shot(string scr, string name, string toast = null) {
    Step++; Render.Shot(H, scr, Path.Combine(Dir, $"{Step:00}-{name}.json"), toast);
    Console.WriteLine($"        screenshot {Step:00}-{name} ({scr})");
  }
  static string Screen() => MockNav.Log.LastOrDefault();

  public static int Run(Host h, string dir) {
    H = h; Dir = dir; Directory.CreateDirectory(dir);
    h.MockControls(g => { var cr = h.Engine.Check(P(g, "Items"), h.ParamType(g, null), h.Opts); return ((TableType)cr.ReturnType).ToRecord(); });
    foreach (var (name, c) in h.Ctl) if (c.GetProperty("type").GetString().EndsWith("DropDown")) {
      var props = c.GetProperty("props");
      string v = props.TryGetProperty("Default", out var d) && !d.GetString().Contains("ThisItem") && !d.GetString().Contains("gInv") ? S(d.GetString()) : null;
      if (string.IsNullOrEmpty(v) && !props.GetProperty("Items").GetString().Contains("ThisItem")) { try { v = S("First(" + props.GetProperty("Items").GetString() + ").Value"); } catch { } }
      if (v != null) Sel(name, v);
    }
    E(h.App.GetProperty("onstart").GetString()); Touch();
    var hx = h.App.GetProperty("tests").GetProperty("hash_fx").GetString();
    string Hash(string pw, string user) => S(hx.Replace("\"PW\"", "\"" + pw + "\"").Replace("\"SALT\"", "\"" + user + "\""));
    const string ENG = "akshay.kakde", ADM = "abhijit.dubey", PW = "Lab2026x";
    foreach (var u in new[] { ENG, ADM }) E($"Patch(tblUsers, LookUp(tblUsers, Username = \"{u}\"), {{Password: \"{Hash(PW, u)}\"}})");
    Touch();
    var engName = S($"LookUp(tblUsers, Username = \"{ENG}\").FullName");
    var reqBefore = N("CountRows(nfReq)");

    Console.WriteLine($"== Step 1. Engineer logs in ({engName}, role {S($"LookUp(tblUsers, Username = \"{ENG}\").Role")})");
    Shot("scrWelcome", "welcome");
    Do("goWl");
    Txt("usrLi", ENG); Txt("pwdLi", PW);
    Shot("scrLogin", "login-engineer");
    var t = Do("goLi");
    Ok(S("gRole") == "Engineer" && S("gMeName") == engName && Screen() == "scrDash", $"logged in as {engName}, Engineer, Dashboard opened");
    var nav = ((TableValue)E(P("navGalDsh", "Items"))).Rows.Select(r => ((StringValue)r.Value.GetField("Label")).Value).ToList();
    Ok(nav.Contains("Check Stock") && nav.Contains("BOM Compare") && nav.Contains("New Request") && nav.Contains("My Requests") && !nav.Contains("Request Queue") && !nav.Contains("Team Access"),
       "engineer menu: Check Stock, BOM Compare, New Request, My Requests (no admin pages)");
    Shot("scrDash", "engineer-dashboard", t);

    Console.WriteLine("== Step 2. Engineer checks stock");
    var pn = S("First(Sort(Filter(nfStock, OnHand > 20 && Reserved = 0), OnHand, SortOrder.Descending)).PartNo");
    var pnLow = S("First(Filter(nfStock, Status = \"LOW STOCK\" && Avail > 0)).PartNo");
    var pnOut = S("First(Filter(nfStock, Status = \"OUT OF STOCK\")).PartNo");
    Txt("qStk", pn.Substring(0, Math.Min(5, pn.Length)));
    var rows = (TableValue)E(P("stStkGal", "Items"));
    Ok(rows.Rows.Any(r => ((StringValue)r.Value.GetField("PartNo")).Value == pn), $"searching '{pn.Substring(0, Math.Min(5, pn.Length))}' finds {pn} (on hand {N($"LookUp(nfStock, PartNo = \"{pn}\").OnHand")})");
    Shot("scrStock", "check-stock");
    Txt("qStk", "");

    Console.WriteLine("== Step 3. Engineer pastes the harness BOM (copied from Excel: Sr, part, description, qty)");
    var onBefore = N($"LookUp(nfStock, PartNo = \"{pn}\").OnHand");
    // real workbooks often carry invisible characters in part-number cells (copied from SAP/web): a trailing
    // non-breaking space, a tab, a zero-width space. Put them into the Parts sheet and expect the BOM to still match.
    E($"Patch(tblParts, LookUp(tblParts, Text(PartNo) = \"{pn}\"), {{PartNo: \"{pn}\" & Char(160) & Char(9)}})");
    E($"Patch(tblParts, LookUp(tblParts, Text(PartNo) = \"{pnLow}\"), {{PartNo: UniChar(8203) & \"{pnLow}\" & Char(160)}})");
    Touch();
    Txt("qStk", pn);
    var diag = S("With({k: Upper(Trim(qStk.Text))}, \"Typed: [\" & k & \"] \" & Len(k) & \" chars  |  exact match: \" & CountRows(Filter(tblParts, Upper(Text(PartNo)) = k)) & \"  |  contains: \" & CountRows(Filter(tblParts, k in Upper(Text(PartNo)))) & \"  |  Excel cell: [\" & LookUp(tblParts, k in Upper(Text(PartNo))).PartNo & \"] \" & Len(LookUp(tblParts, k in Upper(Text(PartNo))).PartNo) & \" chars\")");
    Console.WriteLine("        diagnostic label: " + diag);
    Ok(diag.Contains("exact match: 0") && diag.Contains("contains: 1"), "docs/14 diagnostic label spots the invisible character (exact 0, contains 1)");
    Txt("qStk", "");
    Ok(S($"LookUp(nfStock, PN = \"{pn}\").PN") == pn && N($"LookUp(nfStock, PN = \"{pn}\").OnHand") == onBefore, "hidden characters in the Parts sheet (non-breaking space, tab, zero-width space) are ignored: same part, same on hand");
    var desc = S($"LookUp(nfStock, PartNo = \"{pn}\").Description");
    var bom = $"Sr\tPart Number\tDescription\tQty\n1\t{pn}\t{desc}\t10\n2\t{pnLow}\t{S($"LookUp(nfStock, PartNo = \"{pnLow}\").Description")}\t{N($"LookUp(nfStock, PartNo = \"{pnLow}\").Avail") + 5} NOS\n3\t{pnOut}\tOut of stock part\t4\n4\tNEW/PART-0099\tNot in catalogue\t2\n5\tMC000AAOAVO2IH 4001 8\tPart number with spaces\t3";
    E($"Set(gBomText, \"{bom.Replace("\"", "\"\"").Replace("\n", "\" & Char(10) & \"").Replace("\t", "\" & Char(9) & \"")}\")");
    Txt("txtBom", S("gBomText"));
    t = Do("goBom");
    Ok(N("CountRows(colBom)") == 5, "5 BOM lines read (header row skipped, Sr column ignored, 'NOS' unit ignored)");
    Ok(N("LookUp(colBom, PN = \"MC000AAOAVO2IH 4001 8\").Qty") == 3 && S("LookUp(colBom, PN = \"MC000AAOAVO2IH 4001 8\").Status") != "NEW PART", "part number with spaces (MC000AAOAVO2IH 4001 8) found in stock, qty 3");
    Ok(S($"LookUp(colBom, PartNo = \"{pn}\").Status") == "AVAILABLE" && S($"LookUp(colBom, PartNo = \"{pnLow}\").Status") == "SHORTAGE"
       && S($"LookUp(colBom, PartNo = \"{pnOut}\").Status") == "OUT OF STOCK" && S("LookUp(colBom, PN = \"NEW/PART-0099\").Status") == "NEW PART",
       "stock check per line: Available / Shortage / Out of Stock / New Part");
    Ok(N($"LookUp(colBom, PartNo = \"{pn}\").OnHand") == N($"LookUp(nfStock, PartNo = \"{pn}\").OnHand"), "on hand shown = live stock from the Movements sheet");
    Shot("scrBom", "bom-compare", t);

    Console.WriteLine("== Step 4. Engineer raises the request");
    Do("reqBom");
    Ok(Screen() == "scrNewReq", "Raise Part Request opens New Request with the 5 BOM lines carried over");
    foreach (var (c, v) in new[] { ("machNr", "3CX 74KW"), ("pcodeNr", "PCODE-00042"), ("harnNr", "405/F8525"), ("ccNr", "IDC00005"), ("bucNr", "Shashank G"), ("dccNr", "Mahendra M"), ("circNr", "48"), ("scopeNr", "New cab harness for the 74 kW variant: add work-light circuit, move fuse box to the left pillar.") }) Txt(c, v);
    Sel("stageNr", "Proto"); Sel("buNr", "BHL India");
    Dt("needNr", DateTime.Today.AddDays(10));
    Shot("scrNewReq", "new-request-filled");
    t = Do("subNr");
    var REQ = S($"First(Sort(Filter(nfReq, RaisedByEmail = \"{ENG}\"), RequestNo, SortOrder.Descending)).RequestNo");
    Ok(N("CountRows(nfReq)") == reqBefore + 1 && REQ.StartsWith("REQ-"), $"{REQ} written to the Requests sheet, status {S($"LookUp(nfReq, RequestNo = \"{REQ}\").Status")}");
    Ok(N($"CountRows(Filter(nfLines, RequestNo = \"{REQ}\"))") == 5, "its 5 lines written to the RequestLines sheet");
    Ok(S($"LookUp(nfReq, RequestNo = \"{REQ}\").RaisedByName") == engName, $"saved under {engName}");
    Ok(Screen() == "scrMyReq" && ((TableValue)E(P("rlMyGal", "Items"))).Rows.Any(r => ((StringValue)r.Value.GetField("RequestNo")).Value == REQ), $"My Requests shows {REQ}");
    Shot("scrMyReq", "my-requests", t);
    E($"Set(gReqNo, \"{REQ}\")");
    Shot("scrReqDetail", "engineer-request-detail");

    Console.WriteLine("== Step 5. The request reaches the Lab Admin");
    Do("hdrOutDsh");
    Txt("usrLi", ADM); Txt("pwdLi", PW);
    t = Do("goLi");
    Ok(S("gRole") == "Lab Admin", $"{S("gMeName")} logged in as Lab Admin");
    Ok(N("nfQueueCount") >= 1 && ((TableValue)E(P("rqDshGal", "Items"))).Rows.Any(r => ((StringValue)r.Value.GetField("RequestNo")).Value == REQ), $"Lab Admin dashboard lists {REQ} under Needs Your Action (queue badge {N("nfQueueCount")})");
    Shot("scrDash", "lab-admin-dashboard", t);
    var q = ((TableValue)E(P("rlQuGal", "Items"))).Rows.ToList();
    Ok(q.Any(r => ((StringValue)r.Value.GetField("RequestNo")).Value == REQ && ((StringValue)r.Value.GetField("RaisedByName")).Value == engName), $"Request Queue: {REQ} from {engName}, status Submitted");
    Shot("scrQueue", "lab-admin-queue");
    E($"Set(gReqNo, \"{REQ}\")");
    Shot("scrReqDetail", "lab-admin-request-detail");

    Console.WriteLine($"\nphase 1 (engineer -> lab admin): {Pass} passed, {Fail} failed, {Step} screenshots");
    return Fail;
  }
}
