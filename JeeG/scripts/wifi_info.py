# keywords: wifi, wi-fi, ssid, wireless, signal, wifi name, which wifi, network name
# desc: Show the Wi-Fi network you are connected to
# category: network
import re, subprocess
from _lib import WIN, MAC, fail
from _sys import out
if WIN:
    t = out(["netsh", "wlan", "show", "interfaces"])
    keep = [l.strip() for l in t.splitlines() if re.match(r"\s*(SSID|State|Signal|Radio type|Receive rate|Transmit rate)\b", l)]
elif MAC:
    t = out(["networksetup", "-getairportnetwork", "en0"]) or out(["networksetup", "-getairportnetwork", "en1"])
    keep = [t] if t else []
else:
    t = out(["nmcli", "-t", "-f", "active,ssid,signal,rate", "dev", "wifi"])
    keep = []
    for l in t.splitlines():
        p = l.split(":")
        if p[0] == "yes":
            keep.append(f"SSID: {p[1]}   Signal: {p[2]}%   Rate: {p[3]}")
print("\n".join(keep) if keep else "Not connected to Wi-Fi (or Wi-Fi details are unavailable).")
