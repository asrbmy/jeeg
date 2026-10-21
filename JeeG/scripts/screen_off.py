# keywords: screen off, turn off screen, turn off display, monitor off, display off, blank screen, switch off monitor
# desc: Turn the screen off without sleeping
# category: system
import shutil, subprocess
from _lib import WIN, MAC, fail
if WIN:
    import ctypes
    ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, 2)
elif MAC:
    subprocess.run(["pmset", "displaysleepnow"])
elif shutil.which("xset"):
    subprocess.run(["xset", "dpms", "force", "off"])
else:
    fail("Needs 'xset' (X11) to turn the display off.")
print("Screen off - move the mouse to wake it.")
