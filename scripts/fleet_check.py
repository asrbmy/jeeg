# keywords: fleet check, check all computers, all my computers, status of all computers, check my servers, all machines, health of all computers
# desc: Ask every saved computer (see "computer add") for its health at once: disk, memory, uptime. Needs JeeG and an ssh key on each.
# category: network
# network: yes
# usage: check all computers
# confirm: yes
# rawargs: full
# patterns: \b(?:check|status\s+of|health\s+of)\s+(?:all|every)\s+(?:of\s+)?(?:my\s+)?(?:computers|machines|servers|pis)\b ;; \bfleet\s+(?:check|status|health)\b ;; \b(?:all|every)\s+(?:my\s+)?(?:computers|machines|servers)\s+(?:health|status|ok)\b
# priority: 4
import re, shlex, shutil, subprocess, threading
from _lib import fail
from _conn import load_reg

reg = load_reg("computers")
if not reg:
    fail("No saved computers. Add one:  computer add pi pi@192.168.1.20")
ssh = shutil.which("ssh")
if not ssh:
    fail("ssh is not installed. Windows 10/11: Settings > Optional features > OpenSSH Client.")
results = {}


def ask(name, target):
    if target.startswith("-") or not re.fullmatch(r"(?:[A-Za-z0-9._\-]+@)?[A-Za-z0-9][A-Za-z0-9.\-]*", target):
        results[name] = (False, "the saved address looks wrong")
        return
    cmd = [ssh, "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", "-o", "StrictHostKeyChecking=accept-new", "--", target, "jeeg " + shlex.quote("health check")]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL, errors="replace")
    except subprocess.TimeoutExpired:
        results[name] = (False, "no answer in 60 seconds")
        return
    if r.returncode == 255:
        results[name] = (False, "could not connect (off, wrong address, or no ssh key)")
    elif r.returncode != 0:
        results[name] = (False, ((r.stdout or "") + (r.stderr or "")).strip().splitlines()[-1][:100] if (r.stdout or r.stderr) else "JeeG is not installed there?")
    else:
        results[name] = (True, (r.stdout or "").strip())


ths = [threading.Thread(target=ask, args=(n, t), daemon=True) for n, t in list(sorted(reg.items()))[:20]]
for t in ths:
    t.start()
for t in ths:
    t.join(75)
bad = 0
for n in sorted(reg)[:20]:
    ok, out = results.get(n, (False, "timed out"))
    if not ok:
        bad += 1
        print(f"\n{n}: PROBLEM - {out}")
        continue
    lines = [ln for ln in out.splitlines() if ln.strip() and not ln.startswith("Computer health")]
    print(f"\n{n}:")
    for ln in lines[:8]:
        print("  " + ln.strip())
print(f"\n{len(reg) - bad} of {len(reg)} computers answered." + ("" if not bad else "  Check the ones marked PROBLEM."))
raise SystemExit(1 if bad else 0)
