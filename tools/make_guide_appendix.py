#!/usr/bin/env python3
"""Rewrite the task table at the end of USER_GUIDE.md ("15. Appendix: every task") from the real task list.

    python tools/make_guide_appendix.py
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDE = ROOT / "USER_GUIDE.md"
MARK = "## 15. Appendix: every task"
TAIL = "![JeeG in the terminal]"


def main() -> int:
    out = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "--list-json"], capture_output=True, text=True, check=True,
                         env={**__import__("os").environ, "JEEG_HOME": str(ROOT / ".guide_tmp")}).stdout
    tasks = json.loads(out)
    text = GUIDE.read_text(encoding="utf-8")
    head, _, rest = text.partition(MARK)
    tail = ""                                  # the appendix is the last part of the guide
    lines = [MARK, "",
             f"{len(tasks)} tasks. In the Usage column, `<...>` is something you fill in and `[...]` is optional. "
             "A star means the task asks before running; \"online\" means it can use the internet.", ""]
    cats = {}
    for t in tasks:
        cats.setdefault(t["category"], []).append(t)
    for c in sorted(cats):
        lines += ["", f"### {c}", "", "| Task | Usage | What it does |", "|---|---|---|"]
        for t in sorted(cats[c], key=lambda x: x["name"]):
            name = t["name"].replace("_", " ") + (" (online)" if t["online"] else "") + (" *" if t["confirm"] else "")
            esc = lambda x: x.replace("|", "\\|")
            usage = "`" + esc(t["usage"]) + "`" if t["usage"] else ""
            lines.append("| " + name + " | " + usage + " | " + esc(t["description"]) + " |")
    GUIDE.write_text(head + "\n".join(lines) + "\n\n" + tail, encoding="utf-8")
    import shutil
    shutil.rmtree(ROOT / ".guide_tmp", ignore_errors=True)
    print(f"Wrote {len(tasks)} tasks into {GUIDE.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
