# keywords: setup home, find home devices, discover devices, find smart home, scan for devices, home setup, find mqtt, find home assistant
# desc: Look on your home network for Home Assistant, MQTT brokers, Shelly and Tasmota plugs, and print the exact commands to save them (setup home, or setup home 192.168.1)
# category: network
# usage: setup home [192.168.1 | 192.168.1.50]
# rawargs: full
# network: yes
# patterns: ^\s*(?:setup|set up)\s+home\b ;; \b(find|discover|scan for)\b.*\b(home devices|smart home|smart plugs?)\b
# priority: 4
import concurrent.futures as cf, json, re, socket, urllib.request
from _lib import args_text, fail
from _conn import need_private, is_private_host
t = re.sub(r"^\s*(?:setup|set up)\s+home\s*", "", args_text(), flags=re.I).strip()


def my_prefix():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip.rsplit(".", 1)[0]
    except OSError:
        return ""


if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", t):
    hosts = [t]
elif re.fullmatch(r"\d{1,3}(\.\d{1,3}){2}", t):
    hosts = [f"{t}.{i}" for i in range(1, 255)]
elif not t:
    pre = my_prefix()
    if not pre:
        fail("Could not tell which network you are on. Say it:  setup home 192.168.1")
    hosts = [f"{pre}.{i}" for i in range(1, 255)]
else:
    fail("Usage: setup home [192.168.1 | 192.168.1.50]")
for h in hosts[:1]:
    need_private(h, "Network")
HA_PORT, MQTT_PORT = 8123, 1883


def open_port(h, p, t=0.35):
    try:
        socket.create_connection((h, p), t).close()
        return True
    except OSError:
        return False


def get(h, path, port=80):
    try:
        with urllib.request.urlopen(urllib.request.Request(f"http://{h}:{port}{path}", headers={"User-Agent": "JeeG"}), timeout=1.5) as r:
            return r.read(20000).decode("utf-8", "replace")
    except Exception:
        return None


def probe(h):
    found = []
    if open_port(h, HA_PORT):
        body = get(h, "/api/", HA_PORT)
        found.append(("homeassistant", h, HA_PORT, "Home Assistant" if body is not None else "something on the Home Assistant port"))
    if open_port(h, MQTT_PORT):
        found.append(("mqtt", h, MQTT_PORT, "MQTT broker"))
    if open_port(h, 80):
        b = get(h, "/shelly")
        if b and '"type"' in b:
            try:
                found.append(("shelly", h, 80, "Shelly " + str(json.loads(b).get("type", ""))))
            except ValueError:
                pass
        b = get(h, "/cm?cmnd=Status%200")
        if b and '"Status"' in b:
            found.append(("tasmota", h, 80, "Tasmota"))
    return found


print(f"Looking at {len(hosts)} address(es) for Home Assistant, MQTT, Shelly and Tasmota...")
res = []
with cf.ThreadPoolExecutor(max_workers=64) as ex:
    for r in ex.map(probe, hosts):
        res += r
if not res:
    print("Nothing found. The devices may be off, on another network, or use other ports.")
    raise SystemExit(0)
n = {"shelly": 0, "tasmota": 0, "mqtt": 0, "homeassistant": 0}
print("Found:")
for kind, h, p, label in sorted(res, key=lambda x: (x[0], x[1])):
    n[kind] += 1
    print(f"  {h:<16}{label}")
print("\nTo save them, run:")
for kind, h, p, label in sorted(res, key=lambda x: (x[0], x[1])):
    nm = f"{kind}{n[kind]}" if n[kind] > 1 else kind
    if kind == "homeassistant":
        print(f"  ha add home http://{h}:{p}")
    elif kind == "mqtt":
        print(f"  mqtt add home {h}{'' if p == 1883 else ':' + str(p)}")
    else:
        print(f"  device add {kind}-{h.rsplit('.', 1)[1]} {kind} {h}")
print("\nNothing was saved or changed. Passwords and tokens are asked for when you save.")
