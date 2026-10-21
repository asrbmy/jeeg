# keywords: startup programs, startup apps, autostart, what starts at boot, boot programs, login items, programs on startup, startup items
# desc: List programs that start with your computer
# category: system
import glob, os
from pathlib import Path
from _lib import WIN, MAC
from _sys import ps
if WIN:
    out = ps("Get-CimInstance Win32_StartupCommand | ForEach-Object { $_.Name + '  ->  ' + $_.Command }")
    print(out or "Could not read the startup list (try Task Manager > Startup).")
elif MAC:
    rows = []
    for d in (Path.home() / "Library/LaunchAgents", Path("/Library/LaunchAgents"), Path("/Library/LaunchDaemons")):
        rows += [f"{p.name}   ({d})" for p in sorted(d.glob("*.plist"))] if d.is_dir() else []
    print("\n".join(rows) or "Nothing found. Also check System Settings > General > Login Items.")
else:
    rows = []
    for d in (Path.home() / ".config/autostart", Path("/etc/xdg/autostart")):
        for p in sorted(d.glob("*.desktop")) if d.is_dir() else []:
            name = p.stem
            try:
                for line in p.read_text(errors="ignore").splitlines():
                    if line.startswith("Name=") : name = line[5:]; break
            except OSError: pass
            rows.append(f"{name}   ({p})")
    print("\n".join(rows) or "No autostart entries found.")
