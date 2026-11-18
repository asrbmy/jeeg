#!/usr/bin/env python3
"""Write wiki/Task-Catalog.md (every task by category) from the real task list, so it cannot go stale.

    python tools/make_wiki.py
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "wiki" / "Task-Catalog.md"


def main() -> int:
    tmp = ROOT / ".wiki_tmp"
    out = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "--list-json"], capture_output=True, text=True, check=True,
                         env={**os.environ, "JEEG_HOME": str(tmp)}).stdout
    shutil.rmtree(tmp, ignore_errors=True)
    tasks = json.loads(out)
    cats = {}
    for t in tasks:
        cats.setdefault(t["category"], []).append(t)
    esc = lambda x: (x or "").replace("|", "\\|")
    L = ["# Task Catalog", "",
         f"Every task in JeeG, by category ({len(tasks)} tasks). Generated from the real task list; do not edit by hand (`python tools/make_wiki.py`).", "",
         "In **Usage**, `<...>` is something you fill in and `[...]` is optional. A star `*` means the task asks before running; *online* means it can use the internet. "
         "In the terminal, `list <category>` shows the same, and `explain <words>` shows how a phrase would be matched.", "",
         "## Categories", ""]
    L.append(" | ".join(f"[{c} ({len(cats[c])})](#{c.lower().replace('_', '-')})" for c in sorted(cats)))
    L.append("")
    for c in sorted(cats):
        L += ["", f"## {c}", "", "| Task | Usage | What it does |", "|---|---|---|"]
        for t in sorted(cats[c], key=lambda x: x["name"]):
            name = t["name"].replace("_", " ") + (" *(online)*" if t["online"] else "") + (" \\*" if t["confirm"] else "")
            L.append(f"| {name} | " + (f"`{esc(t['usage'])}`" if t["usage"] else "") + f" | {esc(t['description'])} |")
    L += ["", "Back to [Home](Home)."]
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"Wrote {len(tasks)} tasks into {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
