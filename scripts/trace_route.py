# keywords: traceroute, tracert, route, hops, path to, trace
# desc: Trace the network route to a host
# category: network
# network: yes
# usage: trace route <host>
import subprocess
from _lib import WIN, args_text, call, fail
from _sys import valid_host
h = (args_text() or "").split()
if not h or not valid_host(h[0]):
    fail("Give a host, e.g. trace route google.com")
raise SystemExit(call(["tracert", "-d", "-h", "20", h[0]] if WIN else ["traceroute", "-n", "-m", "20", h[0]]))
