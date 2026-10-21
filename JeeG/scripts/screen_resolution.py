# keywords: screen resolution, display resolution, screen size, monitor resolution, display size, how many pixels, resolution
# desc: Show your screen resolution
# category: system
import re
from _lib import WIN, MAC
from _sys import out
if WIN:
    import ctypes
    try: ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception: pass
    u = ctypes.windll.user32
    print(f"Primary screen: {u.GetSystemMetrics(0)} x {u.GetSystemMetrics(1)}  ({u.GetSystemMetrics(80)} monitor(s))")
elif MAC:
    print("\n".join(l.strip() for l in out(["system_profiler", "SPDisplaysDataType"], timeout=20).splitlines() if "Resolution" in l) or "Not available.")
else:
    x = out(["xrandr", "--current"])
    cur = [l.split()[0] + "  " + re.search(r"(\d+x\d+)", l).group(1) for l in x.splitlines() if " connected" in l and re.search(r"\d+x\d+", l)]
    print("\n".join(cur) if cur else (out(["xdpyinfo"]).split("dimensions:")[-1].split("\n")[0].strip() or "Not available (needs xrandr on X11)."))
