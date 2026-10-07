// Runs the app's real button formulas (from the generated pa.yaml) against the real workbook data,
// in Microsoft's Power Fx engine, and asserts the business rules of the HTA.
using System.Text.Json;
using Microsoft.PowerFx;
using Microsoft.PowerFx.Types;

public static class Sim {
  static Host H; static int Fail = 0, Pass = 0;
  static string P(string ctl, string prop) => H.Ctl[ctl].GetProperty("props").GetProperty(prop).GetString();
  static void Ok(bool c, string what) { if (c) { Pass++; Console.WriteLine("  PASS  " + what); } else { Fail++; Console.WriteLine("  FAIL  " + what); } }
  static FormulaValue E(string expr, RecordValue p = null) => H.Run(expr, p);
  static string S(string expr) { var v = E(expr); return v is BlankValue ? "" : v is StringValue s ? s.Value : v.ToObject()?.ToString(); }
  static double N(string expr) { var v = E(expr); return v is BlankValue ? 0 : Convert.ToDouble(v.ToObject()); }
  static void Touch() { foreach (var t in H.TableTypes.Keys) H.Engine.UpdateVariable(t, H.Engine.GetValue(t)); foreach (var c in new[] { "colBom", "colNP", "colInvLines", "colCostLines", "colShots" }) H.Engine.UpdateVariable(c, H.Engine.GetValue(c)); }
  static void Do(string ctl, string prop = "OnSelect", RecordValue p = null) {
    MockNotify.Log.Clear();
    var r = H.Engine.Eval(P(ctl, prop), p, H.Opts);
    if (r is ErrorValue ev) throw new Exception(ctl + "." + prop + ": " + string.Join("; ", ev.Errors.Select(e => e.Message)));
    Touch();
    foreach (var l in MockNotify.Log) Console.WriteLine("        notify " + l);
  }
  static void Txt(string c, string v) => H.SetCtl(c, "Text", FormulaValue.New(v));
  static void Sel(string c, string v) => H.SetCtl(c, "Selected", FormulaValue.NewRecordFromFields(new NamedValue("Value", FormulaValue.New(v))));
  static void Dt(string c, DateTime d) => H.SetCtl(c, "SelectedDate", FormulaValue.NewDateOnly(d.Date));

