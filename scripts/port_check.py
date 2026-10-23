# keywords: port, open port, tcp, listening, reachable port, connect
# desc: Check if a port is open (port check example.com 443)
# category: network
# usage: port check <host> <port>
import re, socket, time
from _lib import args_text, fail
from _sys import valid_host
p = args_text().split()
nums = [x for x in p if x.isdigit()]
hosts = [x for x in p if not x.isdigit() and valid_host(x) and x.lower() not in ("on", "at", "of")]
if not nums or not hosts or not 1 <= int(nums[0]) <= 65535:
    fail("Usage: port check <host> <port>   e.g. port check example.com 443")
h, port = hosts[0], int(nums[0])
t = time.perf_counter()
try:
    socket.create_connection((h, port), timeout=4).close()
    print(f"{h}:{port} is OPEN ({(time.perf_counter() - t) * 1000:.0f} ms)")
except OSError as e:
    fail(f"{h}:{port} is closed or unreachable ({e.__class__.__name__}).")
