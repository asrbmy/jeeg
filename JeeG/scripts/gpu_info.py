# keywords: gpu, graphics card, video card, gpu info, graphics info, nvidia, display adapter, which gpu
# desc: Show graphics card details
# category: system
import shutil
from _lib import WIN, MAC
from _sys import ps, out
if WIN:
    print(ps("Get-CimInstance Win32_VideoController | ForEach-Object { $_.Name + '   driver ' + $_.DriverVersion }") or "Not available.")
elif MAC:
    print("\n".join(l.strip() for l in out(["system_profiler", "SPDisplaysDataType"], timeout=20).splitlines() if "Chipset" in l or "VRAM" in l or "Cores" in l) or "Not available.")
else:
    t = out(["lspci"]) if shutil.which("lspci") else ""
    rows = [l.split(": ", 1)[-1] for l in t.splitlines() if "VGA" in l or "3D controller" in l or "Display controller" in l]
    print("\n".join(rows) or "Not available (needs lspci: sudo apt install pciutils).")
if shutil.which("nvidia-smi"):
    print(out(["nvidia-smi", "--query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total", "--format=csv,noheader"]))
