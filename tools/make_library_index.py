#!/usr/bin/env python3
"""Rebuild library/index.json (name, description, tags, SHA-256 of each plugin). Run after changing a plugin:
    python tools/make_library_index.py
"""
import hashlib
import json
import re
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "library"
plugins = {}
for f in sorted(LIB.glob("*.py")):
    meta = {}
    for line in f.read_text(encoding="utf-8").splitlines()[:15]:
        m = re.match(r"^\s*#\s*(\w+)\s*:\s*(.*?)\s*$", line)
        if m:
            meta[m.group(1).lower()] = m.group(2)
    assert meta.get("keywords") and meta.get("desc"), f"{f.name} needs keywords and desc"
    plugins[f.stem] = {"desc": meta["desc"], "tags": meta.get("category", ""), "sha256": hashlib.sha256(f.read_bytes()).hexdigest()}
(LIB / "index.json").write_text(json.dumps({"version": 1, "plugins": plugins}, indent=1) + "\n", encoding="utf-8")
print(f"Wrote {LIB / 'index.json'} with {len(plugins)} plugin(s).")
