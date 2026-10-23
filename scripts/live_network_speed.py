# keywords: live network speed, network usage, bandwidth, download speed now, current speed, data usage now, upload speed now, network monitor, internet usage
# desc: Watch your current download/upload speed for a few seconds (live network speed)
# category: network
# usage: live network speed [seconds]
# rawargs: yes
import re, shutil, time
from _lib import args_text, WIN, MAC
from _sys import ps, out
m = re.search(r"(\d+)", args_text())
secs = max(2, min(int(m.group(1)), 60)) if m else 5
def counters():
    try:
        import psutil
        c = psutil.net_io_counters(); return c.bytes_recv, c.bytes_sent
    except ImportError: pass
    if WIN:
        v = ps("$a=Get-NetAdapterStatistics; ($a|Measure-Object ReceivedBytes -Sum).Sum; ($a|Measure-Object SentBytes -Sum).Sum").split()
        return (int(v[0]), int(v[1])) if len(v) >= 2 else None
    if MAC:
        lines = out(["netstat", "-ib"]).splitlines()
        if not lines: return None
        h = lines[0].split(); ib, ob = h.index("Ibytes"), h.index("Obytes"); r = s = 0; seen = set()
        for l in lines[1:]:
            f = l.split()
            if len(f) > ob and f[0] not in seen and not f[0].startswith("lo") and "Link" in f[2]:
                seen.add(f[0]); r += int(f[ib]); s += int(f[ob])
        return r, s
    try:
        r = s = 0
        for l in open("/proc/net/dev").read().splitlines()[2:]:
            name, _, rest = l.partition(":")
            if name.strip() == "lo": continue
            f = rest.split(); r += int(f[0]); s += int(f[8])
        return r, s
    except (OSError, ValueError, IndexError): return None
def rate(b): return f"{b * 8 / 1e6:6.2f} Mbit/s  ({b / 1048576:5.2f} MB/s)"
a = counters()
if not a: print("Could not read network counters (try: pip install psutil)."); raise SystemExit(1)
print(f"Measuring for {secs} seconds (Ctrl+C to stop)...")
try:
    for _ in range(secs):
        time.sleep(1); b = counters()
        print(f"  down {rate(b[0] - a[0])}   up {rate(b[1] - a[1])}"); a = b
except KeyboardInterrupt:
    pass
