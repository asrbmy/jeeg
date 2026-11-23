# keywords: home assistant, ha, hass, smart home hub, home assistant lights, ha entity
# desc: Control Home Assistant (add it once with ha add home http://homeassistant.local:8123, then ha states light, ha on light.kitchen, ha call switch.turn_off switch.fan). The access token is asked for and kept private.
# category: network
# usage: ha add <name> <address> | ha states [filter] | ha on|off|toggle <entity> | ha call <domain.service> <entity> [json] | ha list | ha remove <name>
# rawargs: full
# network: yes
# patterns: ^\s*(?:ha|hass|home\s*assistant)\b
# priority: 3
import json, re, urllib.error, urllib.request
from _lib import args_text, fail
from _conn import load_reg, save_reg, clean_name, check_url, ask_secret, mask_url
t = re.sub(r"^\s*(?:ha|hass|home\s*assistant)\s*", "", args_text(), flags=re.I).strip()
parts = t.split(None, 3)
cmd = parts[0].lower() if parts else "list"
reg = load_reg("homeassistant")


def inst():
    if not reg:
        fail("No Home Assistant saved. Add it:  ha add home http://homeassistant.local:8123   (you will be asked for a long-lived access token)")
    if len(reg) > 1:
        fail("More than one saved; keep one, or remove the others (ha remove <name>).")
    return next(iter(reg.values()))


def call(method, path, body=None):
    i = inst()
    check_url(i["url"])
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(i["url"].rstrip("/") + path, data=data, method=method,
                                 headers={"Authorization": "Bearer " + i["token"], "Content-Type": "application/json", "User-Agent": "JeeG"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read(2_000_000).decode("utf-8", "replace") or "null")
    except urllib.error.HTTPError as ex:
        fail("Home Assistant refused the token." if ex.code in {401, 403} else f"Home Assistant answered {ex.code}.")
    except (urllib.error.URLError, OSError, ValueError) as ex:
        fail(f"Could not reach Home Assistant: {getattr(ex, 'reason', ex)}")


if cmd == "list":
    print("Saved:" if reg else "None saved. Add it:  ha add home http://homeassistant.local:8123")
    for k, v in sorted(reg.items()):
        print(f"  {k:<12} {mask_url(v['url'])}")
elif cmd == "add":
    if len(parts) < 3:
        fail("Usage: ha add <name> <address>   (the token is asked for, never typed in the command)")
    check_url(parts[2])
    tok = ask_secret("Long-lived access token (Profile > Security in Home Assistant): ")
    if len(tok) < 20:
        fail("That token looks too short.")
    reg.clear()
    reg[clean_name(parts[1])] = {"url": parts[2].strip(), "token": tok}
    save_reg("homeassistant", reg)
    print("Saved. Try:  ha states")
elif cmd in {"remove", "delete"}:
    if reg.pop(clean_name(parts[1] if len(parts) > 1 else ""), None) is None:
        fail("No such name.")
    save_reg("homeassistant", reg)
    print("Removed.")
elif cmd == "states":
    flt = (parts[1] if len(parts) > 1 else "").lower()
    rows = [s for s in (call("GET", "/api/states") or []) if flt in s.get("entity_id", "").lower() or flt in str(s.get("attributes", {}).get("friendly_name", "")).lower()]
    for s in rows[:60]:
        print(f"  {s['entity_id']:<36}{str(s.get('state', ''))[:20]:<14}{str(s.get('attributes', {}).get('friendly_name', ''))[:30]}")
    print(f"{len(rows)} match(es)." + ("  (first 60 shown)" if len(rows) > 60 else ""))
elif cmd in {"on", "off", "toggle"}:
    ent = parts[1] if len(parts) > 1 else ""
    if not re.fullmatch(r"[a-z_]+\.[a-z0-9_]+", ent):
        fail("Give an entity like light.kitchen (see:  ha states).")
    call("POST", f"/api/services/homeassistant/turn_{cmd}" if cmd != "toggle" else "/api/services/homeassistant/toggle", {"entity_id": ent})
    print(f"Sent {cmd} to {ent}.")
elif cmd == "call":
    if len(parts) < 3 or not re.fullmatch(r"[a-z_]+\.[a-z0-9_]+", parts[1]) or not re.fullmatch(r"[a-z_]+\.[a-z0-9_]+", parts[2]):
        fail("Usage: ha call <domain.service> <entity> [json data]     e.g.  ha call light.turn_on light.kitchen {\"brightness\": 120}")
    body = {"entity_id": parts[2]}
    if len(parts) > 3:
        try:
            extra = json.loads(parts[3])
        except ValueError:
            fail("The extra data must be JSON.")
        if not isinstance(extra, dict):
            fail("The extra data must be a JSON object.")
        body.update({k: v for k, v in extra.items() if k != "entity_id"})
    dom, _, svc = parts[1].partition(".")
    call("POST", f"/api/services/{dom}/{svc}", body)
    print(f"Called {parts[1]} on {parts[2]}.")
else:
    fail("Use:  ha add | states | on | off | toggle | call | list | remove")
