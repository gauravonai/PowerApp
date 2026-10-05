"""
Pack app/Src/*.pa.yaml into app/EDS-Lab-Portal.msapp with Microsoft's Power Platform CLI.

    python3 tools/make_msapp.py

How it works
  * `pac canvas pack --layout SourceCode` builds an .msapp from two things: a ".msapr" reference file
    (the non-source parts of an app: header, app properties, theme list, control templates) and the
    Src/*.pa.yaml source. It marks the result "LoadFromYaml", so Power Apps Studio rebuilds every
    screen from the YAML when the file is opened.
  * The .msapr comes from Microsoft's own test app (PowerApps-Tooling, MIT licence,
    src/Persistence.Tests/_TestData/AlmApps/AlmTestApp-asManyEntitiesAsPossible.msapp, saved by
    Power Apps Studio in Feb 2026, DocVersion 1.348). This script strips everything that app
    carried (its screen, component, images, Dataverse table) and renames it, keeping only the shell.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import uuid
import zipfile
import base64

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASE = os.path.join(HERE, "msapp-base", "AlmTestApp.msapr")
STAGE = os.path.join(HERE, "out", "pack")
OUT = os.path.join(ROOT, "app", "EDS-Lab-Portal.msapp")
NAME = "EDS-Lab-Portal"

DROP_PREFIX = ("msapp/Controls/4.json", "msapp/Components/", "msapp/Assets/", "msapp/AppCheckerResult.sarif")


def clean(name, data):
    if name == "msapp/Properties.json":
        p = json.loads(data)
        p.update({"Name": base64.b64encode((NAME + ".msapp").encode()).decode().rstrip("="),
                  "Id": str(uuid.uuid5(uuid.NAMESPACE_URL, "jcb-eds-lab-portal")),
                  "FileID": str(uuid.uuid5(uuid.NAMESPACE_URL, "jcb-eds-lab-portal-file")),
                  "LocalConnectionReferences": "{}", "LocalDatabaseReferences": "",
                  "AppDescription": "JCB EDS Lab Material Portal - stock, requests, release, invoices, PR/PO.",
                  "DefaultConnectedDataSourceMaxGetRowsCount": 2000, "ControlCount": {},
                  "ParserErrorCount": 0, "BindingErrorCount": 0, "Author": ""})
        return json.dumps(p, indent=2).encode()
    if name == "msapp/Controls/1.json":
        c = json.loads(data)
        for r in c["TopParent"]["Rules"]:
            if r["Property"] == "Theme":
                r["InvariantScript"] = "PowerAppsTheme"
        return json.dumps(c).encode()
    if name == "msapp/ComponentsMetadata.json":
        return json.dumps({"Components": []}, indent=2).encode()
    if name == "msapp/References/DataSources.json":
        return json.dumps({"DataSources": []}, indent=2).encode()
    if name == "msapp/References/Resources.json":
        return json.dumps({"Resources": []}, indent=2).encode()
    if name == "msapp/References/QualifiedValues.json":
        return json.dumps({"QualifiedValues": []}, indent=2).encode()
    if name == "msapp/References/ModernThemes.json":
        return json.dumps({"Themes": [{"EntityName": "PowerAppsTheme", "ThemeName": "PowerAppsTheme"}]}, indent=2).encode()
    if name == "msapp/References/Templates.json":
        t = json.loads(data)
        t["ComponentTemplates"] = []
        t["PcfTemplates"] = []
        return json.dumps(t).encode()
    if name == "msapp/Resources/PublishInfo.json":
        p = json.loads(data)
        p.update({"AppName": "JCB EDS Lab Material Portal", "BackgroundColor": "RGBA(242,176,30,1)",
                  "IconColor": "RGBA(21,22,26,1)", "IconName": "Settings", "UserLocale": "en-IN"})
        return json.dumps(p).encode()
    return data


def main():
    pac = shutil.which("pac") or os.path.expanduser("~/.dotnet/tools/pac")
    if os.path.isdir(STAGE):
        shutil.rmtree(STAGE)
    os.makedirs(STAGE)
    msapr = os.path.join(STAGE, NAME + ".msapr")
    with zipfile.ZipFile(BASE) as zin, zipfile.ZipFile(msapr, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            if info.filename.startswith(DROP_PREFIX):
                continue
            zout.writestr(info.filename, clean(info.filename, zin.read(info.filename)))
    shutil.copytree(os.path.join(ROOT, "app", "Src"), os.path.join(STAGE, "Src"))
    r = subprocess.run([pac, "canvas", "pack", "--sources", STAGE, "--msapp", OUT, "--layout", "SourceCode",
                        "--overwrite"], capture_output=True, text=True)
    print(r.stdout[-1200:], r.stderr[-1200:])
    if r.returncode != 0 or not os.path.exists(OUT):
        sys.exit("pack failed")
    with zipfile.ZipFile(OUT) as z:
        names = z.namelist()
        packed = json.loads(z.read("packed.json"))
    print("entries:", len(names), "| packed.json LoadFromYaml =", packed["LoadConfiguration"]["LoadFromYaml"])
    print("size: %.0f KB" % (os.path.getsize(OUT) / 1024))


if __name__ == "__main__":
    main()
