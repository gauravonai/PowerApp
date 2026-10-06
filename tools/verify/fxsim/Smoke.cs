// "Click every button": after the workflow simulation, run every behaviour formula (OnSelect, OnChange,
// OnTimerEnd) of every control that is not inside a gallery, in screen order, and report any runtime error.
// Gallery rows are covered by the bind check (types) and by the simulation (the important row buttons).
using Microsoft.PowerFx;
using Microsoft.PowerFx.Types;

public static class Smoke {
  public static int Run(Host h) {
    var bad = 0; var n = 0;
    foreach (var (name, c) in h.Ctl) {
      if (c.GetProperty("gallery").ValueKind == System.Text.Json.JsonValueKind.String) continue;
      foreach (var prop in new[] { "OnSelect", "OnChange", "OnTimerEnd" }) {
        if (!c.GetProperty("props").TryGetProperty(prop, out var f)) continue;
        var expr = f.GetString();
        if (expr == "true" || expr.Contains("Exit(")) continue;
        n++;
        try {
          var st = h.SelfType(c.GetProperty("type").GetString());
          RecordValue prm = null;
          var parent = FormulaValue.NewRecordFromFields(new NamedValue("Width", FormulaValue.New(1000.0)), new NamedValue("Height", FormulaValue.New(500.0)),
            new NamedValue("TemplateWidth", FormulaValue.New(1000.0)), new NamedValue("TemplateHeight", FormulaValue.New(500.0)));
          var fields = new List<NamedValue> { new("ParentX", parent) };
          if (st != null) fields.Add(new NamedValue("SelfX", h.Engine.GetValue(name)));
          var rows = new List<RecordValue> { null };
          if (c.GetProperty("type").GetString().StartsWith("Gallery")) {   // a gallery click needs a row: every nav row, else the first row
            var items = (TableValue)h.Engine.Eval(c.GetProperty("props").GetProperty("Items").GetString(), FormulaValue.NewRecordFromFields(fields), h.Opts);
            rows = items.Rows.Where(x => x.IsValue).Select(x => x.Value).Take(name.StartsWith("navGal") ? 100 : 1).ToList();
          }
          foreach (var row in rows) {
            var f2 = new List<NamedValue>(fields); if (row != null) f2.Add(new NamedValue("ThisItem", row));
            prm = FormulaValue.NewRecordFromFields(f2);
            MockNotify.Log.Clear();
            var r = h.Engine.Eval(expr, prm, h.Opts);
            if (r is ErrorValue ev) { bad++; Console.WriteLine($"  ERROR {c.GetProperty("screen").GetString()}.{name}.{prop}: " + string.Join("; ", ev.Errors.Select(e => e.Message))); }
            else if (MockNotify.Log.Any(l => l.Contains("Saving failed"))) { bad++; Console.WriteLine($"  SAVE FAILED {name}.{prop}: " + MockNotify.Log.First()); }
          }
        } catch (Exception e) { bad++; Console.WriteLine($"  EXCEPTION {c.GetProperty("screen").GetString()}.{name}.{prop}: " + e.Message.Split('\n')[0]); }
      }
    }
    Console.WriteLine($"smoke test: {n} buttons and inputs pressed, {bad} runtime errors");
    return bad;
  }
}
