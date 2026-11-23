# keywords: bridge, bridge rule, when message then, if this then that, connect devices, protocol bridge, automation rule
# desc: Rules that connect things: when a message arrives from MQTT, a webhook, UDP/TCP, serial, WebSocket, a channel or a chat, do steps on something else (bridge add door when mqtt home door/front if contains open then ha on light.hall ; channel post lab door opened). Run them with: bridge run. Terminal only.
# category: network
# usage: bridge add <name> when <source> [if contains <word>] then <step> ; <step> | bridge list | bridge remove <name> | bridge test <name> <message> | bridge run [minutes]
# rawargs: full
# network: yes
# patterns: ^\s*bridges?\b
# priority: 3
import json, os, queue, re, secrets, sys, threading, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import args_text, fail
from _conn import load_reg, save_reg, clean_name
import _steps

t = re.sub(r"^\s*bridges?\s*", "", args_text(), flags=re.I).strip()
cmd, _, rest = t.partition(" ")
cmd, rest = cmd.lower() or "list", rest.strip()
rules = load_reg("bridge")
MAX_STEPS, MAX_RULES = 10, 30
SAFE = re.compile(r"[^A-Za-z0-9 ._:/@#+\-]")


def clean_value(v):
    return SAFE.sub("", v or "")[:120].strip()


def fill(step, topic, msg, sender):
    """Put {msg} {topic} {from} into a step. Only plain characters get through, so a message can never add words like ';' or quotes."""
    vals = {"msg": clean_value(msg), "topic": clean_value(topic), "from": clean_value(sender)}
    used = re.findall(r"\{(msg|topic|from)\}", step)
    if any(not vals[u] for u in used):
        return None
    return re.sub(r"\{(msg|topic|from)\}", lambda m: vals[m.group(1)], step)


def parse_source(s):
    w = s.split()
    k = w[0].lower() if w else ""
    if k == "mqtt" and len(w) == 3:
        if clean_name(w[1]) not in load_reg("mqtt"):
            fail(f"No MQTT broker named '{w[1]}' (add one:  mqtt add home 192.168.1.2).")
        if len(w[2]) > 200 or "\x00" in w[2]:
            fail("That topic does not look right.")
        return {"kind": "mqtt", "broker": clean_name(w[1]), "topic": w[2]}
    if k in {"webhook", "udp", "tcp"} and len(w) == 2 and w[1].isdigit() and 1024 <= int(w[1]) <= 65535:
        d = {"kind": k, "port": int(w[1])}
        if k == "webhook":
            d["token"] = secrets.token_urlsafe(16)
        return d
    if k == "serial" and 2 <= len(w) <= 3:
        if not re.fullmatch(r"(?:COM\d{1,3}|/dev/[A-Za-z0-9_./\-]{3,40}|cu\.[A-Za-z0-9_.\-]+)", w[1]):
            fail("Give a port such as COM3 or /dev/ttyUSB0.")
        return {"kind": "serial", "port": w[1], "baud": int(w[2]) if len(w) == 3 and w[2].isdigit() else 9600}
    if k in {"ws", "websocket"} and len(w) == 2:
        from urllib.parse import urlparse
        from _conn import need_private
        u = urlparse(w[1])
        if u.scheme == "ws":
            need_private(u.hostname or "", "Device")
        elif u.scheme != "wss":
            fail("Use ws:// (your own network) or wss://")
        return {"kind": "ws", "url": w[1]}
    if k == "channel" and len(w) == 2:
        import jeeg_chan
        try:
            return {"kind": "channel", "name": jeeg_chan.clean(w[1])}
        except jeeg_chan.ChanError as ex:
            fail(str(ex))
    if k == "chat" and len(w) == 1:
        return {"kind": "chat"}
    if k == "every" and len(w) == 3 and w[1].isdigit() and w[2].lower().rstrip("s") in {"minute", "hour", "second"}:
        secs = int(w[1]) * {"second": 1, "minute": 60, "hour": 3600}[w[2].lower().rstrip("s")]
        if not 10 <= secs <= 7 * 86400:
            fail("A timer runs from every 10 seconds to every 7 days.")
        return {"kind": "timer", "secs": secs}
    fail("A source is one of:  every <n> seconds|minutes|hours | mqtt <broker> <topic> | webhook <port> | udp <port> | tcp <port> | serial <port> [baud] | ws <address> | channel <name> | chat")


def describe(r):
    s = r["src"]
    k = s["kind"]
    return {"mqtt": f"mqtt {s.get('broker')} {s.get('topic')}", "webhook": f"webhook on port {s.get('port')}", "udp": f"udp port {s.get('port')}", "tcp": f"tcp port {s.get('port')}",
            "serial": f"serial {s.get('port')}", "ws": f"ws {s.get('url')}", "channel": f"channel {s.get('name')}", "chat": "chat messages", "timer": f"every {s.get('secs')} seconds"}[k]


def trigger(name, r, topic, msg, sender, out):
    """Run one rule's steps for one incoming message."""
    if r.get("contains") and r["contains"].lower() not in (msg or "").lower():
        return
    for st in r["steps"]:
        s2 = fill(st, topic, msg, sender)
        if s2 is None:
            out(f"[{name}] skipped a step: the message had nothing usable for it")
            continue
        ok_, line = _steps.run_step(s2, {"JEEG_VIA_BRIDGE": name})
        out(f"[{name}] {s2}  ->  {'ok' if ok_ else 'FAILED'}  {line}")


