// Stand-alone host for the canvas formulas: data tables from the workbook, mock controls,
// mock Studio functions. Used by both the binding check and the workflow simulation.
using System.Text.Json;
using Microsoft.PowerFx;
using Microsoft.PowerFx.Types;

public class MockNav : ReflectionFunction {
  public static List<string> Log = new();
  public MockNav() : base("MockNav", FormulaType.Boolean, FormulaType.String, FormulaType.String) {}
  public BooleanValue Execute(StringValue s, StringValue t) { Log.Add(s.Value); return FormulaValue.New(true); }
}
public class MockNotify : ReflectionFunction {
  public static List<string> Log = new();
  public MockNotify() : base("MockNotify", FormulaType.Boolean, FormulaType.String, FormulaType.String) {}
  public BooleanValue Execute(StringValue s, StringValue t) { Log.Add(t.Value + ": " + s.Value); return FormulaValue.New(true); }
}
public class MockCreateFile : ReflectionFunction {
  static RecordType RT = RecordType.Empty().Add("Path", FormulaType.String);
  public MockCreateFile() : base("MockCreateFile", RT, FormulaType.String, FormulaType.String, FormulaType.String) {}
  public RecordValue Execute(StringValue a, StringValue b, StringValue c) =>
    FormulaValue.NewRecordFromFields(new NamedValue("Path", FormulaValue.New(a.Value + "/" + b.Value)));
}
public class MockMeta : ReflectionFunction {
  static RecordType RT = RecordType.Empty().Add("Path", FormulaType.String).Add("Name", FormulaType.String);
  public MockMeta() : base("MockMeta", RT, FormulaType.String) {}
  public RecordValue Execute(StringValue a) =>
    FormulaValue.NewRecordFromFields(new NamedValue("Path", FormulaValue.New(a.Value)), new NamedValue("Name", FormulaValue.New("x")));
}
public class MockGetFile : ReflectionFunction {
  public MockGetFile() : base("MockGetFile", FormulaType.String, FormulaType.String) {}
  public StringValue Execute(StringValue a) => FormulaValue.New("blob:" + a.Value);
}

public class Host {
  public RecalcEngine Engine;
  public ParserOptions Opts = new ParserOptions { AllowsSideEffects = true, NumberIsFloat = true, MaxExpressionLength = 200000 };
  public JsonElement App;
  public Dictionary<string, FormulaType> CtlTypes = new();
  public Dictionary<string, RecordType> TableTypes = new();
  public Dictionary<string, JsonElement> Ctl = new();
  public List<string> NamedErrors = new();

  public static RecordType Rec(params (string, FormulaType)[] f) { var r = RecordType.Empty(); foreach (var (n, t) in f) r = r.Add(n, t); return r; }

