# keywords: installed programs, installed apps, list programs, what is installed, installed software, list apps, programs installed, is app installed
# desc: List installed programs, or search them (installed programs chrome)
# category: system
# usage: installed programs [name]
# rawargs: yes
import re, shutil
from pathlib import Path
from _lib import args_text, WIN, MAC
from _sys import ps, out
q = re.sub(r"\b(is|installed|my|the|any|programs?|apps?|software|list|show|on|computer|pc|do|i|have)\b", " ", args_text().lower()).strip()
if WIN:
    txt = ps("$k='HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*','HKLM:\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*','HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*';"
             "Get-ItemProperty $k -ErrorAction SilentlyContinue | Where-Object {$_.DisplayName} | ForEach-Object { $_.DisplayName + ' ' + $_.DisplayVersion }", timeout=40)
    rows = sorted({l.strip() for l in txt.splitlines() if l.strip()}, key=str.lower)
elif MAC:
    rows = sorted(p.stem for d in (Path("/Applications"), Path.home() / "Applications") if d.is_dir() for p in d.glob("*.app"))
else:
    if shutil.which("dpkg-query"): txt = out(["dpkg-query", "-W", "-f=${Package} ${Version}\n"], timeout=30)
    elif shutil.which("rpm"): txt = out(["rpm", "-qa"], timeout=30)
    else: txt = ""
    if shutil.which("flatpak"): txt += "\n" + out(["flatpak", "list", "--app", "--columns=name,version"])
    if shutil.which("snap"): txt += "\n" + "\n".join(l.split()[0] + " " + l.split()[1] for l in out(["snap", "list"]).splitlines()[1:] if len(l.split()) > 1)
    rows = sorted({l.strip() for l in txt.splitlines() if l.strip()}, key=str.lower)
if q: rows = [r for r in rows if q in r.lower()]
if not rows: print(f"Nothing found{' for ' + repr(q) if q else ''}.")
else:
    print("\n".join(rows[:80]))
    print(f"{len(rows)} found" + (" (showing 80, add a word to filter)" if len(rows) > 80 else ""))
