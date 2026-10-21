# keywords: port owner, who uses port, what is using port, which program uses port, port in use, what is on port, process on port, what is running on port
# desc: Which program is using a port (who uses port 3000)
# category: network
# usage: who uses port <number>
# rawargs: yes
# patterns: \b(who|what|which)\b.*\bport\b ;; \bport (owner|in use)\b ;; \bprocess (on|using) port\b
import re, shutil
from _lib import args_text, fail, WIN, MAC
from _sys import out
m = re.search(r"\b(\d{1,5})\b", args_text())
if not m or not 1 <= int(m.group(1)) <= 65535: fail("Usage: who uses port <1-65535>     e.g. who uses port 3000")
port = m.group(1)
if WIN:
    rows = [l.split() for l in out(["netstat", "-ano"], timeout=20).splitlines() if re.search(r":" + port + r"\s", l)]
    seen = set()
    for r in rows:
        pid = r[-1]
        if pid in seen or not pid.isdigit(): continue
        seen.add(pid)
        name = out(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"]).split(",")[0].strip('"')
        print(f"port {port}: PID {pid} {name}")
    if not seen: print(f"Nothing is using port {port}.")
elif shutil.which("lsof"):
    t = out(["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN"])
    print(t or f"Nothing is listening on port {port}.")
elif shutil.which("ss"):
    t = out(["ss", "-ltnp", f"sport = :{port}"])
    print(t if len(t.splitlines()) > 1 else f"Nothing is listening on port {port}.")
else:
    fail("Needs lsof or ss (Linux/macOS) to look this up.")
