#!/usr/bin/env python3
"""After a release: write the version and file hashes into the Scoop and winget files.
    python tools/fill_packaging.py 2.15.0
Reads jeeg-windows-x64.exe.sha256 from the GitHub release (needs internet). Nothing else is sent."""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if len(sys.argv) != 2 or not re.fullmatch(r"\d+\.\d+\.\d+", sys.argv[1]):
    sys.exit("Usage: python tools/fill_packaging.py 2.15.0")
v = sys.argv[1]
url = f"https://github.com/asrbmy/jeeg/releases/download/v{v}/jeeg-windows-x64.exe.sha256"
try:
    with urllib.request.urlopen(url, timeout=30) as r:
        sha = r.read().decode().split()[0].lower()
except Exception as ex:
    sys.exit(f"Could not read {url}: {ex}. Is the release finished and the build-exe workflow done?")
if not re.fullmatch(r"[0-9a-f]{64}", sha):
    sys.exit("That file did not contain a SHA-256 hash.")
scoop = ROOT / "packaging" / "scoop" / "jeeg.json"
d = json.loads(scoop.read_text(encoding="utf-8"))
d["version"] = v
d["url"] = f"https://github.com/asrbmy/jeeg/releases/download/v{v}/jeeg-windows-x64.exe#/jeeg.exe"
d["hash"] = sha
scoop.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
out = ROOT / "packaging" / "winget" / "out"
out.mkdir(exist_ok=True)
for f in (ROOT / "packaging" / "winget").glob("*.yaml"):
    (out / f.name).write_text(f.read_text(encoding="utf-8").replace("__VERSION__", v).replace("__SHA256_WINDOWS__", sha.upper()), encoding="utf-8")
print(f"Scoop file updated. winget files for {v} are in {out}. Copy them to manifests/a/asrbmy/JeeG/{v}/ in your winget-pkgs fork.")
