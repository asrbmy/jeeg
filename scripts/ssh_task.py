# keywords: ssh task, remote task, task on my pi, task on my server
# desc: Run a JeeG task on another computer over ssh (on pi run disk space). Needs JeeG there and an ssh key (no password prompts).
# category: network
# usage: on <name> run <task>
# confirm: yes
# rawargs: full
# network: yes
# patterns: ^\s*on\s+[A-Za-z0-9_\-]+\s+run\b
# priority: 4
import re, shlex, shutil, subprocess
from _lib import args_text, fail
from _conn import load_reg
m = re.match(r"^\s*(?:run\s+)?on\s+([A-Za-z0-9_\-]+)\s+run\s+(.+)$", args_text(), re.I | re.S)
if not m:
    fail("Usage: on <name> run <task>   e.g. on pi run disk space   (save it first: computer add pi pi@192.168.1.20)")
name, task = m.group(1).lower(), m.group(2).strip()[:500]
reg = load_reg("computers")
if name not in reg:
    fail(f"No saved computer '{name}'. Saved: {', '.join(sorted(reg)) or 'none'}. Add one: computer add {name} user@host")
target = reg[name]
if target.startswith("-") or not re.fullmatch(r"(?:[A-Za-z0-9._\-]+@)?[A-Za-z0-9][A-Za-z0-9.\-]*", target):
    fail("The saved address looks wrong; remove and add it again.")
ssh = shutil.which("ssh")
if not ssh:
    fail("ssh is not installed. Windows 10/11: Settings > Optional features > OpenSSH Client.")
cmd = [ssh, "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=accept-new", "--", target, "jeeg " + shlex.quote(task)]
try:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL, errors="replace")
except subprocess.TimeoutExpired:
    fail("It took over 2 minutes, so it was stopped.")
out = ((r.stdout or "") + (r.stderr or "")).strip()
print(out[:6000] if out else "(no output)")
if r.returncode == 255:
    fail("Could not connect. Check that the computer is on, the address is right, and ssh keys are set up (ssh-copy-id).")
raise SystemExit(0 if r.returncode == 0 else 1)
