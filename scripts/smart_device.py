# keywords: smart device, smart plug, device on, device off, shelly, tasmota, switch device, home device
# desc: Control smart plugs on your home network (device add lamp shelly 192.168.1.50, then: device on lamp / device off lamp / device status lamp)
# category: network
# usage: device add <name> <shelly|tasmota> <ip> | device on|off|toggle|status <name> | device list | device remove <name>
# rawargs: full
# network: yes
# patterns: ^\s*devices?\b
# priority: 3
import json, re, urllib.error, urllib.request
from _lib import args_text, fail
from _conn import load_reg, save_reg, clean_name, need_private, split_host
t = re.sub(r"^\s*devices?\s*", "", args_text(), flags=re.I).strip()
parts = t.split()
cmd = parts[0].lower() if parts else "list"
reg = load_reg("devices")


def call(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "JeeG"}), timeout=6) as r:
            return json.loads(r.read(200_000).decode("utf-8", "replace") or "{}")
    except urllib.error.HTTPError:
        return None
    except (urllib.error.URLError, OSError, ValueError) as ex:
        fail(f"Could not reach the device: {getattr(ex, 'reason', ex)}")


def shelly(ip, action):
    v = {"on": "true", "off": "false"}.get(action)
    r = call(f"http://{ip}/rpc/Switch.GetStatus?id=0")                      # newer models (Gen2+)
    if r is not None:
        if action == "toggle":
            call(f"http://{ip}/rpc/Switch.Toggle?id=0")
        elif v:
            call(f"http://{ip}/rpc/Switch.Set?id=0&on={v}")
        r = call(f"http://{ip}/rpc/Switch.GetStatus?id=0") or {}
        return bool(r.get("output"))
    if action in {"on", "off", "toggle"}:                                    # older models (Gen1)
        call(f"http://{ip}/relay/0?turn={action}")
    r = call(f"http://{ip}/relay/0")
    if r is None:
        fail("The device did not answer like a Shelly. Check the address and the kind.")
    return bool(r.get("ison"))


def tasmota(ip, action):
    cmd = {"on": "Power On", "off": "Power Off", "toggle": "Power Toggle", "status": "Power"}[action]
    r = call(f"http://{ip}/cm?cmnd=" + cmd.replace(" ", "%20"))
    if r is None:
        fail("The device did not answer like a Tasmota. Check the address and the kind.")
    val = str(r.get("POWER", r.get("POWER1", ""))).upper()
    return val in {"ON", "1", "TRUE"}


if cmd == "list":
    print("Saved devices:" if reg else "None saved. Add one:  device add lamp shelly 192.168.1.50")
    for k, v in sorted(reg.items()):
        print(f"  {k:<12} {v['kind']:<8} {v['ip']}")
elif cmd == "add":
    if len(parts) != 4 or parts[2].lower() not in {"shelly", "tasmota"}:
        fail("Usage: device add <name> <shelly|tasmota> <ip address>")
    need_private(split_host(parts[3], 80)[0], "Device")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.\-]*(?::\d{2,5})?", parts[3]):
        fail("That address does not look right.")
    reg[clean_name(parts[1])] = {"kind": parts[2].lower(), "ip": parts[3]}
    save_reg("devices", reg)
    print(f"Saved. Try:  device on {parts[1].lower()}")
elif cmd in {"remove", "delete"}:
    if reg.pop(clean_name(parts[1] if len(parts) > 1 else ""), None) is None:
        fail("No device with that name.")
    save_reg("devices", reg)
    print("Removed.")
elif cmd in {"on", "off", "toggle", "status"}:
    name = clean_name(parts[1] if len(parts) > 1 else "")
    if name not in reg:
        fail(f"No device named '{name}'. Saved: {', '.join(sorted(reg)) or 'none'}")
    d = reg[name]
    need_private(split_host(d["ip"], 80)[0], "Device")
    state = (shelly if d["kind"] == "shelly" else tasmota)(d["ip"], cmd)
    print(f"{name} is {'ON' if state else 'OFF'}.")
else:
    fail("Use:  device add | on | off | toggle | status | list | remove")
