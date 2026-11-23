# keywords: zigbee, zigbee2mqtt, zigbee lights, zigbee devices, z2m
# desc: Switch Zigbee devices through zigbee2mqtt over your saved MQTT broker (zigbee devices home, zigbee on home hall-lamp, zigbee off home hall-lamp, zigbee set home hall-lamp brightness 120). Save the broker first: mqtt add
# category: network
# usage: zigbee devices <broker> | zigbee on|off|toggle <broker> <device> | zigbee set <broker> <device> <key> <value> | zigbee get <broker> <device>
# rawargs: full
# network: yes
# patterns: ^\s*(?:zigbee|z2m)\b
# priority: 3
import json, re, time
from _lib import args_text, fail
from _conn import load_reg, clean_name
import _mqtt
t = re.sub(r"^\s*(?:zigbee|z2m)\s*", "", args_text(), flags=re.I).strip()
w = t.split()
cmd = w[0].lower() if w else "devices"
BASE = "zigbee2mqtt"
if len(w) < 2:
    fail("Usage: zigbee devices <broker> | zigbee on|off|toggle <broker> <device> | zigbee set <broker> <device> <key> <value>")
reg = load_reg("mqtt")
bn = clean_name(w[1])
if bn not in reg:
    fail(f"No MQTT broker named '{bn}'. Saved: {', '.join(sorted(reg)) or 'none'}   (add one:  mqtt add home 192.168.1.2)")
b = reg[bn]


def dev(i):
    d = w[i] if len(w) > i else ""
    if not re.fullmatch(r"[A-Za-z0-9 _\-.]{1,60}", d):
        fail("Give the device's friendly name (letters, numbers, - or _).")
    return d


try:
    s = _mqtt.connect(b["host"], b["port"], b.get("user", ""), b.get("password", ""), b.get("tls", False))
except OSError as ex:
    fail(f"Could not connect to the broker: {ex}")
try:
    if cmd == "devices":
        _mqtt.subscribe(s, f"{BASE}/bridge/devices")
        got = None
        for tp, text in _mqtt.read_messages(s, 6, 3):
            got = text
            break
        if not got:
            fail("No answer from zigbee2mqtt (is it running and using the base topic 'zigbee2mqtt'?).")
        try:
            lst = json.loads(got)
        except ValueError:
            fail("zigbee2mqtt answered something unexpected.")
        for d in lst:
            if d.get("type") != "Coordinator":
                print(f"  {d.get('friendly_name', '?'):<28}{d.get('type', ''):<10}{(d.get('definition') or {}).get('description', '')[:40]}")
    elif cmd in {"on", "off", "toggle"}:
        _mqtt.publish(s, f"{BASE}/{dev(2)}/set", json.dumps({"state": cmd.upper()}))
        print(f"Sent {cmd} to {dev(2)}.")
    elif cmd == "set":
        if len(w) < 5 or not re.fullmatch(r"[a-z_]{1,30}", w[3]):
            fail("Usage: zigbee set <broker> <device> <key> <value>     e.g.  zigbee set home hall-lamp brightness 120")
        v = w[4]
        val = int(v) if v.lstrip("-").isdigit() else v
        _mqtt.publish(s, f"{BASE}/{dev(2)}/set", json.dumps({w[3]: val}))
        print(f"Set {w[3]} to {val} on {dev(2)}.")
    elif cmd == "get":
        d = dev(2)
        _mqtt.subscribe(s, f"{BASE}/{d}")
        _mqtt.publish(s, f"{BASE}/{d}/get", json.dumps({"state": ""}))
        for tp, text in _mqtt.read_messages(s, 5, 1):
            print(f"  {text[:400]}")
            break
        else:
            print("No answer.")
    else:
        fail("Use:  zigbee devices | on | off | toggle | set | get")
finally:
    _mqtt.disconnect(s)
