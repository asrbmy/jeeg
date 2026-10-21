# keywords: processes, process list, running programs, what is running, tasks running, top, memory hogs
# desc: List the programs using the most memory
# category: system
import re, subprocess
from _lib import WIN, MAC, human
try:
    import psutil
    rows = []
    for p in psutil.process_iter(["pid", "name", "memory_info"]):
        mi = p.info.get("memory_info")
        if mi:
            rows.append((mi.rss, p.info["pid"], p.info["name"] or "?"))
except ImportError:
    rows = []
    if WIN:
        txt = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True, errors="replace").stdout
        for line in txt.splitlines():
            c = [x.strip('"') for x in line.split('","')]
            if len(c) >= 5:
                kb = re.sub(r"[^\d]", "", c[4])
                rows.append((int(kb or 0) * 1024, c[1], c[0]))
    else:
        txt = subprocess.run(["ps", "-Ao", "pid=,rss=,comm="], capture_output=True, text=True, errors="replace").stdout
        for line in txt.splitlines():
            parts = line.split(None, 2)
            if len(parts) == 3 and parts[1].isdigit():
                rows.append((int(parts[1]) * 1024, parts[0], parts[2].split("/")[-1]))
rows.sort(reverse=True)
print(f"{'PID':>7}  {'MEMORY':>9}  NAME")
for mem, pid, name in rows[:15]:
    print(f"{pid:>7}  {human(mem):>9}  {name}")
print(f"({len(rows)} processes in total)")
