# keywords: network doctor, why is my internet slow, internet not working, wifi not working, diagnose network, fix my internet, network problem, no internet, wifi slow
# desc: Find out why the internet is slow or down: checks your network, router, name lookup and the internet, then says what to try
# category: network
# network: yes
# usage: network doctor
# patterns: \bnetwork\s+(?:doctor|diagnos\w*|problem|troubleshoot\w*)\b ;; \bwhy\s+is\s+(?:my\s+|the\s+)?(?:internet|wi-?fi|net|network)\s+(?:so\s+)?(?:slow|down|not\s+working|broken|bad)\b ;; \b(?:my\s+)?(?:internet|wi-?fi)\s+(?:is\s+)?(?:slow|not\s+working|isn'?t\s+working|down|broken)\b ;; \b(?:diagnose|fix|troubleshoot)\s+(?:my\s+)?(?:internet|wi-?fi|network)\b
# priority: 4
import socket, sys, time
from _lib import WIN
from _netdoc import default_gateway, diagnose, local_ip, run_text


def tcp_ms(host, port, timeout=4):
    t = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return (time.perf_counter() - t) * 1000
    except OSError:
        return None


print("Network doctor")
r = {"local_ip": local_ip()}
print(f"  1. This computer      {r['local_ip'] or 'no network address'}")
gw = default_gateway() if r["local_ip"] else None
if gw:
    out = run_text(["ping", "-n" if WIN else "-c", "2", "-w" if WIN else "-W", "2000" if WIN else "2", gw], timeout=10)
    r["gateway_ok"] = ("TTL=" in out.upper()) if WIN else (" 0% packet loss" in out or "1 received" in out or "2 received" in out)
    print(f"  2. Router {gw:<15} {'answers' if r['gateway_ok'] else 'does not answer'}")
else:
    r["gateway_ok"] = None
    print("  2. Router              (could not find it; skipping)")
t = time.perf_counter()
try:
    socket.getaddrinfo("example.com", 443)
    r["dns_ok"], r["dns_ms"] = True, (time.perf_counter() - t) * 1000
except OSError:
    r["dns_ok"], r["dns_ms"] = False, None
print(f"  3. Name lookup         {'%.0f ms' % r['dns_ms'] if r['dns_ok'] else 'failed'}")
ms = [m for m in (tcp_ms("1.1.1.1", 443), tcp_ms("8.8.8.8", 443)) if m is not None]
r["internet_ok"], r["internet_ms"] = bool(ms), min(ms) if ms else None
print(f"  4. Internet (by IP)    {'%.0f ms' % r['internet_ms'] if ms else 'unreachable'}")
head, tips = diagnose(r)
print("\n" + head)
for t_ in tips:
    print("  - " + t_)
sys.exit(0 if r["internet_ok"] else 1)
