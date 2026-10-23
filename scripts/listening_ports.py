# keywords: listening ports, open ports, ports in use, listening, netstat, which ports, active ports, show ports
# desc: Show which programs are listening on network ports
# category: network
import shutil
from _lib import WIN, MAC
from _sys import out
if WIN:
    t = out(["netstat", "-ano", "-p", "tcp"], timeout=20)
    rows = [l.split() for l in t.splitlines() if "LISTENING" in l]
    print(f"{'Local address':<26}PID")
    for r in sorted(rows, key=lambda r: r[1])[:60]: print(f"{r[1]:<26}{r[-1]}")
elif MAC:
    print(out(["lsof", "-iTCP", "-sTCP:LISTEN", "-nP"], timeout=20) or "None found.")
elif shutil.which("ss"):
    print(out(["ss", "-tlnp"]) or "None found.")
else:
    print("Needs 'ss' (iproute2) or netstat.")
