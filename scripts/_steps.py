"""Steps that scenes (iot scene) and bridge rules may run: a short list of device and messaging tasks. Not a task."""
import os, re, subprocess, sys, time
from pathlib import Path
from _lib import fail

ALLOWED = {"device", "devices", "mqtt", "serial", "computer", "computers", "ssh", "wake", "pause", "ha", "hass", "zigbee", "z2m", "modbus", "tcp", "udp", "ws", "websocket",
           "rest", "webhook", "channel", "handoff", "bluetooth", "notify", "playbook", "log"}
LINK_OK = {"send", "run", "ping"}
SHOWN = "device, mqtt, serial, computer/ssh, wake, ha, zigbee, modbus, tcp, udp, ws, rest, webhook, channel, handoff, bluetooth, notify, log reading, playbook run, pause, link send/run/ping"


def check_step(s, fail_fn=fail):
    w = s.split()
    if not w:
        fail_fn("A step is empty.")
    first = w[0].lower()
    if first == "link":
        if len(w) < 2 or w[1].lower() not in LINK_OK:
            fail_fn("Steps can use  link send / link run / link ping  only.")
    elif first == "log":
        if len(w) < 3 or w[1].lower() != "reading":
            fail_fn("Use  log reading <name> <value>  for logging a sensor value.")
    elif first == "playbook":
        if len(w) < 3 or w[1].lower() != "run":
            fail_fn("Steps can only use  playbook run <name>.")
    elif first == "pause":
        if len(w) != 2 or not w[1].isdigit() or int(w[1]) > 60:
            fail_fn("Use  pause <seconds>  (up to 60).")
    elif first == "iot" or first not in ALLOWED:
        fail_fn(f"A step can be: {SHOWN}. Not '{first}'.")


def run_step(s, env_extra=None, timeout=120):
    """Run one step through JeeG itself (so every safety rule applies). No --yes: a step that needs a yes says so. -> (ok, one-line result)"""
    check_step(s)
    if s.split()[0].lower() == "pause":
        time.sleep(int(s.split()[1]))
        return True, f"waited {s.split()[1]} s"
    engine = Path(__file__).resolve().parent.parent / "jeeg.py"
    env = dict(os.environ)
    env.update(env_extra or {})
    try:
        r = subprocess.run([sys.executable, str(engine), s], capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL, env=env)
    except subprocess.TimeoutExpired:
        return False, "took too long"
    lines = [x for x in (r.stdout + "\n" + r.stderr).splitlines() if x.strip() and not x.startswith(">>") and not re.search(r"^(ok|failed.*) in [\d.]+s$", x)]
    return r.returncode == 0, (lines[-1] if lines else "")[:140]
