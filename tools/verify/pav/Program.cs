using Microsoft.PowerPlatform.PowerApps.Persistence.PaYaml.Serialization;
using Microsoft.PowerPlatform.PowerApps.Persistence.PaYaml.Models;
using Microsoft.PowerPlatform.PowerApps.Persistence.PaYaml.Models.SchemaV3;
int bad = 0, n = 0;
foreach (var f in Directory.GetFiles(args[0], "*.pa.yaml")) {
  n++;
  try { var m = PaYamlSerializer.Deserialize<PaModule>(File.ReadAllText(f));
        var again = PaYamlSerializer.Serialize(m); // round trip through Microsoft's own writer
        if (m == null) throw new Exception("null module");
  } catch (Exception e) { bad++; Console.WriteLine(Path.GetFileName(f) + ": " + e.Message.Split('\n')[0]); }
}
foreach (var f in Directory.GetFiles(args[1], "*.yaml")) {
  n++;
  try { var seq = PaYamlSerializer.Deserialize<NamedObjectSequence<ControlInstance>>(File.ReadAllText(f));
        if (seq == null || seq.Count != 1) throw new Exception("expected exactly one root control");
  } catch (Exception e) { bad++; Console.WriteLine(Path.GetFileName(f) + ": " + e.Message.Split('\n')[0]); }
}
Console.WriteLine($"Microsoft PaYamlSerializer: {n} files, {bad} failed");
return bad;
