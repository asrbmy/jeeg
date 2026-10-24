# keywords: ip, address, my ip, public ip, local ip, ip address, hostname
# desc: Show your local and public IP address
# category: network
# network: yes
import socket, urllib.request
print("Hostname :", socket.gethostname())
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(3); s.connect(("8.8.8.8", 80))
    print("Local IP :", s.getsockname()[0]); s.close()
except OSError:
    print("Local IP : unavailable (offline?)")
for url in ("https://api.ipify.org", "https://ifconfig.me/ip"):
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            print("Public IP:", r.read().decode().strip()); break
    except Exception:
        continue
else:
    print("Public IP: unavailable (offline?)")
