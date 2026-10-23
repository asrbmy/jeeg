# keywords: kill port, free port, port in use, stop server, address already in use, close port, stop process on port
# desc: Stop whatever is listening on a port (kill port 3000)
# category: developer
# usage: kill port <number>
# confirm: yes
import re, subprocess
from _lib import WIN, args_text, fail
m = re.search(r"\d{2,5}", args_text())
if not m or not 1 <= int(m.group()) <= 65535:
    fail("Usage: kill port <number>")
port = m.group()
pids = set()
if WIN:
    t = subprocess.run(["netstat", "-ano", "-p", "tcp"], capture_output=True, text=True, errors="replace").stdout
    for l in t.splitlines():
        p = l.split()
        if len(p) >= 5 and p[3] == "LISTENING" and p[1].endswith(":" + port):
            pids.add(p[4])
else:
    try:
        t = subprocess.run(["lsof", "-ti", f"tcp:{port}", "-sTCP:LISTEN"], capture_output=True, text=True).stdout
    except FileNotFoundError:
        fail("'lsof' is not installed.")
    pids = set(t.split())
pids.discard("0")
if not pids:
    fail(f"Nothing is listening on port {port}.")
for pid in sorted(pids):
    rc = subprocess.call(["taskkill", "/PID", pid, "/F"] if WIN else ["kill", pid])
    print(f"{'Stopped' if rc == 0 else 'Could not stop'} process {pid} on port {port}.")
