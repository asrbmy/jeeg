# keywords: show desktop, minimize all, minimise all, hide windows, clear screen windows, desktop
# desc: Minimise everything and show the desktop
# category: hardware
import shutil, subprocess
from _lib import WIN, MAC, fail
if WIN:
    from _sys import press_key
    press_key(0x44, hold=(0x5B,))
elif MAC:
    subprocess.run(["osascript", "-e", 'tell application "System Events" to key code 103'])
elif shutil.which("xdotool"):
    subprocess.run(["xdotool", "key", "super+d"])
else:
    fail("Install 'xdotool' to use this on Linux.")
