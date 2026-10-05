// Lays out the generated controls the way canvas apps do (manual X/Y, auto-layout stacks, galleries)
// and evaluates every visible property with the Power Fx engine, then writes a JSON draw list per screen.
// A Python script turns that into HTML for screenshots. This is a PREVIEW, not Power Apps itself.
using System.Text.Json;
using Microsoft.PowerFx;
using Microsoft.PowerFx.Types;

public static class Render {
  static Host H; static List<Dictionary<string, object>> Out;
  static Dictionary<string, RecordType> ItemTypes = new();
  static Dictionary<string, List<JsonElement>> Kids = new();

  static FormulaValue Ev(string expr, RecordValue p) {
    try { var r = H.Engine.Eval(expr, p, H.Opts); return r; } catch { return FormulaValue.NewBlank(); }
  }
  static string Str(FormulaValue v) => v switch {
    StringValue s => s.Value, NumberValue n => n.Value.ToString("0.##########", System.Globalization.CultureInfo.InvariantCulture),
    DecimalValue d => d.Value.ToString(), BooleanValue b => b.Value ? "true" : "false",
    DateValue d => d.GetConvertedValue(TimeZoneInfo.Local).ToString("dd-MMM-yyyy"), DateTimeValue dt => dt.GetConvertedValue(TimeZoneInfo.Local).ToString("dd-MMM-yyyy HH:mm"),
    _ => "" };
  static double Num(FormulaValue v, double d = 0) => v is NumberValue n ? n.Value : v is DecimalValue dd ? (double)dd.Value : d;
  static string Col(FormulaValue v) {
    if (v is ColorValue c) { var x = c.Value; return $"rgba({x.R},{x.G},{x.B},{(x.A / 255.0).ToString("0.###", System.Globalization.CultureInfo.InvariantCulture)})"; }
    return null;
  }
  static string P(JsonElement c, string prop) => c.GetProperty("props").TryGetProperty(prop, out var v) ? v.GetString() : null;

  static RecordValue Param(double pw, double ph, RecordValue item, double tw = 0, double th = 0) {
    var N = FormulaType.Number;
    var parent = FormulaValue.NewRecordFromFields(new NamedValue("Width", FormulaValue.New(pw)), new NamedValue("Height", FormulaValue.New(ph)),
      new NamedValue("TemplateWidth", FormulaValue.New(tw > 0 ? tw : pw)), new NamedValue("TemplateHeight", FormulaValue.New(th > 0 ? th : ph)));
    var f = new List<NamedValue> { new("ParentX", parent) };
    if (item != null) f.Add(new NamedValue("ThisItem", item));
    return FormulaValue.NewRecordFromFields(f);
  }

  static double Prop(JsonElement c, string p, RecordValue prm, double d) { var e = P(c, p); return e == null ? d : Num(Ev(e, prm), d); }
  static bool Vis(JsonElement c, RecordValue prm) { var e = P(c, "Visible"); if (e == null) return true; var v = Ev(e, prm); return v is not BooleanValue b || b.Value; }

  static void Emit(string kind, JsonElement c, double x, double y, double w, double h, RecordValue prm, Dictionary<string, object> extra = null) {
    var d = new Dictionary<string, object> { ["k"] = kind, ["n"] = c.GetProperty("name").GetString(), ["x"] = x, ["y"] = y, ["w"] = w, ["h"] = h };
    foreach (var p in new[] { "Fill", "Color", "BorderColor" }) { var e = P(c, p); if (e != null) d[p] = Col(Ev(e, prm)); }
    foreach (var p in new[] { "Text", "HintText", "Default", "Size", "FontWeight", "Align", "VerticalAlign", "Font", "BorderThickness", "Icon", "Image", "HtmlText", "PaddingLeft", "Wrap", "DefaultDate", "Mode" }) {
      var e = P(c, p); if (e != null) d[p] = Str(Ev(e, prm));
    }
    if (kind == "dropdown") { var it = P(c, "Items"); var def = P(c, "Default"); d["Text"] = def != null ? Str(Ev(def, prm)) : Str(Ev("First(" + it + ").Value", prm)); }
    if (extra != null) foreach (var kv in extra) d[kv.Key] = kv.Value;
    Out.Add(d);
  }

  static void Draw(JsonElement c, double ox, double oy, double pw, double ph, RecordValue item, double tw, double th, double? fx = null, double? fy = null, double? fw = null, double? fh = null) {
    var prm = Param(pw, ph, item, tw, th);
    if (!Vis(c, prm)) return;
    var t = c.GetProperty("type").GetString();
    double x = fx ?? Prop(c, "X", prm, 0), y = fy ?? Prop(c, "Y", prm, 0);
    double w = fw ?? Prop(c, "Width", prm, 100), h = fh ?? Prop(c, "Height", prm, 40);
    double ax = ox + x, ay = oy + y;
    var name = c.GetProperty("name").GetString();
    var kids = Kids.GetValueOrDefault(name) ?? new();
    if (t.StartsWith("GroupContainer")) {
      Emit("box", c, ax, ay, w, h, prm);
      var dir = P(c, "LayoutDirection");
      if (dir == null) { foreach (var k in kids) Draw(k, ax, ay, w, h, item, tw, th); return; }
      var cp = Param(w, h, item);
      double pad = Prop(c, "PaddingTop", cp, 0), gap = Prop(c, "LayoutGap", cp, 0);
      var vis = kids.Where(k => Vis(k, Param(w, h, item))).ToList();
      if (dir.Contains("Vertical")) {
        double cy = pad;
        foreach (var k in vis) { var kh = Prop(k, "Height", Param(w, h, item), 40); Draw(k, ax, ay, w, h, item, tw, th, pad, cy, w - 2 * pad, kh); cy += kh + gap; }
        if (cy > h) Out.Add(new() { ["k"] = "grow", ["y"] = ay + cy + pad, ["h0"] = ay + h });
      } else {
        double tot = vis.Sum(k => Prop(k, "FillPortions", Param(w, h, item), 1));
        double cx = pad, avail = w - 2 * pad - gap * Math.Max(0, vis.Count - 1);
        foreach (var k in vis) { var kw = avail * Prop(k, "FillPortions", Param(w, h, item), 1) / Math.Max(1, tot); Draw(k, ax, ay, w, h, item, tw, th, cx, pad, kw, h - 2 * pad); cx += kw + gap; }
      }
      return;
    }
    if (t.StartsWith("Gallery")) {
      Emit("box", c, ax, ay, w, h, prm);
      var rows = Ev(P(c, "Items"), prm) as TableValue;
      double ts = Prop(c, "TemplateSize", prm, 40); int wrap = (int)Prop(c, "WrapCount", prm, 1);
      double cw = (w - 12) / Math.Max(1, wrap);
      int i = 0;
      if (rows != null) foreach (var r in rows.Rows) {
        if (!r.IsValue) continue;
        double ry = ay + (i / wrap) * ts, rx = ax + (i % wrap) * cw;
        if (ry + ts > ay + h + 0.5) break;
        foreach (var k in kids) Draw(k, rx, ry, cw, ts, r.Value, cw, ts);
        i++;
      }
      return;
    }
    string kind = t switch {
      var s when s.StartsWith("Label") => "label", var s when s.EndsWith("Button") => "button", var s when s.EndsWith("TextInput") => "input",
      var s when s.EndsWith("DropDown") => "dropdown", var s when s.EndsWith("DatePicker") => "date", var s when s.StartsWith("Rectangle") => "rect",
      var s when s.StartsWith("Image") => "image", var s when s.EndsWith("Icon@2.5.0") => "icon", "HtmlViewer" => "html", "AddMedia" => "media", _ => "other" };
    if (kind == "other") return;
    Emit(kind, c, ax, ay, w, h, prm);
  }

  public static int RunAfterSim(Host h, string outDir) {
    H = h;
    var roots = new Dictionary<string, JsonElement>();
    foreach (var c in h.App.GetProperty("controls").EnumerateArray()) {
      var n = c.GetProperty("name").GetString();
      // parent link = previous controls listed; rebuild tree from 'parent' field
      var par = c.TryGetProperty("parent", out var pp) && pp.ValueKind == JsonValueKind.String ? pp.GetString() : null;
      if (par == null) roots[c.GetProperty("screen").GetString()] = c; else { if (!Kids.ContainsKey(par)) Kids[par] = new(); Kids[par].Add(c); }
    }
    Directory.CreateDirectory(outDir);
    // galleries: AllItems = their current Items, so "empty" labels behave like in Power Apps
    foreach (var (name, c) in h.Ctl) {
      if (!c.GetProperty("type").GetString().StartsWith("Gallery") || c.GetProperty("gallery").ValueKind == JsonValueKind.String) continue;
      if (!h.CtlTypes.TryGetValue(name, out var gtt)) continue;
      var gt = (RecordType)gtt; var allT = (TableType)gt.GetFieldType("AllItems");
      var items = Ev(c.GetProperty("props").GetProperty("Items").GetString(), Param(1000, 500, null)) as TableValue;
      if (items == null) continue;
      var recs = new List<RecordValue>();
      foreach (var row in items.Rows) {
        if (!row.IsValue) continue;
        var rt = allT.ToRecord();
        recs.Add(FormulaValue.NewRecordFromFields(rt, rt.FieldNames.Select(f => new NamedValue(f,
          row.Value.Type.FieldNames.Contains(f) ? row.Value.GetField(f) : (FormulaValue)(rt.GetFieldType(f) is RecordType rr ? Host.Blankish(rr) : FormulaValue.NewBlank(rt.GetFieldType(f)))))));
      }
      h.Engine.UpdateVariable(name, FormulaValue.NewRecordFromFields(gt, new NamedValue("AllItems", FormulaValue.NewTable(allT.ToRecord(), recs)), new NamedValue("Selected", FormulaValue.NewBlank(gt.GetFieldType("Selected")))));
    }
    foreach (var (scr, root) in roots) {
      Out = new();
      Draw(root, 0, 0, 1366, 768, null, 0, 0);
      File.WriteAllText(Path.Combine(outDir, scr + ".json"), JsonSerializer.Serialize(Out));
    }
    Console.WriteLine($"rendered {roots.Count} screens to {outDir}");
    return 0;
  }
}
