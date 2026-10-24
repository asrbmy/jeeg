# keywords: ping, latency, reachable, ping test, response time, is up
# desc: Ping a host (ping google.com)
# category: network
# network: yes
# usage: ping host <name or ip>
import subprocess
from _lib import WIN, args_text, call, fail
from _sys import valid_host
host = (args_text() or "8.8.8.8").split()[0]
if not valid_host(host):
    fail("That does not look like a valid host name or IP address.")
raise SystemExit(call(["ping", "-n" if WIN else "-c", "4", host]))
