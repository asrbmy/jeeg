# keywords: shutdown, shut down, power off, turn off, switch off, switch off pc, off
# desc: Shut the computer down (30 second delay, can be cancelled)
# category: power
# confirm: yes
import subprocess
from _lib import WIN, MAC, fail
if WIN:
    rc = subprocess.call(["shutdown", "/s", "/t", "30"])
    note = "Cancel with: cancel shutdown"
elif MAC:
    rc = subprocess.call(["osascript", "-e", 'tell application "System Events" to shut down'])
    note = ""
else:
    rc = subprocess.call(["shutdown", "-h", "+1"]) and subprocess.call(["systemctl", "poweroff"])
    note = "Cancel with: cancel shutdown"
if rc:
    fail("Could not start the shutdown (administrator rights may be needed).")
print("Shutting down shortly. " + note)