  public static int Run(Host h) {
    H = h;
    var itemTypes = new Dictionary<string, RecordType>();
    h.MockControls(g => { var cr = h.Engine.Check(P(g, "Items"), h.ParamType(g, null), h.Opts); var t = ((TableType)cr.ReturnType).ToRecord(); itemTypes[g] = t; return t; });
    foreach (var (name, c) in h.Ctl) if (c.GetProperty("type").GetString().EndsWith("DropDown")) {   // dropdowns start on their Default (or first item)
      var props = c.GetProperty("props");
      string v = props.TryGetProperty("Default", out var d) && !d.GetString().Contains("ThisItem") && !d.GetString().Contains("gInv") ? S(d.GetString()) : null;
      if (string.IsNullOrEmpty(v) && !props.GetProperty("Items").GetString().Contains("ThisItem")) { try { v = S("First(" + props.GetProperty("Items").GetString() + ").Value"); } catch { } }
      if (v != null) Sel(name, v);
    }

    Console.WriteLine("== 1. log in: username + password from the Users tab");
    E(h.App.GetProperty("onstart").GetString()); Touch();
    var tests = h.App.GetProperty("tests");
    Ok(S("gRole") == "" && S("gMeName") == "", "nobody is signed in when the app opens");
    var canon = tests.GetProperty("role_canon").GetString();
    foreach (var (raw, wantRole) in new[] { ("Lab Lead", "Lab Lead"), ("lab admin", "Lab Admin"), ("Admin", "Lab Admin"), ("Store", "Lab Admin"), ("Lab In-charge", "Lab Admin"), ("Manager", "Manager"), ("mgr", "Manager"), ("Engineer", "Engineer"), ("Tester", "Engineer"), ("", "Engineer"), ("Pending", "Pending"), ("disabled", "Disabled") }) {
      var got = S(canon.Replace("RAWROLE", "\"" + raw + "\""));
      Ok(got == wantRole, $"role text '{raw}' -> {wantRole} (got {got})");
    }
    var hx = tests.GetProperty("hash_fx").GetString();
    foreach (var v in tests.GetProperty("hash_vectors").EnumerateArray()) {
      var pw = v[0].GetString(); var salt = v[1].GetString(); var wantH = v[2].GetString();
      var got = S(hx.Replace("\"PW\"", "\"" + pw.Replace("\"", "\"\"") + "\"").Replace("\"SALT\"", "\"" + salt + "\""));
      Ok(got == wantH, $"password scramble of '{pw}' matches the reference implementation ({got.Substring(0, 13)}...)");
    }
    void Login(string u, string p) { Txt("usrLi", u); Txt("pwdLi", p); Do("goLi"); }
    void Logout() { Do("hdrOutDsh"); }
    Login("", ""); Ok(S("gLoginMsg") == "Type your username.", "empty username -> 'Type your username.'");
    Login("nobody.here", "x"); Ok(S("gLoginMsg").StartsWith("No account"), "unknown username refused");
    Login("Gaurav.Shelke", "");
    Ok(S("gLoginMode") == "setpw" && S("gRole") == "", "first login of gaurav.shelke (no password yet, same person as this PC's account) -> choose a password");
    Txt("np1Li", "abc"); Txt("np2Li", "abc"); Do("spLi"); Ok(S("gLoginMsg").StartsWith("At least 6"), "password 'abc' refused (too short)");
    Txt("np1Li", "abcdefg"); Txt("np2Li", "abcdefg"); Do("spLi"); Ok(S("gLoginMsg").StartsWith("At least 6"), "password without a number refused");
    Txt("np1Li", "abc123"); Txt("np2Li", "abc124"); Do("spLi"); Ok(S("gLoginMsg").Contains("do not match"), "mismatched confirmation refused");
    Txt("np2Li", "abc123"); Do("spLi");
    var hv = tests.GetProperty("hash_vectors")[0][2].GetString();
    Ok(S("gRole") == "Lab Lead" && S("gMeName") == "Gaurav Shelke" && S("gMeInitials") == "GS" && MockNav.Log.LastOrDefault() == "scrDash", "password saved and logged in: Gaurav Shelke, GS, Lab Lead, Dashboard");
    Ok(S("LookUp(tblUsers, Username = \"gaurav.shelke\").Password") == hv && !S("LookUp(tblUsers, Username = \"gaurav.shelke\").Password").Contains("abc123"), "Users.Password holds the scrambled value, never 'abc123'");
    Ok(N("CountRows(gRoleOptions)") == 3, "Lab Lead can view as Engineer / Lab Admin / Manager");
    Logout(); Ok(S("gRole") == "" && MockNav.Log.LastOrDefault() == "scrLogin", "Log Out clears the session and returns to the login page");
    Login("gaurav.shelke", "abc999"); Ok(S("gRole") == "" && S("gLoginMsg") == "That password is not right." && N("gLoginTries") == 1, "wrong password refused, attempt counted");
    Login("gaurav.shelke", "abc123"); Ok(S("gRole") == "Lab Lead" && N("gLoginTries") == 0, "right password logs in");
    var eng = "akshay.aadarsh";
    var engRow = (RecordValue)E($"LookUp(tblUsers, Username = \"{eng}\")");
    Logout(); Login(eng, "whatever");
    Ok(S("gRole") == "" && S("gLoginMsg").Contains("no password yet"), "another person with no password cannot claim the account from this PC");
    Login("gaurav.shelke", "abc123");
    Do("tmC6t", "OnSelect", FormulaValue.NewRecordFromFields(new NamedValue("ThisItem", engRow)));
    var code = S("gTempCode"); code = code.Substring(code.Length - 6);
    Ok(S($"LookUp(tblUsers, Username = \"{eng}\").Password").StartsWith("t1$") && code.All(char.IsDigit), $"Lab Lead gives {eng} a temporary password ({code}), stored scrambled");
    Logout(); Login(eng, code);
    Ok(S("gLoginMode") == "setpw", "temporary password accepted -> must choose own password");
    Txt("np1Li", "Pune2026x"); Txt("np2Li", "Pune2026x"); Do("spLi");
    Ok(S("gRole") == "Engineer" && N("CountRows(gRoleOptions)") == 1, "engineer logged in, Engineer only");
    Logout(); Login(eng, code); Ok(S("gRole") == "", "the temporary password no longer works once used");
    E($"Patch(tblUsers, LookUp(tblUsers, Username = \"{eng}\"), {{Role: \"Engineer, Manager\"}})"); Touch();
    Login(eng, "Pune2026x");
    Ok(S("gRole") == "Engineer" && N("CountRows(gRoleOptions)") == 2 && S("Last(gRoleOptions).Value") == "Manager", "Role 'Engineer, Manager' -> opens as Engineer, can switch to Manager");
    Logout();
    E("Set(gLoginMode, \"register\")");
    foreach (var (c, v) in new[] { ("rgNLi", "Test Person"), ("rgULi", "test.person"), ("rgBLi", "EDS"), ("rgMLi", ""), ("rgP1Li", "abc12345"), ("rgP2Li", "abc12345") }) Txt(c, v);
    Do("rsLi");
    Ok(S("LookUp(tblUsers, Username = \"test.person\").Role") == "Pending" && S("gLoginMsg").StartsWith("✓"), "Register creates a Pending row in Users");
    Do("rsLi"); Ok(S("gLoginMsg").Contains("already exists"), "registering the same username twice is refused");
    Login("test.person", "abc12345"); Ok(S("gRole") == "" && S("gLoginMsg").Contains("waiting"), "a pending person cannot log in until approved");
    E("Patch(tblUsers, LookUp(tblUsers, Username = \"test.person\"), {Role: \"Engineer\"})"); Touch();
    Login("test.person", "abc12345"); Ok(S("gRole") == "Engineer", "after approval (Role = Engineer) the person logs in");
    Logout(); Login("gaurav.shelke", "abc123");

    Console.WriteLine("== 0. hand-built Live Data Test formulas (docs/10), straight from the tables");
    var hand = tests.GetProperty("hand");
    Ok(S(hand.GetProperty("PARTS").GetString()) == "Parts: 418" && S(hand.GetProperty("MOVES").GetString()) == "Movements: 775", "Parts: 418 · Movements: 775");
    var onExp = N("LookUp(nfStock, PartNo = \"7213/0024\").OnHand");
    Ok(S(hand.GetProperty("ONHAND").GetString().Replace("txtPart.Text", "\"7213/0024\"")) == "On hand: " + onExp, $"On hand of 7213/0024 = {onExp}, same as the app");
    var bomRows = (TableValue)E(hand.GetProperty("BOM").GetString().Replace("txtBom.Text", "nfSampleBom"));
    var bomOk = bomRows.Rows.All(r => { var pn = ((StringValue)r.Value.GetField("Part")).Value; var oh = Convert.ToDouble(r.Value.GetField("OnHand").ToObject() ?? 0.0);
      return Math.Abs(oh - N($"Coalesce(LookUp(nfStock, PN = \"{pn}\").OnHand, 0)")) < 1e-9; });
    Ok(bomRows.Rows.Count() == 5 && bomOk, "BOM test: 5 lines, every on hand equals the app's live stock");

    Console.WriteLine("== 1b. Data Health: the app read every row the workbook counts");
    Ok(N("nXlParts") == 418 && N("nAppParts") == 418 && N("nXlMoves") == 775 && N("nAppMoves") == 775, $"Excel ROWS() = app rows: parts 418/418, movements {N("nXlMoves")}/{N("nAppMoves")}");
    Ok(Math.Abs(N("nXlStock") - N("nAppStock")) < 0.001 && S("nfHealthText") == "All rows read", $"Excel stock total {N("nXlStock")} = app total {N("nAppStock")} -> '{S("nfHealthText")}'");

    Console.WriteLine("== 2. live stock = sum of Movements (same rule as the LiveStock SUMIFS)");
    var exp = new Dictionary<string, double>();
    foreach (RecordValue r in ((TableValue)E("tblMoves")).Rows.Select(x => x.Value)) {
      var pn = (r.GetField("PartNo") as StringValue)?.Value?.Trim().ToUpperInvariant(); if (pn == null) continue;
      var t = (r.GetField("Type") as StringValue)?.Value?.ToUpperInvariant() ?? ""; var q = Math.Abs(Convert.ToDouble(r.GetField("Qty").ToObject() ?? 0));
      var s = t is "RECEIPT" or "RETURN" or "ADJUST+" ? 1 : t is "ISSUE" or "SCRAP" or "ADJUST-" ? -1 : 0;
      exp[pn] = exp.GetValueOrDefault(pn) + s * q;
    }
    int mism = 0, parts = 0;
    foreach (RecordValue r in ((TableValue)E("nfStock")).Rows.Select(x => x.Value)) {
      parts++; var pn = ((StringValue)r.GetField("PN")).Value; var on = Convert.ToDouble(r.GetField("OnHand").ToObject());
      if (Math.Abs(Math.Round(exp.GetValueOrDefault(pn), 3) - on) > 1e-6) mism++;
    }
    Ok(parts == 418 && mism == 0, $"OnHand matches the movement sum for all {parts} active parts ({mism} mismatches)");
    Console.WriteLine($"        stock: {N("CountRows(Filter(nfStock, Status = \"OUT OF STOCK\"))")} out, {N("CountRows(Filter(nfStock, Status = \"LOW STOCK\"))")} low, {N("CountRows(Filter(nfStock, Status = \"IN STOCK\"))")} in stock");
    Ok(N("CountRows(Filter(nfStock, Status = \"OUT OF STOCK\"))") == 10 && N("CountRows(Filter(nfStock, Status = \"LOW STOCK\"))") == 37, "OUT OF STOCK = 10 and LOW STOCK = 37, the same counts the HTA dashboard shows for this workbook");

    Console.WriteLine("== 3. BOM compare (sample harness)");
    Txt("txtBom", S("nfSampleBom")); Do("goBom");
    Ok(N("CountRows(colBom)") == 5, "5 lines parsed from tab / double-space / comma separated text");
    Ok(S("LookUp(colBom, PN = \"NEW/PART-0001\").Status") == "NEW PART", "unknown part -> NEW PART");
    Ok(N("CountRows(Filter(colBom, Status = \"OUT OF STOCK\"))") == 1 && N("CountRows(Filter(colBom, Status = \"AVAILABLE\"))") == 3, "1 OUT OF STOCK, 3 AVAILABLE");

    Console.WriteLine("== 4. the manager's case: engineer asks 50, only 40 on the shelf");
    var pick = E("First(Filter(nfStock, OnHand = 40 && Reserved = 0))");
    string P40 = pick is RecordValue pr ? ((StringValue)pr.GetField("PartNo")).Value : null;
    if (P40 == null) { P40 = S("First(Filter(nfStock, OnHand >= 10 && OnHand <= 200 && Reserved = 0)).PartNo"); }
    var on40 = N($"LookUp(nfStock, PartNo = \"{P40}\").OnHand");
    var want = on40 + 10;
    Console.WriteLine($"        using part {P40}: on hand {on40}, request {want}");
    Txt("txtBom", P40 + "\t" + want + "\n" + S("First(Split(nfSampleBom, Char(10))).Value")); Do("goBom");
    Ok(S($"LookUp(colBom, PartNo = \"{P40}\").Status") == "SHORTAGE" && N($"LookUp(colBom, PartNo = \"{P40}\").Short") == 10, "BOM compare shows SHORTAGE with short = 10");

    Console.WriteLine("== 5. NEW REQUEST submit");
    foreach (var (c, v) in new[] { ("machNr", "3CX 74KW"), ("pcodeNr", "PCODE-00042"), ("harnNr", "405/F8525"), ("ccNr", "IDC00005"), ("bucNr", "Shashank G"), ("dccNr", "Mahendra M"), ("circNr", ""), ("scopeNr", "Test scope") }) Txt(c, v);
    Dt("needNr", DateTime.Today.AddDays(7));
    Do("subNr");
    Ok(N("CountRows(nfReq)") == 0, "circuits missing -> request NOT created (mandatory field)");
    Txt("circNr", "48"); Do("subNr");
    var REQ = S("First(nfReq).RequestNo");
    Ok(REQ == "REQ-" + DateTime.Today.Year + "-00001", "request number REQ-YYYY-00001 (got " + REQ + ")");
    Ok(S("First(nfReq).Status") == "SUBMITTED" && N("First(nfReq).NoOfCircuits") == 48, "status SUBMITTED, circuits 48");
    Ok(N($"CountRows(Filter(nfLines, RequestNo = \"{REQ}\"))") == 2, "2 RequestLines rows written");
    Ok(S($"LookUp(nfLines, RequestNo = \"{REQ}\" && PartNo = \"{P40}\").LineStatus") == "PARTIAL", "line status PARTIAL at submit");
    Ok(N("CountRows(colBom)") == 0 && MockNav.Log.LastOrDefault() == "scrMyReq", "BOM cleared and user sent to My Requests");
    Ok(N($"CountRows(Table(ParseJSON(LookUp(nfReq, RequestNo = \"{REQ}\").History)))") == 1, "History holds 1 JSON event");

    Console.WriteLine("== 6. Lab Admin: Reserve available stock");
    E($"Set(gReqNo, \"{REQ}\")"); Do("resRd");
    Ok(N($"LookUp(nfLines, RequestNo = \"{REQ}\" && PartNo = \"{P40}\").QtyReserved") == on40, $"reserved exactly what was on the shelf ({on40})");
    Ok(S($"LookUp(nfReq, RequestNo = \"{REQ}\").Status") == "PURCHASE REQUIRED", "request -> PURCHASE REQUIRED");
    Ok(N($"LookUp(nfStock, PartNo = \"{P40}\").Avail") == 0 && N($"LookUp(nfStock, PartNo = \"{P40}\").OnHand") == on40, "reserving does not move stock: on hand unchanged, available 0");
    Ok(N($"CountRows(Filter(nfPurch, PartNo = \"{P40}\" && RequestNo = \"{REQ}\" && QtyRequired = 10))") == 1, "shortfall 10 put on Ongoing Purchase automatically");
    Ok(N($"LookUp(nfShortBook, PartNo = \"{P40}\").Qty") == 10, "shortfall book shows 10");

    Console.WriteLine("== 7. Lab Admin: RELEASE what is reserved");
    var movesBefore = N("CountRows(nfMoves)");
    var gt = (RecordType)H.CtlTypes["lnRdGal"];
    void Lines(string relText) {
      var all = E($"AddColumns(Sort(Filter(nfLines, RequestNo = \"{REQ}\"), Sr), lnRdC9, {{Text: {relText}}})");
      H.Engine.UpdateVariable("lnRdGal", FormulaValue.NewRecordFromFields(gt, new NamedValue("AllItems", all), new NamedValue("Selected", FormulaValue.NewBlank(itemTypes["lnRdGal"]))));
    }
    Lines("\"999\""); Do("relRd");
    Ok(N("CountRows(nfMoves)") == movesBefore && MockNotify.Log.Any(l => l.StartsWith("NotificationType.Error")), "typing more than is reserved is refused, nothing posted");
    Lines("Text(QtyReserved - QtyReleased)"); Do("relRd");
    Ok(N("CountRows(nfMoves)") == movesBefore + 2, "one ISSUE movement per released line (2)");
    Ok(N($"LookUp(nfStock, PartNo = \"{P40}\").OnHand") == 0, $"stock of {P40} dropped by exactly {on40} -> 0");
    Ok(S("Last(nfMoves).Type") == "RELEASE" && S("Last(nfMoves).RawType") == "ISSUE" && S("Last(nfMoves).Reference") == REQ && S("Left(Last(nfMoves).EntryId, 4)") == "TXN-", "movement typed ISSUE (shown as RELEASE), referenced to the request, with an EntryId");
    var line = $"LookUp(nfLines, RequestNo = \"{REQ}\" && PartNo = \"{P40}\")";
    Ok(N(line + ".QtyReleased") == on40 && N(line + ".QtyRequested") == want, $"line: requested {want}, released {on40}");
    Ok(N($"Max(0, {line}.QtyRequested - Max({line}.QtyReserved, {line}.QtyReleased))") == 10, "shortfall 10 still visible on the line after release");
    Ok(S($"LookUp(nfReq, RequestNo = \"{REQ}\").Status") == "PARTIALLY RELEASED", "request -> PARTIALLY RELEASED");
    Ok(N($"LookUp(nfShortBook, PartNo = \"{P40}\").Qty") == 10, "shortfall book still shows 10 after release (the HTA formula lost it here)");
    Ok(S("First(nfLedger).IssuedTo") == "Gaurav Shelke" && S("First(nfLedger).Harness") == "405/F8525", "ledger joins the release to requester and harness");
    Lines("\"5\""); var mb = N("CountRows(nfMoves)"); Do("relRd");
    Ok(N("CountRows(nfMoves)") == mb, "a second release with nothing left reserved posts nothing");

    Console.WriteLine("== 8. Request the shortfall separately");
    E($"Set(gShortSr, {line}.Sr)");
    Txt("sfPnRd", P40); Txt("sfQRd", "10"); Txt("sfNRd", "needed by Friday");
    Do("sfGoRd");
    var SHT = S("First(Filter(nfReq, Kind = \"SHORTAGE\")).RequestNo");
    Ok(SHT == "SHT-" + DateTime.Today.Year + "-00002", "shortfall request SHT-YYYY-00002 created (got " + SHT + ")");
    Ok(S($"LookUp(nfReq, RequestNo = \"{SHT}\").ParentRequest") == REQ && S($"LookUp(nfReq, RequestNo = \"{SHT}\").RaisedByEmail") == S("gMeEmail"), "ParentRequest = original, requester kept");
    Ok(N($"First(Filter(nfLines, RequestNo = \"{SHT}\")).QtyRequested") == 10, "its single line asks for 10");
    Ok(N($"CountRows(Table(ParseJSON(LookUp(nfReq, RequestNo = \"{REQ}\").History)))") == 4, "original History appended (4 events: submitted, reserved, released, split)");

    Console.WriteLine("== 9. Material Inward");
    Txt("pnIn", P40); Txt("qtyIn", "25"); Sel("typIn", "PO"); Txt("refIn", "4700012345"); Txt("rsnIn", ""); Dt("dtIn", DateTime.Today); Txt("costIn", ""); Txt("locIn", "");
    Do("goIn");
    Ok(N($"LookUp(nfStock, PartNo = \"{P40}\").OnHand") == 25 && S("Last(nfMoves).Type") == "RECEIPT", "PO receipt of 25 -> RECEIPT row, on hand 25");
    Sel("typIn", "SCRAP"); Txt("qtyIn", "5"); Txt("rsnIn", ""); Do("goIn");
    Ok(N($"LookUp(nfStock, PartNo = \"{P40}\").OnHand") == 25, "scrap without a reason is refused");
    Txt("rsnIn", "damaged"); Txt("qtyIn", "500"); Do("goIn");
    Ok(N($"LookUp(nfStock, PartNo = \"{P40}\").OnHand") == 25, "scrapping more than on hand is refused");
    Txt("qtyIn", "5"); Do("goIn");
    Ok(N($"LookUp(nfStock, PartNo = \"{P40}\").OnHand") == 20 && S("Last(nfMoves).RawType") == "SCRAP", "scrap 5 with reason -> SCRAP row, on hand 20");

    Console.WriteLine("== 10. Finance-locked cost formula");
    var cost = h.Ctl["hrsCs"].GetProperty("props").GetProperty("Text").GetString();
    Txt("cktCs", "100"); E("Clear(colCostLines)"); Touch();
    var asm100 = N(P("cvCsV4", "Text").Replace("Text(", "Value(Text(").Replace(", \"#,##0.00\")", ", \"0.00\"))"));
    Txt("cktCs", "200");
    var asm200 = N(P("cvCsV4", "Text").Replace("Text(", "Value(Text(").Replace(", \"#,##0.00\")", ", \"0.00\"))"));
    Ok(Math.Abs(asm100 - 16808.15) < 0.005, $"100 circuits -> assembly 16,808.15 (got {asm100})");
    Ok(Math.Abs(asm200 - 33616.30) < 0.005, $"200 circuits -> assembly 33,616.30 (got {asm200})");
    Ok(S(P("cvCsV6", "Text")) == "₹" + (33616.30 + 200).ToString("#,##0.00", System.Globalization.CultureInfo.InvariantCulture) || S(P("cvCsV6", "Text")).Contains("33,816.30"), "TOTAL = material + assembly + 200 transport (" + S(P("cvCsV6", "Text")) + ")");

    Console.WriteLine("== 11. Invoice number and save");
    var fy = DateTime.Today.Month >= 4 ? DateTime.Today.Year : DateTime.Today.Year - 1;
    var pre = $"IDC EDS/{fy % 100:00}-{(fy + 1) % 100:00}/";
    Ok(S("nfNextInvNo") == pre + "001", "first invoice of the FY is " + pre + "001 (got " + S("nfNextInvNo") + ")");
    Txt("noIv", S("nfNextInvNo")); Sel("stIv", "DRAFT"); Txt("ToNameIv", "Shashank G"); Txt("NoOfCircuitsIv", "100");
    foreach (var f in new[] { "CCNameIv", "FromNameIv", "FromExtIv", "FromMobileIv", "HarnessPartNosIv", "JobDescriptionIv", "BusinessUnitIv", "BUContactIv", "CostCentreIv", "ApplicationDescIv", "DCContactIv", "DCMobileIv", "RefRequestIv", "NotesIv", "DetailsOfRequestIv" }) Txt(f, "x");
    foreach (var f in new[] { "InvoiceDateIv", "JobReceivedIv", "StartDateIv", "CompletionDateIv" }) Dt(f, DateTime.Today);
    E("ClearCollect(colInvLines, {Sr: 1, PartNo: \"A\", Description: \"\", Qty: 2, UnitCost: 50})"); Touch();
    Do("svIv");
    Ok(N("CountRows(nfInv)") == 1 && Math.Abs(N("First(nfInv).TotalCost") - (16808.15 + 100 + 200)) < 0.01, "invoice saved with TotalCost = 16,808.15 + 100 material + 200 transport");
    Ok(S("nfNextInvNo") == pre + "002", "next number moves to " + pre + "002");

    Console.WriteLine("== 12. Brand New Purchase Part");
    E("ClearCollect(colNP, {Id: 1, RequesterName: \"G\", Category: \"Electrical\", SubCategory: \"\", PlantCode: \"5040\", PartName: \"Relay 24V\", MakeBrand: \"\", ModelNo: \"\", OtherSpecs: \"\", Remarks: \"\", UOM: \"NO\", HSNCode: \"\"}, {Id: 2, RequesterName: \"\", Category: \"\", SubCategory: \"\", PlantCode: \"\", PartName: \"\", MakeBrand: \"\", ModelNo: \"\", OtherSpecs: \"\", Remarks: \"\", UOM: \"NO\", HSNCode: \"\"})"); Touch();
    Do("goNp");
    Ok(N("CountRows(nfNewPart)") == 0 && MockNotify.Log.Any(l => l.Contains("missing 8-Digit HSN")), "missing mandatory HSN is refused with the row and column named");
    E("Patch(colNP, First(colNP), {HSNCode: \"85364900\"})"); Touch(); Do("goNp");
    Ok(N("CountRows(nfNewPart)") == 1 && S("First(nfNewPart).RequestNo") == "NPR-" + DateTime.Today.Year + "-00001", "1 row submitted as NPR-YYYY-00001 (blank rows ignored, SAMPLE row ignored)");

    Console.WriteLine("== 13. Procurement stage flow");
    Txt("pfPRNumberPc", "800099999"); Txt("pfSummaryPc", "Relay for test"); Txt("pfDepartmentPc", "EDS");
    foreach (var f in new[] { "pfRaisedByPc", "pfApprovedByPc", "pfPONumberPc", "pfVendorPc", "pfOwnershipPc", "pfPOCopyPathPc", "pfNotesPc" }) Txt(f, "");
    foreach (var f in new[] { "pfQtyPc", "pfPOAmountPc", "pfPRAmountPc" }) Txt(f, "1");
    foreach (var f in new[] { "pfDateRaisedPc", "pfApprovedDatePc", "pfPODatePc", "pfDeliveredDatePc", "pfPOApprovedDatePc" }) Dt(f, DateTime.Today);
    Sel("pfStagePc", "PR RAISED");
    Do("pfGoPc");
    Ok(S("LookUp(nfProc, PRNumber = \"800099999\").Stage") == "PR RAISED", "new PR saved at PR RAISED");
    var row = (RecordValue)E("LookUp(nfProc, PRNumber = \"800099999\")");
    var prm = FormulaValue.NewRecordFromFields(new NamedValue("ThisItem", row));
    Do("pcPcC8", "OnSelect", prm);
    Ok(S("LookUp(nfProc, PRNumber = \"800099999\").Stage") == "APPROVED" && S("LookUp(nfProc, PRNumber = \"800099999\").ApprovedBy") == "Gaurav Shelke", "stage button -> APPROVED, approver recorded");

    Console.WriteLine("== 14. dashboards and lists evaluate");
    foreach (var g in new[] { "rqDshGal", "loDshGal", "stStkGal", "stInvGal", "lgLgGal", "dmDmGal", "rlQuGal", "rlMyGal", "pcPcGal", "shPcGal", "lgPcGal", "bkPuGal", "ptPuGal", "lcGal", "tmGal", "ivIlGal", "npNqGal", "revLgMgr", "prBarsMgr" }) {
      var v = E(P(g, "Items")); Ok(v is TableValue, $"{g}.Items -> {((TableValue)v).Rows.Count()} rows");
    }
    Ok(N("CountRows(" + P("dmDmGal", "Items") + ")") > 0, "High Demand ranks issued parts");
    Ok(S(P("imgPieTest".Length > 0 ? "revPieMgr" : "", "Image")).StartsWith("data:image/svg+xml;utf8,"), "revenue pie renders an SVG data URI");

    Console.WriteLine($"\nworkflow simulation: {Pass} passed, {Fail} failed");
    // Excel recalculates the Settings Data Health formulas after every write; do the same for the previews
    E("Patch(tblSettings, LookUp(tblSettings, Key = \"ExcelMovementRows\"), {Value: Text(CountRows(tblMoves))}); Patch(tblSettings, LookUp(tblSettings, Key = \"ExcelStockTotal\"), {Value: Text(Sum(nfMoves, SQty))})"); Touch();
    // leave a realistic state behind for the screen previews
    Txt("txtBom", S("nfSampleBom")); Do("goBom");
    E($"Set(gReqNo, \"{REQ}\"); Set(gCostReq, \"{REQ}\"); Set(gPrintKind, \"cost\"); Set(gPrintCkt, 100); Set(gInvReq, \"{REQ}\")");
    E($"ClearCollect(colCostLines, ForAll(Filter(nfLines, RequestNo = \"{REQ}\") As L, {{Sr: L.Sr, PartNo: L.PartNo, Description: L.Description, Qty: L.QtyReleased, UnitCost: L.UnitCost}}))");
    Txt("cktCs", "100");
    Touch();
    return Fail;
  }
}
