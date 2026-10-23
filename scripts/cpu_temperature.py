# keywords: temperature, cpu temperature, cpu temp, how hot, processor temperature, laptop heat, thermal, overheating, check temp
# desc: Show processor temperature (where the computer allows it)
# category: system
import glob
from _lib import WIN, MAC, LINUX
from _sys import ps
vals = []
try:
    import psutil
    for name, arr in (psutil.sensors_temperatures() or {}).items():
        vals += [f"{name} {e.label or ''}: {e.current:.0f} C" for e in arr]
except (ImportError, AttributeError):
    pass
if not vals and LINUX:
    for z in sorted(glob.glob("/sys/class/thermal/thermal_zone*")):
        try:
            t = int(open(z + "/temp").read()) / 1000
            vals.append(f"{open(z + '/type').read().strip()}: {t:.0f} C")
        except (OSError, ValueError): continue
if not vals and WIN:
    t = ps("Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature | ForEach-Object { [math]::Round($_.CurrentTemperature/10-273.15) }")
    vals = [f"Thermal zone: {x} C" for x in t.split()]
print("\n".join(vals) if vals else
      "This computer does not expose temperature to normal programs."
      + (" On macOS it needs sudo powermetrics." if MAC else " Try HWiNFO or Core Temp." if WIN else ""))
