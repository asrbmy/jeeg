# keywords: restart, reboot, reset, restart pc, restart computer
# desc: Restart the computer (30 second delay, can be cancelled)
# category: power
# confirm: yes
import subprocess
from _lib import WIN, MAC, fail
if WIN:
    rc = subprocess.call(["shutdown", "/r", "/t", "30"]); note = "Cancel with: cancel shutdown"
elif MAC:
    rc = subprocess.call(["osascript", "-e", 'tell application "System Events" to restart']); note = ""
else:
    rc = subprocess.call(["shutdown", "-r", "+1"]) and subprocess.call(["systemctl", "reboot"]); note = "Cancel with: cancel shutdown"
if rc:
    fail("Could not start the restart (administrator rights may be needed).")
print("Restarting shortly. " + note)