if cmd == "list":
    if not rules:
        print("No bridge rules. Example:  bridge add door when mqtt home door/front if contains open then channel post lab front door opened")
    for k, r in sorted(rules.items()):
        print(f"  {k}\n      when {describe(r)}" + (f" and the text contains '{r['contains']}'" if r.get("contains") else ""))
        if r["src"]["kind"] == "webhook":
            print(f"      send to:  http://<this computer's address>:{r['src']['port']}/hook/<secret>   (the secret is in your JeeG folder; 'bridge show {k}' prints it)")
        for st in r["steps"]:
            print(f"      then {st}")
elif cmd == "show":
    r = rules.get(clean_name(rest))
    if not r:
        fail("No such rule.")
    print(json.dumps({"when": describe(r), "steps": r["steps"], "contains": r.get("contains", ""), **({"webhook path": "/hook/" + r["src"]["token"]} if r["src"]["kind"] == "webhook" else {})}, indent=1))
elif cmd == "add":
    m = re.match(r"(\S+)\s+when\s+(.+?)(?:\s+if\s+contains\s+(\S+))?\s+then\s+(.+)$", rest, re.I | re.S)
    if not m:
        fail("Usage: bridge add <name> when <source> [if contains <word>] then <step> ; <step>")
    if len(rules) >= MAX_RULES:
        fail(f"At most {MAX_RULES} rules.")
    steps = [x.strip() for x in m.group(4).split(";") if x.strip()]
    if not steps or len(steps) > MAX_STEPS:
        fail(f"A rule has 1 to {MAX_STEPS} steps, separated by ;")
    for st in steps:
        _steps.check_step(re.sub(r"\{(?:msg|topic|from)\}", "x", st))
    rule = {"src": parse_source(m.group(2)), "steps": steps, "contains": (m.group(3) or "")[:60], "cooldown": 2}
    name = clean_name(m.group(1))
    rules[name] = rule
    save_reg("bridge", rules)
    print(f"Saved rule '{name}': when {describe(rule)}, do {len(steps)} step(s). Start all rules:  bridge run")
    print("In steps, {msg} {topic} {from} are replaced by what arrived (letters, numbers and . : / @ # + - only).")
    if rule["src"]["kind"] == "webhook":
        print(f"Webhook address:  http://<this computer's address>:{rule['src']['port']}/hook/{rule['src']['token']}   (keep it secret; 'bridge show {name}' shows it again)")
elif cmd in {"remove", "delete"}:
    if rules.pop(clean_name(rest), None) is None:
        fail("No such rule.")
    save_reg("bridge", rules)
    print("Removed.")
elif cmd == "test":
    w = rest.split(None, 1)
    r = rules.get(clean_name(w[0] if w else ""))
    if not r:
        fail("No such rule. Usage: bridge test <name> <message>")
    trigger(clean_name(w[0]), r, "test", w[1] if len(w) > 1 else "", "test", print)
elif cmd == "run":
    if os.environ.get("JEEG_VIA_AI") == "1" or os.environ.get("JEEG_VIA_PEER"):
        fail("The bridge can only be started at this computer.")
    if not rules:
        fail("No rules yet (bridge add ...).")
    import _bridge_src, signal
    for sg in (signal.SIGINT, getattr(signal, "SIGTERM", None)):          # also works when started in the background, where Ctrl+C may be ignored by default
        if sg is not None:
            try:
                signal.signal(sg, signal.default_int_handler)
            except (ValueError, OSError):
                pass
    mins = int(rest) if rest.isdigit() else 0
    q = queue.Queue(maxsize=200)
    stop = threading.Event()
    log = lambda s: print(time.strftime("%H:%M:%S ") + s, flush=True)
    for name, r in rules.items():
        _bridge_src.start(name, r["src"], lambda tp, tx, sd, n=name: (q.put_nowait((n, tp, tx, sd)) if not q.full() else None), stop, log)
    log(f"Bridge running with {len(rules)} rule(s). Ctrl+C stops it." + (f" It stops by itself after {mins} minute(s)." if mins else ""))
    last, hourly = {}, {}
    end = time.time() + mins * 60 if mins else None
    try:
        while not stop.is_set() and (end is None or time.time() < end):
            try:
                name, tp, tx, sd = q.get(timeout=0.5)
            except queue.Empty:
                continue
            r = rules.get(name)
            now = time.time()
            if now - last.get(name, 0) < r.get("cooldown", 2):
                continue                                     # a rule cannot fire more than once per cooldown: stops loops
            hits = [x for x in hourly.get(name, []) if now - x < 3600]
            if len(hits) >= 120:
                if len(hits) == 120:
                    log(f"[{name}] paused: too many triggers this hour (120)")
                    hourly[name] = hits + [now]
                continue
            hourly[name] = hits + [now]
            last[name] = now
            trigger(name, r, tp, tx, sd, log)
    except KeyboardInterrupt:
        pass
    stop.set()
    log("Bridge stopped.")
else:
    fail("Use:  bridge add | list | show | remove | test | run")
