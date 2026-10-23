# keywords: usb devices, usb list, connected usb, what usb is plugged, plugged in devices, usb drives, connected devices
# desc: List connected USB devices
# category: system
import shutil
from _lib import WIN, MAC
from _sys import ps, out
if WIN:
    print(ps("Get-PnpDevice -Class USB -Status OK | Select-Object -ExpandProperty FriendlyName | Sort-Object -Unique") or "None found.")
elif MAC:
    print(out(["system_profiler", "SPUSBDataType"], timeout=20) or "None found.")
elif shutil.which("lsusb"):
    print(out(["lsusb"]) or "None found.")
else:
    print("Needs 'lsusb' (sudo apt install usbutils).")
