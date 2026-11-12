# keywords: who is on my wifi, devices on my network, scan network, network devices, connected devices, find devices, who is connected to my wifi, lan scan
# desc: List the devices on your home network (who is on my wifi). Add "scan" to wake the quiet ones first. Only your own private network.
# category: network
# network: yes
# usage: who is on my wifi [scan]
# rawargs: full
# patterns: \bwho\s+is\s+(?:on|connected\s+to)\s+(?:my\s+|the\s+)?(?:wi-?fi|network|lan|router)\b ;; \b(?:devices|computers|phones)\s+(?:on|connected\s+to)\s+(?:my\s+|the\s+)?(?:wi-?fi|network|lan)\b ;; \b(?:scan|list)\s+(?:my\s+|the\s+)?(?:local\s+|home\s+)?(?:network|lan)\b
# priority: 4
import socket, sys, threading
from _lib import args_text, fail
from _netdoc import local_ip, neighbour_table, parse_neighbours, subnet_hosts

me = local_ip()
if not me:
    fail("This computer is not on a network.")
scan = "scan" in args_text().lower().split()
if scan:
    hosts = subnet_hosts(me)
    if not hosts:
        fail("I only scan private home or office networks (like 192.168.x.x).")
    print(f"Scanning {len(hosts)} addresses next to {me} (private network only)...")

    def poke(h):
        for port in (80, 443, 22, 445, 53):
            try:
                socket.create_connection((h, port), timeout=0.3).close()
                return
            except OSError:
                continue
    todo, lock = list(hosts), threading.Lock()

    def worker():
        while True:
            with lock:
                if not todo:
                    return
                h = todo.pop()
            poke(h)
    ts = [threading.Thread(target=worker, daemon=True) for _ in range(64)]
    for t in ts:
        t.start()
    for t in ts:
        t.join(60)
rows = parse_neighbours(neighbour_table())
if not rows:
    print("No other devices found yet. Try:  who is on my wifi scan")
    sys.exit(0)
names = {}


def look(ip):
    try:
        names[ip] = socket.gethostbyaddr(ip)[0]
    except OSError:
        names[ip] = ""


ths = [threading.Thread(target=look, args=(ip,), daemon=True) for ip, _ in rows]
for t in ths:
    t.start()
for t in ths:
    t.join(2)
print(f"{len(rows)} device(s) seen from {me}:")
for ip, mac in rows:
    print(f"  {ip:<16} {mac}  {names.get(ip, '')}")
print("A device you do not recognise? Change the Wi-Fi password in your router.")
