# keywords: flush dns, clear dns, dns cache, reset dns, dns problem
# desc: Clear the DNS cache
# category: network
# confirm: yes
import subprocess
from _lib import WIN, MAC, fail
if WIN:
    rc = subprocess.call(["ipconfig", "/flushdns"])
elif MAC:
    rc = subprocess.call(["sudo", "dscacheutil", "-flushcache"]) or subprocess.call(["sudo", "killall", "-HUP", "mDNSResponder"])
else:
    rc = subprocess.call(["resolvectl", "flush-caches"])
if rc:
    fail("Could not flush the DNS cache (administrator rights may be needed).")
print("DNS cache cleared.")
