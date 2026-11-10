# keywords: mqtt, mqtt publish, mqtt listen, mqtt broker, send mqtt message, home assistant mqtt, iot message
# desc: Send or listen to MQTT messages (mqtt add home 192.168.1.2, mqtt publish home lights/kitchen on, mqtt listen home sensors/#)
# category: network
# usage: mqtt add <name> <host[:port]> [user] | mqtt publish <name> <topic> <message> | mqtt listen <name> <topic> [seconds] | mqtt list | mqtt remove <name>
# rawargs: full
# network: yes
# patterns: ^\s*mqtt\b
# priority: 3
import re
from _lib import args_text, fail
from _conn import load_reg, save_reg, clean_name, ask_secret
import _mqtt
t = re.sub(r"^\s*mqtt\s*", "", args_text(), flags=re.I).strip()
parts = t.split(None, 3)
cmd = parts[0].lower() if parts else "list"
reg = load_reg("mqtt")
if cmd == "list":
    print("Saved brokers:" if reg else "None saved. Add one:  mqtt add home 192.168.1.2")
    for k, v in sorted(reg.items()):
        print(f"  {k:<12} {v['host']}:{v['port']}{'  (user ' + v['user'] + ')' if v.get('user') else ''}{'  tls' if v.get('tls') else ''}")
elif cmd == "add":
    if len(parts) < 3:
        fail("Usage: mqtt add <name> <host[:port]> [user]   (the password is asked for, never typed in the command)")
    host, _, port = parts[2].partition(":")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.\-]*", host) or (port and not port.isdigit()):
        fail("That broker address does not look right.")
    user = parts[3].strip().split()[0] if len(parts) > 3 and parts[3].strip() else ""
    pw = ask_secret(f"Password for {user}: ") if user else ""
    port = int(port or 1883)
    reg[clean_name(parts[1])] = {"host": host, "port": port, "user": user, "password": pw, "tls": port == 8883}
    save_reg("mqtt", reg)
    print(f"Saved. Try:  mqtt publish {parts[1].lower()} test/hello hi")
elif cmd in {"remove", "delete"}:
    if reg.pop(clean_name(parts[1] if len(parts) > 1 else ""), None) is None:
        fail("No broker with that name.")
    save_reg("mqtt", reg)
    print("Removed.")
elif cmd in {"publish", "send", "listen", "subscribe"}:
    if len(parts) < 3:
        fail("Usage: mqtt publish <name> <topic> <message>   |   mqtt listen <name> <topic> [seconds]")
    name = clean_name(parts[1])
    if name not in reg:
        fail(f"No broker named '{name}'. Saved: {', '.join(sorted(reg)) or 'none'}")
    b = reg[name]
    topic = parts[2]
    if not topic or len(topic) > 200 or "\x00" in topic:
        fail("That topic does not look right.")
    try:
        s = _mqtt.connect(b["host"], b["port"], b.get("user", ""), b.get("password", ""), b.get("tls", False))
    except OSError as ex:
        fail(f"Could not connect: {ex}")
    try:
        if cmd in {"publish", "send"}:
            msg = parts[3] if len(parts) > 3 else ""
            if re.search(r"[+#]", topic):
                fail("A topic you publish to cannot contain + or #.")
            _mqtt.publish(s, topic, msg[:4000])
            print(f"Published to {topic}.")
        else:
            secs = 10
            if len(parts) > 3 and parts[3].strip().isdigit():
                secs = max(1, min(60, int(parts[3])))
            _mqtt.subscribe(s, topic)
            n = 0
            for tp, text in _mqtt.read_messages(s, secs):
                n += 1
                print(f"  {tp}: {text[:300]}")
            print(f"{n} message(s) in {secs} seconds." if n else f"No messages on {topic} in {secs} seconds.")
    finally:
        _mqtt.disconnect(s)
else:
    fail("Use:  mqtt add | publish | listen | list | remove")