  public Host(string dataJson, string bindJson, string userEmail = null) {
    var config = new PowerFxConfig(Features.PowerFxV1) { MaximumExpressionLength = 200000 };
    config.EnableSetFunction(); config.SymbolTable.EnableMutationFunctions();
    config.EnableJsonFunctions(); config.EnableParseJSONFunction();
    config.AddFunction(new MockNav()); config.AddFunction(new MockNotify());
    config.AddFunction(new MockCreateFile()); config.AddFunction(new MockGetFile()); config.AddFunction(new MockMeta());
    Engine = new RecalcEngine(config);
    App = JsonDocument.Parse(File.ReadAllText(bindJson)).RootElement;

    // ---- data tables, typed like the Excel connector
    var data = JsonDocument.Parse(File.ReadAllText(dataJson)).RootElement;
    foreach (var t in data.EnumerateObject()) {
      var rt = RecordType.Empty();
      foreach (var c in t.Value.GetProperty("types").EnumerateObject())
        rt = rt.Add(c.Name, c.Value.GetString() == "n" ? FormulaType.Number : c.Value.GetString() == "d" ? FormulaType.DateTime : FormulaType.String);
      TableTypes[t.Name] = rt;
      var rows = new List<RecordValue>();
      foreach (var r in t.Value.GetProperty("rows").EnumerateArray()) {
        var fields = new List<NamedValue>();
        foreach (var f in rt.FieldNames) {
          var ft = rt.GetFieldType(f);
          if (!r.TryGetProperty(f, out var v)) { fields.Add(new NamedValue(f, FormulaValue.NewBlank(ft))); continue; }
          FormulaValue fv = ft == FormulaType.Number ? FormulaValue.New(v.GetDouble())
                          : ft == FormulaType.DateTime ? FormulaValue.New(DateTime.Parse(v.GetString()))
                          : FormulaValue.New(v.GetString());
          fields.Add(new NamedValue(f, fv));
        }
        rows.Add(FormulaValue.NewRecordFromFields(rt, fields));
      }
      Engine.UpdateVariable(t.Name, FormulaValue.NewTable(rt, rows));
    }
    // ---- host enums (as text) and screens (as text, so screen names are still checked)
    foreach (var e in App.GetProperty("enums").EnumerateObject()) {
      var fields = e.Value.EnumerateArray().Select(m => new NamedValue(m.GetString(), FormulaValue.New(e.Name + "." + m.GetString())));
      Engine.UpdateVariable(e.Name, FormulaValue.NewRecordFromFields(fields));
    }
    foreach (var s in App.GetProperty("screens").EnumerateArray()) Engine.UpdateVariable(s.GetString(), FormulaValue.New(s.GetString()));

    // ---- global variables and collections exactly as App.OnStart creates them
    void V(string n, FormulaValue v) => Engine.UpdateVariable(n, v);
    foreach (var n in new[] { "gRole", "gReqNo", "gInvReq", "gInvEdit", "gCostReq", "gPrintKind", "gBomText", "gEditPr", "gEditPurch", "gPanel", "gVendorPick", "gEditPurchReq", "gSyncNote", "gPhotoCheck", "gRoleHome", "gMeName", "gMeEmail", "gMeInitials", "gLoginMode", "gLoginMsg", "gTempCode" }) V(n, FormulaValue.New(""));
    V("gBusy", FormulaValue.New(false)); V("gPrinting", FormulaValue.New(false));
    V("gShortSr", FormulaValue.New(-1.0)); V("gPrintCkt", FormulaValue.New(200.0));
    var N = FormulaType.Number; var S = FormulaType.String; var B = FormulaType.Boolean;
    V("gLastSync", FormulaValue.New(DateTime.Now));
    foreach (var n in new[] { "gIsLead", "gIsAdmin", "gIsMgr" }) V(n, FormulaValue.New(false));
    V("gLoginTries", FormulaValue.New(0.0));
    V("gRoleOptions", FormulaValue.NewTable(Rec(("Value", S)), FormulaValue.NewRecordFromFields(new NamedValue("Value", FormulaValue.New("Engineer")))));
    var usersT = TableTypes[TableTypes.Keys.First(k => k == "tblUsers" || k.StartsWith("tblUsers_"))];
    V("gMe", Blankish(usersT)); V("gPend", Blankish(usersT));
    V("colBom", FormulaValue.NewTable(Rec(("Sr", N), ("PartNo", S), ("PN", S), ("Qty", N), ("Description", S), ("UOM", S), ("Location", S), ("OnHand", N), ("Reserved", N), ("Avail", N), ("UnitCost", N), ("Short", N), ("Status", S), ("Found", B))));
    V("colNP", FormulaValue.NewTable(Rec(("Id", N), ("RequesterName", S), ("Category", S), ("SubCategory", S), ("PlantCode", S), ("PartName", S), ("MakeBrand", S), ("ModelNo", S), ("OtherSpecs", S), ("Remarks", S), ("UOM", S), ("HSNCode", S))));
    var npT = Rec(("Id", N), ("RequesterName", S), ("Category", S), ("SubCategory", S), ("PlantCode", S), ("PartName", S), ("MakeBrand", S), ("ModelNo", S), ("OtherSpecs", S), ("Remarks", S), ("UOM", S), ("HSNCode", S));
    V("gNpForm", Blankish(npT));
    V("colInvLines", FormulaValue.NewTable(Rec(("Sr", N), ("PartNo", S), ("Description", S), ("Qty", N), ("UnitCost", N))));
    V("colCostLines", FormulaValue.NewTable(Rec(("Sr", N), ("PartNo", S), ("Description", S), ("Qty", N), ("UnitCost", N))));
    V("colShots", FormulaValue.NewTable(Rec(("Name", S), ("Img", S))));

    // ---- named formulas (App.Formulas)
    foreach (var nf in App.GetProperty("named").EnumerateArray()) {
      var nm = nf.GetProperty("name").GetString();
      var chk = Engine.Check(nf.GetProperty("expr").GetString(), RecordType.Empty(), new ParserOptions { NumberIsFloat = true, MaxExpressionLength = 200000 });
      if (!chk.IsSuccess) { NamedErrors.Add(nm + ": " + string.Join(" | ", chk.Errors.Where(e => !e.IsWarning).Select(e => e.Message).Distinct().Take(3))); continue; }
      Engine.SetFormula(nm, nf.GetProperty("expr").GetString(), (n, v) => { }, new ParserOptions { NumberIsFloat = true, MaxExpressionLength = 200000 });
    }

    foreach (var c in App.GetProperty("controls").EnumerateArray()) Ctl[c.GetProperty("name").GetString()] = c;
  }

