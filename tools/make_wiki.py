#!/usr/bin/env python3
"""Build the generated wiki pages from the real task list and by really running JeeG:

    wiki/Task-Catalog.md                       every task by category
    wiki/Reference-*.md                        every task in detail (usage, flags, wording, script file)
    wiki/Tutorial-Your-First-Hour.md           }
    wiki/Recipes-and-Workflows.md              } text from tools/wiki_content.py, output captured by running JeeG
    wiki/Examples-Gallery.md                   }

    python tools/make_wiki.py            (about a minute; runs the demo phrases in temporary home folders)
    python tools/make_wiki.py --quick    (only the task catalog and reference pages, no demo runs)

The other wiki pages are written by hand.
"""
import json, os, re, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
sys.path.insert(0, str(ROOT / "tools"))
import wiki_content, wiki_run

esc = lambda x: (x or "").replace("|", "\\|")


def tasks():
    tmp = ROOT / ".wiki_tmp"
    out = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "--list-json"], capture_output=True, text=True, check=True, env={**os.environ, "JEEG_HOME": str(tmp)}).stdout
    shutil.rmtree(tmp, ignore_errors=True)
    return json.loads(out)


def header(name):
    """The header lines of a task script: dict of key -> text."""
    for p in sorted((ROOT / "scripts").glob(name + ".*")):
        if p.suffix.lower() in {".py", ".sh", ".bat", ".cmd", ".ps1", ".js"}:
            h = {}
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines()[:16]:
                m = re.match(r"^\s*(?:#|//|REM|::)\s*([a-z]+):\s*(.*)$", line, re.I)
                if m:
                    h[m.group(1).lower()] = m.group(2).strip()
            h["file"] = "scripts/" + p.name
            return h
    return {}


def catalog(ts):
    cats = {}
    for t in ts:
        cats.setdefault(t["category"], []).append(t)
    L = ["# Task Catalog", "",
         f"Every task in JeeG, by category ({len(ts)} tasks). Generated from the real task list; do not edit by hand (`python tools/make_wiki.py`).", "",
         "In **Usage**, `<...>` is something you fill in and `[...]` is optional. A star `*` means the task asks before running; *online* means it can use the internet. "
         "For more detail on each task (flags, other wording that finds it, script file) see the reference pages: " +
         ", ".join(f"[{g[1]}]({g[0]})" for g in wiki_content.GROUPS) + ". In the terminal, `list <category>` shows the same, and `explain <words>` shows how a phrase would be matched.", "",
         "## Categories", ""]
    L.append(" | ".join(f"[{c} ({len(cats[c])})](#{c.lower().replace('_', '-')})" for c in sorted(cats)))
    for c in sorted(cats):
        L += ["", f"## {c}", "", "| Task | Usage | What it does |", "|---|---|---|"]
        for t in sorted(cats[c], key=lambda x: x["name"]):
            name = t["name"].replace("_", " ") + (" *(online)*" if t["online"] else "") + (" \\*" if t["confirm"] else "")
            L.append(f"| {name} | " + (f"`{esc(t['usage'])}`" if t["usage"] else "") + f" | {esc(t['description'])} |")
    L += ["", "Back to [Home](Home)."]
    (WIKI / "Task-Catalog.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def reference(ts):
    bycat = {}
    for t in ts:
        bycat.setdefault(t["category"], []).append(t)
    used = set()
    for page, title, intro, cats in wiki_content.GROUPS:
        used.update(cats)
        n = sum(len(bycat.get(c, [])) for c in cats)
        L = [f"# Reference: {title}", "", intro, "",
             f"{n} tasks. Each entry shows the **usage** (`<x>` you fill in, `[x]` optional), what the task does, how it behaves, other words that also find it, and the script file you can read or edit. "
             "Say the task name, or the usage with your words filled in. `explain <words>` shows how any phrase is matched; `<task> preview` or `--dry-run` shows what would happen without doing it.", ""]
        L.append("Categories on this page: " + ", ".join(f"[{c}](#{c.replace('_', '-')})" for c in cats if c in bycat))
        for c in cats:
            if c not in bycat:
                continue
            L += ["", f"## {c.replace('_', '-')}", ""]
            for t in sorted(bycat[c], key=lambda x: x["name"]):
                h = header(t["name"])
                flags = []
                if t["confirm"]:
                    flags.append("asks before running")
                if t["online"]:
                    flags.append("can use the internet")
                if h.get("private", "").lower() in {"yes", "true"}:
                    flags.append("never saved in history")
                if h.get("stdin"):
                    flags.append("reads piped text")
                L.append(f"### {t['name'].replace('_', ' ')}")
                L.append("")
                if t["usage"]:
                    L.append("**Usage:** `" + t["usage"].replace("`", "'") + "`  ")
                L.append(f"**What it does:** {t['description']}  ")
                if flags:
                    L.append("**Behaviour:** " + "; ".join(flags) + ".  ")
                kw = [k.strip() for k in h.get("keywords", "").split(",") if k.strip()]
                kw = [k for k in kw if k.lower() != t["name"].replace("_", " ")][:10]
                if kw:
                    L.append("**Also found by:** " + ", ".join(f"`{k}`" for k in kw) + "  ")
                if h.get("rawargs"):
                    L.append("**Your words:** " + ("passed through untouched" if h["rawargs"] == "yes" else "the whole sentence is passed (quotes kept)") + "  ")
                L.append(f"**Script:** `{h.get('file', 'scripts/' + t['name'] + '.py')}`")
                L.append("")
        L += ["", "Back to [Home](Home) | [Task Catalog](Task-Catalog)."]
        (WIKI / f"{page}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    left = sorted(set(bycat) - used)
    if left:
        print("WARNING: categories not on any reference page:", left)


def show(step, lines, rc):
    out = []
    for l in lines:
        out.append(l)
    if len(out) > 26:
        out = out[:25] + [f"... ({len(lines) - 25} more lines)"]
    body = f"task> {step}\n" + "\n".join(out)
    if rc not in (0,):
        body += f"\n[exit code {rc}]"
    return body


def narrative(version):
    date = time.strftime("%d %B %Y")
    for page, (title, blocks) in wiki_content.PAGES.items():
        L = [f"# {title}", ""]
        for b in blocks:
            if isinstance(b, str):
                L.append(b.replace("{version}", version).replace("{date}", date))
            else:
                _, key = b
                res = wiki_run.run(wiki_content.SC[key])
                L.append("```text")
                L.append("\n\n".join(show(*r) for r in res))
                L.append("```")
                L.append("")
        L += ["", "Back to [Home](Home)."]
        (WIKI / f"{page}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        print("wrote", page)


def main() -> int:
    ts = tasks()
    version = re.search(r'__version__\s*=\s*"([^"]+)"', (ROOT / "jeeg.py").read_text()).group(1)
    catalog(ts)
    reference(ts)
    print(f"Wrote catalog and reference pages for {len(ts)} tasks")
    if "--quick" not in sys.argv:
        narrative(version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
