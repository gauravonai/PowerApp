using System.Text.Json;
using Microsoft.PowerFx;
using Microsoft.PowerFx.Types;

var mode = args[0];
var host = new Host(args[1], args[2]);
if (mode == "bind") return Bind.Run(host);
if (mode == "sim") return Sim.Run(host);
if (mode == "smoke") { Sim.Run(host); return Smoke.Run(host); }
if (mode == "render") { var f = Sim.Run(host); return Render.RunAfterSim(host, args[3]); }
return 2;

static class Bind {
  static readonly string[] NumProps = { "X", "Y", "Width", "Height", "Size", "TemplateSize", "BorderThickness", "PaddingLeft", "PaddingRight", "PaddingTop", "PaddingBottom", "RadiusTopLeft", "RadiusTopRight", "RadiusBottomLeft", "RadiusBottomRight", "Duration", "WrapCount", "LayoutGap", "FillPortions", "LayoutMinHeight", "LayoutMinWidth", "TemplatePadding", "MaxLength", "StartYear", "EndYear" };
  static readonly string[] BoolProps = { "Visible", "ShowScrollbar", "Wrap", "IsEditable", "Start", "AutoStart", "Repeat" };
  static bool IsColorProp(string p) => p == "Fill" || p == "Color" || p.EndsWith("Color") || p.EndsWith("Fill") || p == "ChevronBackground" || p == "ChevronHoverBackground" || p == "IconBackground";
  static readonly string[] Behaviour = { "OnSelect", "OnChange", "OnTimerEnd" };

  public static int Run(Host h) {
    var itemTypes = new Dictionary<string, RecordType>();
    int bad = 0, n = 0;
    var errs = new List<string>(h.NamedErrors.Select(e => "App.Formulas." + e));
    bad += h.NamedErrors.Count;
    h.MockControls(g => {
      var items = h.Ctl[g].GetProperty("props").GetProperty("Items").GetString();
      var cr = h.Engine.Check(items, h.ParamType(g, null), h.Opts);
      if (!cr.IsSuccess) { errs.Add($"{g}.Items: " + string.Join(" | ", cr.Errors.Where(e => !e.IsWarning).Select(e => e.Message))); return null; }
      if (cr.ReturnType is not TableType tt) { errs.Add($"{g}.Items: not a table ({cr.ReturnType})"); return null; }
      itemTypes[g] = tt.ToRecord(); return tt.ToRecord();
    });
    // OnStart and StartScreen
    foreach (var (id, expr) in new[] { ("App.OnStart", h.App.GetProperty("onstart").GetString()), ("App.StartScreen", h.App.GetProperty("startscreen").GetString()) }) {
      n++; var cr = h.Engine.Check(expr, RecordType.Empty(), h.Opts);
      if (!cr.IsSuccess) { bad++; errs.Add(id + ": " + string.Join(" | ", cr.Errors.Where(e => !e.IsWarning).Select(e => e.Message))); }
    }
    foreach (var (name, c) in h.Ctl) {
      var gal = c.GetProperty("gallery").ValueKind == JsonValueKind.String ? c.GetProperty("gallery").GetString() : null;
      RecordType it = null;
      RecordType ownItem = null;
      if (c.GetProperty("type").GetString().StartsWith("Gallery")) itemTypes.TryGetValue(name, out ownItem);
      if (gal != null && !itemTypes.TryGetValue(gal, out it)) { errs.Add($"{name}: gallery {gal} has no item type"); bad++; continue; }
      var pt = h.ParamType(name, it);
      var ptOwn = ownItem != null ? h.ParamType(name, ownItem) : pt;
      foreach (var p in c.GetProperty("props").EnumerateObject()) {
        n++;
        var expr = p.Value.GetString();
        var cr = h.Engine.Check(expr, (p.Name == "OnSelect" || p.Name == "TemplateFill") ? ptOwn : pt, h.Opts);
        var hard = cr.Errors.Where(e => !e.IsWarning).ToList();
        if (hard.Count > 0) { bad++; errs.Add($"{c.GetProperty("screen").GetString()}.{name}.{p.Name}: " + string.Join(" | ", hard.Select(e => e.Message).Distinct().Take(3))); continue; }
        var rt = cr.ReturnType;
        string want = null;
        if (NumProps.Contains(p.Name) && rt != FormulaType.Number) want = "Number";
        else if (BoolProps.Contains(p.Name) && rt != FormulaType.Boolean) want = "Boolean";
        else if (IsColorProp(p.Name) && rt != FormulaType.Color) want = "Color";
        else if (p.Name == "Items" && rt is not TableType) want = "Table";
        else if ((p.Name == "Text" || p.Name == "HintText" || p.Name == "Tooltip" || p.Name == "HtmlText" || p.Name == "Font") && rt != FormulaType.String && rt != FormulaType.Number) want = "Text";
        else if (p.Name == "DefaultDate" && rt != FormulaType.Date && rt != FormulaType.DateTime && rt != FormulaType.Blank) want = "Date";
        if (want != null) { bad++; errs.Add($"{c.GetProperty("screen").GetString()}.{name}.{p.Name}: returns {rt} but {want} is needed"); }
      }
    }
    foreach (var e in errs.Take(80)) Console.WriteLine(e);
    Console.WriteLine($"binding check: {n} property formulas, {bad} errors ({itemTypes.Count} galleries typed)");
    return bad;
  }
}
