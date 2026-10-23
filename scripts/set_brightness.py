# keywords: brightness, dim, brighten, screen brightness, dimmer, brighter, display brightness
# desc: Set screen brightness (set brightness 60)
# category: hardware
# usage: set brightness <0-100>
import re, shutil, subprocess
from _lib import WIN, MAC, args_text, fail
from _sys import ps
m = re.search(r"\d+", args_text())
if not m:
    fail("Give a level 0-100, e.g. set brightness 60")
n = max(0, min(100, int(m.group())))
if WIN:
    ps("(Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods).WmiSetBrightness(1, [int]$env:TR_N)", n=n)
    print(f"Brightness set to {n}% (works on laptop screens).")
elif MAC:
    if not shutil.which("brightness"):
        fail("macOS needs the 'brightness' tool:  brew install brightness")
    subprocess.run(["brightness", str(n / 100)]); print(f"Brightness set to {n}%.")
elif shutil.which("brightnessctl"):
    subprocess.run(["brightnessctl", "set", f"{n}%"])
elif shutil.which("xbacklight"):
    subprocess.run(["xbacklight", "-set", str(n)])
else:
    fail("Install 'brightnessctl' (sudo apt install brightnessctl) to control brightness.")
