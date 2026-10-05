using Microsoft.PowerFx.Functions;
using Microsoft.PowerFx;
using Microsoft.PowerFx.Types;
using System.Text.Json;

var mode = args[0];
var config = new PowerFxConfig(Features.PowerFxV1);
config.EnableSetFunction(); config.SymbolTable.EnableMutationFunctions(); config.EnableJsonFunctions(); config.EnableParseJSONFunction();

var engine = new RecalcEngine(config);
var opts = new ParserOptions { AllowsSideEffects = true, NumberIsFloat = true };

if (mode == "eval") {
  // each block separated by a line "----"
  var text = File.ReadAllText(args[1]);
  int fail = 0;
  foreach (var raw in text.Split("\n----\n")) {
    var expr = raw.Trim(); if (expr.Length == 0 || expr.StartsWith("//")) continue;
    if (expr.StartsWith("SET ")) { // SET name = expr
      var eq = expr.IndexOf('='); var name = expr.Substring(4, eq-4).Trim();
      var v = engine.Eval(expr.Substring(eq+1), null, opts); engine.UpdateVariable(name, v); Console.WriteLine($"[set] {name}"); continue; }
    try {
      var r = engine.Eval(expr, null, opts);
      string s = r is ErrorValue ev ? "ERROR: " + string.Join("; ", ev.Errors.Select(e=>e.Message)) : Show(r);
      Console.WriteLine($"{Short(expr)}\n   => {s}");
    } catch (Exception e) { fail++; Console.WriteLine($"{Short(expr)}\n   !! {e.Message.Split('\n')[0]}"); }
  }
  return fail;
}
if (mode == "parse") {
  // input: JSON array of {id, f}
  var items = JsonSerializer.Deserialize<List<Dictionary<string,string>>>(File.ReadAllText(args[1]))!;
  int bad = 0;
  foreach (var it in items) {
    var res = Engine.Parse(it["f"], options: new ParserOptions { AllowsSideEffects = true });
    if (!res.IsSuccess) { bad++; Console.WriteLine($"{it["id"]}: " + string.Join(" | ", res.Errors.Select(e => e.Message + " @" + e.Span?.Min))); }
  }
  Console.WriteLine($"parsed {items.Count} formulas, {bad} with syntax errors");
  return bad;
}
return 2;

static string Short(string s) { s = s.Replace("\n"," "); return s.Length > 110 ? s.Substring(0,110)+"…" : s; }
static string Show(FormulaValue v) {
  switch (v) {
    case BlankValue: return "Blank";
    case StringValue sv: return "\"" + sv.Value + "\"";
    case NumberValue nv: return nv.Value.ToString("R");
    case DecimalValue dv: return dv.Value.ToString();
    case BooleanValue bv: return bv.Value.ToString();
    case DateValue d: return d.GetConvertedValue(TimeZoneInfo.Utc).ToString("yyyy-MM-dd");
    case DateTimeValue dt: return dt.GetConvertedValue(TimeZoneInfo.Utc).ToString("yyyy-MM-dd HH:mm");
    case RecordValue rv: return "{" + string.Join(", ", rv.Fields.Select(f => f.Name + ":" + Show(f.Value))) + "}";
    case TableValue tv: return "[" + string.Join(", ", tv.Rows.Take(12).Select(r => r.IsValue ? Show(r.Value) : "err")) + (tv.Rows.Count() > 12 ? ", …" : "") + "]";
    case ErrorValue ev: return "ERROR " + string.Join(";", ev.Errors.Select(e=>e.Message));
    default: return v.ToString() ?? "?";
  }
}