  public FormulaType SelfType(string ctype) {
    var S = FormulaType.String;
    if (ctype.EndsWith("TextInput")) return Rec(("Text", S));
    if (ctype.EndsWith("DropDown")) return Rec(("Selected", Rec(("Value", S))));
    if (ctype.EndsWith("DatePicker")) return Rec(("SelectedDate", FormulaType.Date));
    if (ctype == "AddMedia") return Rec(("Media", S));
    if (ctype == "Timer") return Rec(("Value", FormulaType.Number));
    if (ctype == "Label") return Rec(("Text", S));
    return null;
  }

  // controls are mocked as global records: TextInput.Text, DropDown.Selected.Value, DatePicker.SelectedDate, Gallery.AllItems
  public void MockControls(Func<string, RecordType> galleryItemType) {
    foreach (var (name, c) in Ctl) {
      var ct = c.GetProperty("type").GetString();
      var st = SelfType(ct);
      if (st != null) { Engine.UpdateVariable(name, Blankish((RecordType)st)); CtlTypes[name] = st; }
    }
    foreach (var (name, c) in Ctl) {
      if (!c.GetProperty("type").GetString().StartsWith("Gallery")) continue;
      var it = galleryItemType(name);
      if (it == null) continue;
      foreach (var (cn, cc) in Ctl)   // child inputs become columns of AllItems, like in Power Apps
        if (cc.GetProperty("gallery").ValueKind == JsonValueKind.String && cc.GetProperty("gallery").GetString() == name && CtlTypes.TryGetValue(cn, out var ctt))
          it = it.Add(cn, ctt);
      var gt = Rec(("AllItems", it.ToTable()), ("Selected", it));
      Engine.UpdateVariable(name, FormulaValue.NewRecordFromFields(gt, new NamedValue("AllItems", FormulaValue.NewTable(it)), new NamedValue("Selected", FormulaValue.NewBlank(it))));
      CtlTypes[name] = gt;
    }
  }
  public static RecordValue Blankish(RecordType t) {
    var fields = new List<NamedValue>();
    foreach (var f in t.FieldNames) {
      var ft = t.GetFieldType(f);
      fields.Add(new NamedValue(f, ft is RecordType r ? Blankish(r) : ft == FormulaType.String ? FormulaValue.New("") : FormulaValue.NewBlank(ft)));
    }
    return FormulaValue.NewRecordFromFields(t, fields);
  }

  public RecordType ParamType(string control, RecordType itemType) {
    var c = Ctl[control];
    var N = FormulaType.Number;
    var p = RecordType.Empty().Add("ParentX", Rec(("Width", N), ("Height", N), ("TemplateWidth", N), ("TemplateHeight", N)));
    var st = SelfType(c.GetProperty("type").GetString());
    if (st != null) p = p.Add("SelfX", st);
    if (itemType != null) p = p.Add("ThisItem", itemType);
    return p;
  }

  public FormulaValue Run(string expr, RecordValue param = null) {
    var r = Engine.Eval(expr, param, Opts);
    if (r is ErrorValue ev) throw new Exception(string.Join("; ", ev.Errors.Select(e => e.Message)));
    return r;
  }
  public void SetCtl(string name, string field, FormulaValue v) {
    var t = (RecordType)CtlTypes[name];
    var cur = (RecordValue)Engine.GetValue(name);
    var fields = t.FieldNames.Select(f => new NamedValue(f, f == field ? v : cur.GetField(f))).ToList();
    Engine.UpdateVariable(name, FormulaValue.NewRecordFromFields(t, fields));
  }
}
