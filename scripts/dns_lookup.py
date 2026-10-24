# keywords: dns, lookup, resolve, domain, nslookup, ip of, ip address of website
# desc: Look up the IP addresses of a domain
# category: network
# network: yes
# usage: dns lookup <domain>
import socket
from _lib import args_text, fail
from _sys import valid_host
d = (args_text() or "").split()
if not d or not valid_host(d[0]):
    fail("Give a domain, e.g. dns lookup openai.com")
try:
    infos = socket.getaddrinfo(d[0], None)
except socket.gaierror as e:
    fail(f"Could not resolve {d[0]}: {e}")
ips = sorted({i[4][0] for i in infos}, key=lambda x: (":" in x, x))
print(f"{d[0]}:")
for ip in ips:
    print("  ", ip)
