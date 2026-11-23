# keywords: playbook, playbooks, saved job, reviewed job, multi step job, run playbook, ai playbook
# desc: Save a reviewed multi-step job under a name and run it any time, by you or by an AI that is allowed to run but not change it (playbook add morning = show reminders ; what is due ; playbook run morning). Adding and removing are terminal only.
# category: productivity
# usage: playbook add <name> = <step> ; <step> | playbook run <name> | playbook list | playbook show <name> | playbook remove <name>
# rawargs: full
# patterns: ^\s*playbooks?\b
# priority: 3
import os, re, sys
from _lib import args_text, fail
from _conn import load_reg, save_reg, clean_name
import _steps

FORBID = {"link", "update", "upgrade", "autorun", "kit", "audit", "policy", "gui", "window", "windows", "desktop", "plugin", "plugins", "allow", "deny", "pack", "connect",
          "install", "bridge", "playbook", "iot", "browser", "shutdown", "restart", "delete", "format", "export", "import", "admin"}
MAX_STEPS = 15
t = re.sub(r"^\s*playbooks?\s*", "", args_text(), flags=re.I).strip()
words = t.split()
cmd = words[0].lower() if words else "list"
pb = load_reg("playbooks")
remote = os.environ.get("JEEG_VIA_AI") == "1" or bool(os.environ.get("JEEG_VIA_PEER")) or bool(os.environ.get("JEEG_VIA_BRIDGE"))


def check(step):
    w = step.split()
    if not w:
        fail("A step is empty.")
    if w[0].lower() in FORBID:
        fail(f"A playbook step cannot start with '{w[0]}'. Those can only be used directly, at the computer.")


if cmd == "list":
    if not pb:
        print("No playbooks. Add one:  playbook add morning = show reminders ; what is due")
    for k, v in sorted(pb.items()):
        print(f"  {k:<16}{len(v)} step(s)")
elif cmd == "show":
    n = clean_name(words[1] if len(words) > 1 else "")
    if n not in pb:
        fail("No such playbook.")
    for i, s in enumerate(pb[n], 1):
        print(f"  {i}. {s}")
elif cmd in {"add", "remove", "delete"}:
    if remote:
        fail("Playbooks can only be added or removed at this computer, not by an AI, another computer or a rule.")
    if cmd == "add":
        m = re.match(r"add\s+(\S+)\s*=\s*(.+)$", t, re.I | re.S)
        if not m:
            fail("Usage: playbook add <name> = <step> ; <step>")
        steps = [x.strip() for x in m.group(2).split(";") if x.strip()]
        if not steps or len(steps) > MAX_STEPS:
            fail(f"A playbook has 1 to {MAX_STEPS} steps, separated by ;")
        for s in steps:
            check(s)
        pb[clean_name(m.group(1))] = steps
        save_reg("playbooks", pb)
        print(f"Saved playbook '{m.group(1).lower()}' ({len(steps)} steps). Run it:  playbook run {m.group(1).lower()}")
    else:
        if pb.pop(clean_name(words[1] if len(words) > 1 else ""), None) is None:
            fail("No such playbook.")
        save_reg("playbooks", pb)
        print("Removed.")
elif cmd == "run":
    n = clean_name(words[1] if len(words) > 1 else "")
    if n not in pb:
        fail(f"No playbook '{n}'. Saved: {', '.join(sorted(pb)) or 'none'}")
    import subprocess, time
    from pathlib import Path
    engine = Path(__file__).resolve().parent.parent / "jeeg.py"
    bad = 0
    for i, s in enumerate(pb[n], 1):
        check(s)                                              # checked again in case the file was edited by hand
        try:
            r = subprocess.run([sys.executable, str(engine), s], capture_output=True, text=True, timeout=180, stdin=subprocess.DEVNULL,
                               env=dict(os.environ, JEEG_VIA_PLAYBOOK=n))     # no --yes: a step that needs a yes stops and says so
            good, out = r.returncode == 0, (r.stdout if r.returncode == 0 else r.stdout + r.stderr)
        except subprocess.TimeoutExpired:
            good, out = False, "took too long"
        lines = [x for x in out.splitlines() if x.strip() and not x.startswith(">>") and not re.search(r"^(ok|failed.*) in [\d.]+s$", x)]
        print(f"--- {i}. {s}  {'ok' if good else 'FAILED'}")
        for x in lines[:12]:
            print("   " + x[:200])
        bad += not good
        if not good:
            print(f"Stopped at step {i}: nothing after it was run.")
            sys.exit(1)
    print(f"Playbook '{n}' done.")
else:
    fail("Use:  playbook add | run | list | show | remove")
