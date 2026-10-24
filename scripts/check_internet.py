# keywords: internet, connection, online, connected, offline, network, wifi working, net
# desc: Check whether the internet is working
# category: network
# network: yes
import socket, time
from _lib import fail
for host, port in (("1.1.1.1", 443), ("8.8.8.8", 53), ("9.9.9.9", 53)):
    try:
        t = time.perf_counter()
        socket.create_connection((host, port), timeout=3).close()
        print(f"Internet is working ({(time.perf_counter() - t) * 1000:.0f} ms to {host}).")
        break
    except OSError:
        continue
else:
    try:
        socket.gethostbyname("example.com")
        print("Network is up but outbound connections are blocked.")
    except OSError:
        fail("No internet connection.")
