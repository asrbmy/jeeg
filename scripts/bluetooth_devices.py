# keywords: bluetooth devices, bluetooth list, bluetooth connect, bluetooth disconnect, paired bluetooth
# desc: List paired Bluetooth devices and connect or disconnect one (bluetooth list, bluetooth connect headphones). Uses the system's own tools; Linux needs bluetoothctl, macOS needs blueutil for connect.
# category: hardware
# usage: bluetooth list | bluetooth connect <name> | bluetooth disconnect <name>
# rawargs: full
# patterns: ^\s*bluetooth\s+(?:list|devices|connect|disconnect|paired)\b
# priority: 4
import platform, re, shutil, subprocess
from _lib import args_text, fail
t = re.sub(r"^\s*bluetooth\s*", "", args_text(), flags=re.I).strip()
w = t.split(None, 1)
cmd = w[0].lower() if w else "list"
name = w[1].strip() if len(w) > 1 else ""
sysname = platform.system()


def out(cmd_list, timeout=15):
    try:
        r = subprocess.run(cmd_list, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        return r.returncode, (r.stdout + r.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as ex:
        fail(f"Could not run {cmd_list[0]}: {ex}")


def devices():
    """[(mac, name)]"""
    if sysname == "Linux":
        if not shutil.which("bluetoothctl"):
            fail("Needs bluetoothctl (package: bluez).")
        _, o = out(["bluetoothctl", "devices", "Paired"])
        if not o or "Invalid" in o:
            _, o = out(["bluetoothctl", "devices"])
        return [(m.group(1), m.group(2)) for m in re.finditer(r"Device\s+([0-9A-F:]{17})\s+(.+)", o, re.I)]
    if sysname == "Darwin":
        if shutil.which("blueutil"):
            _, o = out(["blueutil", "--paired"])
            return [(m.group(1), m.group(2)) for m in re.finditer(r"address:\s*([0-9a-f\-]{17}).*?name:\s*\"([^\"]*)\"", o, re.I)]
        _, o = out(["system_profiler", "SPBluetoothDataType"], 30)
        return [("", l.strip().rstrip(":")) for l in o.splitlines() if l.startswith("          ") and not l.startswith("           ") and l.strip().endswith(":")]
    if sysname == "Windows":
        _, o = out(["powershell", "-NoProfile", "-Command", "Get-PnpDevice -Class Bluetooth | Where-Object {$_.Status -eq 'OK'} | Select-Object -ExpandProperty FriendlyName"], 30)
        return [("", l.strip()) for l in o.splitlines() if l.strip()]
    fail("Bluetooth is not supported on this system.")


if cmd in {"list", "devices", "paired"}:
    d = devices()
    print("\n".join(f"  {n}" + (f"   ({m})" if m else "") for m, n in d) if d else "No paired Bluetooth devices found.")
elif cmd in {"connect", "disconnect"}:
    if not name:
        fail(f"Usage: bluetooth {cmd} <device name>")
    m = [(a, n) for a, n in devices() if name.lower() in n.lower()]
    if len(m) != 1 or not m[0][0]:
        fail("Name one paired device clearly (see:  bluetooth list)." if len(m) != 1 else "This system's tools do not give the device address; use the Bluetooth settings.")
    if sysname == "Linux":
        rc, o = out(["bluetoothctl", cmd, m[0][0]], 25)
    elif sysname == "Darwin" and shutil.which("blueutil"):
        rc, o = out(["blueutil", "--" + cmd, m[0][0]], 25)
    else:
        fail("Connecting from JeeG works on Linux (bluetoothctl) and macOS (blueutil). Windows: use Bluetooth settings.")
    print(f"{cmd.capitalize()}ed {m[0][1]}." if rc == 0 and "fail" not in o.lower() else f"Did not work: {o[-200:]}")
else:
    fail("Use:  bluetooth list | connect <name> | disconnect <name>")
