# keywords: cancel shutdown, abort shutdown, stop shutdown, cancel restart, cancel reboot, abort, undo shutdown
# desc: Cancel a pending shutdown or restart
# category: power
# priority: 1
import subprocess
from _lib import WIN, MAC, fail
if MAC:
    fail("On macOS, cancel from the shutdown dialog or run: sudo killall shutdown")
rc = subprocess.call(["shutdown", "/a"] if WIN else ["shutdown", "-c"])
if rc:
    fail("No shutdown was pending (or it could not be cancelled).")
print("Pending shutdown cancelled.")
