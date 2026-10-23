# keywords: screenshot, screen, capture, snap, screen shot, print screen, grab screen, screengrab
# desc: Save a screenshot to your Pictures folder
# category: hardware
import datetime, shutil, subprocess
from pathlib import Path
from _lib import WIN, MAC, fail
from _sys import ps
folder = Path.home() / "Pictures" / "Screenshots"
folder.mkdir(parents=True, exist_ok=True)
path = folder / f"screenshot_{datetime.datetime.now():%Y%m%d_%H%M%S}.png"
done = False
try:
    from PIL import ImageGrab
    ImageGrab.grab(all_screens=True).save(path); done = True
except Exception:
    pass
if not done and WIN:
    ps("Add-Type -AssemblyName System.Windows.Forms,System.Drawing;"
       "$b=[System.Windows.Forms.SystemInformation]::VirtualScreen;"
       "$bmp=New-Object System.Drawing.Bitmap $b.Width,$b.Height;"
       "$g=[System.Drawing.Graphics]::FromImage($bmp);"
       "$g.CopyFromScreen($b.Location,[System.Drawing.Point]::Empty,$b.Size);$bmp.Save($env:TR_OUT)", out=path)
elif not done and MAC:
    subprocess.run(["screencapture", "-x", str(path)])
elif not done:
    for cmd in (["grim", str(path)], ["gnome-screenshot", "-f", str(path)], ["scrot", str(path)],
                ["import", "-window", "root", str(path)], ["spectacle", "-b", "-n", "-o", str(path)]):
        if shutil.which(cmd[0]) and subprocess.run(cmd, capture_output=True).returncode == 0:
            break
if path.exists() and path.stat().st_size > 0:
    print(f"Saved: {path}")
else:
    fail("Could not take a screenshot here (no screen available, or no screenshot tool installed).")
