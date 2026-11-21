# keywords: iot, iot scene, iot list, my devices, all devices, home scene, run scene, scenes
# desc: One place for your home devices and computers: see everything (iot list) and save scenes that do several things at once (iot scene add night = device off lamp ; mqtt publish home lights/hall off)
# category: network
# usage: iot list | iot scene add <name> = <step> ; <step> | iot scene run <name> | iot scene list | iot scene remove <name>
# rawargs: full
# network: yes
# patterns: ^\s*iot\b
# priority: 3
import json, os, re, subprocess, sys, time
from pathlib import Path
from _lib import args_text, fail
from _conn import load_reg, save_reg, clean_name

t = re.sub(r"^\s*iot\s*", "", args_text(), flags=re.I).strip()
words = t.split()
cmd = words[0].lower() if words else "list"
ALLOWED = {"device", "devices", "mqtt", "serial", "computer", "computers", "ssh", "wake", "pause"}
LINK_OK = {"send", "run", "ping"}
MAX_STEPS = 20


def check_step(s):
    w = s.split()
    if not w:
        fail("A scene step is empty.")
    first = w[0].lower()
    if first == "link":
        if len(w) < 2 or w[1].lower() not in LINK_OK:
            fail("Scenes can use  link send / link run / link ping  only.")
    elif first == "pause":
        if len(w) != 2 or not w[1].isdigit() or int(w[1]) > 60:
            fail("Use  pause <seconds>  (up to 60).")
    elif first not in ALLOWED:
        fail(f"A scene step can be: {', '.join(sorted(ALLOWED - {'devices', 'computers'}))}, link send/run/ping. Not '{first}'.")


if cmd == "list":
    shown = False
    for label, reg, fmt in (("Smart devices", "devices", lambda v: f"{v.get('kind', '?')} {v.get('ip', '')}"),
                            ("MQTT brokers", "mqtt", lambda v: f"{v.get('host', '')}:{v.get('port', '')}"),
                            ("Computers (SSH)", "computers", lambda v: str(v.get("host") or v.get("target") or v.get("address") or "")),
                            ("Wake-on-LAN", "wake", lambda v: str(v.get("mac", "")))):
        r = load_reg(reg)
        if r:
            shown = True
            print(label + ":")
            for k, v in sorted(r.items()):
                print(f"  {k:<14}{fmt(v) if isinstance(v, dict) else ''}")
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        import jeeg_link
        from _lib import data_dir
        peers = jeeg_link.Store(data_dir()).peers()
        if peers:
            shown = True
            print("Other JeeG computers (link):")
            for r in sorted(peers.values(), key=lambda x: x.get("name", "")):
                print(f"  {r.get('name', '?'):<14}they may: {r.get('level', '?')}")
    except (ImportError, OSError, ValueError):
        pass
    sc = load_reg("scenes")
    if sc:
        shown = True
        print("Scenes:  " + ", ".join(sorted(sc)))
    if not shown:
        print("Nothing saved yet. Add a smart plug (device add), an MQTT broker (mqtt add), a computer (computer add) or pair another JeeG (link pair).")
elif cmd == "scene":
    sub = words[1].lower() if len(words) > 1 else "list"
    sc = load_reg("scenes")
    if sub == "list":
        if not sc:
            print("No scenes. Add one:  iot scene add night = device off lamp ; mqtt publish home lights/hall off")
        for k, v in sorted(sc.items()):
            print(f"  {k}")
            for s in v:
                print(f"      {s}")
    elif sub == "add":
        m = re.match(r"scene\s+add\s+(\S+)\s*=\s*(.+)$", t, re.I | re.S)
        if not m:
            fail("Usage: iot scene add <name> = <step> ; <step>     (steps: device on lamp ; mqtt publish home lights/x off ; pause 5)")
        steps = [x.strip() for x in m.group(2).split(";") if x.strip()]
        if not steps or len(steps) > MAX_STEPS:
            fail(f"A scene has 1 to {MAX_STEPS} steps, separated by ;")
        for s in steps:
            check_step(s)
        sc[clean_name(m.group(1), "scene name")] = steps
        save_reg("scenes", sc)
        print(f"Saved scene '{m.group(1).lower()}' ({len(steps)} steps). Run it:  iot scene run {m.group(1).lower()}")
    elif sub in {"remove", "delete"}:
        if sc.pop(clean_name(words[2] if len(words) > 2 else ""), None) is None:
            fail("No scene with that name.")
        save_reg("scenes", sc)
        print("Removed.")
    elif sub == "run":
        name = clean_name(words[2] if len(words) > 2 else "")
        if name not in sc:
            fail(f"No scene '{name}'. Saved: {', '.join(sorted(sc)) or 'none'}")
        engine = Path(__file__).resolve().parent.parent / "jeeg.py"
        bad = 0
        for i, s in enumerate(sc[name], 1):
            check_step(s)                                   # the file could have been edited by hand
            if s.split()[0].lower() == "pause":
                time.sleep(int(s.split()[1]))
                print(f"  {i}. waited {s.split()[1]} s")
                continue
            r = subprocess.run([sys.executable, str(engine), s], capture_output=True, text=True, timeout=120,
                               stdin=subprocess.DEVNULL, env=dict(os.environ))     # no --yes: steps that need a yes will say so
            lines = [x for x in (r.stdout + "\n" + r.stderr).splitlines() if x.strip() and not x.startswith(">>") and not re.search(r"^(ok|failed.*) in [\d.]+s$", x)]
            out = (lines[-1] if lines else "")[:140]
            print(f"  {i}. {s}  ->  {'ok' if r.returncode == 0 else 'FAILED'}  {out}")
            bad += r.returncode != 0
        print(f"Scene '{name}': {len(sc[name]) - bad} of {len(sc[name])} steps worked." if bad else f"Scene '{name}' done.")
        if bad:
            sys.exit(1)
    else:
        fail("Use:  iot scene add | run | list | remove")
else:
    fail("Use:  iot list | iot scene add | run | list | remove")
