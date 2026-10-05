"""Validate app/Src against Microsoft's pa.yaml v3 JSON schema and check paste files are single-control sequences."""
import glob
import sys

import jsonschema
import yaml

schema = yaml.safe_load(open(sys.argv[1]))
schema["definitions"]["ControlTypeId-1P-controls-enum"] = True   # what Microsoft's published schema build does
v = jsonschema.Draft7Validator(schema)
bad = 0
files = sorted(glob.glob("app/Src/*.pa.yaml"))
for f in files:
    errs = list(v.iter_errors(yaml.safe_load(open(f))))
    if errs:
        bad += 1
        print(f, errs[0].message[:300])
for f in sorted(glob.glob("paste/*.yaml")):
    d = yaml.safe_load(open(f))
    assert isinstance(d, list) and len(d) == 1, f
print("schema: %d files, %d with errors; paste files OK" % (len(files), bad))
sys.exit(bad)
