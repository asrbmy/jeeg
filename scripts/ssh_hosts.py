# keywords: ssh hosts, host add, saved hosts, ssh host list
# desc: Save other computers you can reach with ssh (computer add pi pi@192.168.1.20), then run JeeG tasks on them
# category: network
# usage: computer add <name> <user@host> | computer list | computer remove <name>
# rawargs: full
# patterns: ^\s*computers?\s+(add|list|remove|delete)\b ;; \b(my|saved|remote|other)\s+computers\b
# priority: 3
import re
from _lib import args_text, fail
from _conn import load_reg, save_reg, clean_name
t = re.sub(r"^\s*(?:my\s+|saved\s+|remote\s+|other\s+)?computers?\s*", "", args_text(), flags=re.I).strip()
parts = t.split()
cmd = parts[0].lower() if parts else "list"
reg = load_reg("computers")
if cmd in {"list", "show"}:
    print("Saved computers:" if reg else "None saved. Add one:  computer add pi pi@192.168.1.20")
    for k, v in sorted(reg.items()):
        print(f"  {k:<12} {v}")
    if reg:
        print("Run a task there:  on <name> run <task>     (the other computer needs JeeG installed and your ssh key set up)")
elif cmd == "add":
    if len(parts) != 3 or not re.fullmatch(r"(?:[A-Za-z0-9._\-]+@)?[A-Za-z0-9][A-Za-z0-9.\-]*", parts[2]):
        fail("Usage: computer add <name> <user@host>   (no spaces; the host cannot start with a dash)")
    reg[clean_name(parts[1])] = parts[2]
    save_reg("computers", reg)
    print(f"Saved. Try:  on {parts[1].lower()} run disk space")
elif cmd in {"remove", "delete"}:
    if reg.pop(clean_name(parts[1] if len(parts) > 1 else ""), None) is None:
        fail("No computer with that name.")
    save_reg("computers", reg)
    print("Removed.")
else:
    fail("Use:  computer add | list | remove")
