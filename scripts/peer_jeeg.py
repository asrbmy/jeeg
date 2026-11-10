# keywords: peer, other jeeg, jeeg peer, run on another jeeg, remote jeeg, jeeg to jeeg
# desc: Talk to a JeeG on another computer through its AI-mode link (peer add office <link>, peer run office disk space)
# category: network
# usage: peer add <name> <link from 'connect ai'> | peer run <name> <task> | peer list | peer remove <name>
# rawargs: full
# private: yes
# network: yes
# patterns: ^\s*peers?\b
# priority: 3
import json, re, urllib.error, urllib.parse, urllib.request
from _lib import args_text, fail
from _conn import load_reg, save_reg, clean_name, check_url, mask_url
t = re.sub(r"^\s*peers?\s*", "", args_text(), flags=re.I).strip()
parts = t.split(None, 2)
cmd = parts[0].lower() if parts else "list"
reg = load_reg("peers")
if cmd == "list":
    print("Saved peers:" if reg else "None saved. On the other computer run  connect ai  and copy the link, then:  peer add office <link>")
    for k, v in sorted(reg.items()):
        print(f"  {k:<12} {mask_url(v)}")
elif cmd == "add":
    if len(parts) < 3:
        fail("Usage: peer add <name> <link>")
    link = parts[2].strip().split()[0]
    link = re.sub(r"(?:mcp|run)?/?$", "", link.split("?")[0])
    link = link if link.endswith("/") else link + "/"
    check_url(link)
    reg[clean_name(parts[1])] = link
    save_reg("peers", reg)
    print(f"Saved. The link is kept private. Try:  peer run {parts[1].lower()} gst 100 18")
elif cmd in {"remove", "delete"}:
    if reg.pop(clean_name(parts[1] if len(parts) > 1 else ""), None) is None:
        fail("No peer with that name.")
    save_reg("peers", reg)
    print("Removed.")
elif cmd == "run":
    if len(parts) < 3:
        fail("Usage: peer run <name> <task>")
    name = clean_name(parts[1])
    if name not in reg:
        fail(f"No peer named '{name}'. Saved: {', '.join(sorted(reg)) or 'none'}")
    check_url(reg[name])
    url = reg[name] + "run?" + urllib.parse.urlencode({"q": parts[2][:500]})
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "JeeG"}), timeout=130) as r:
            d = json.loads(r.read(500_000).decode("utf-8", "replace"))
    except urllib.error.HTTPError as ex:
        try:
            d = json.loads(ex.read(50_000).decode("utf-8", "replace"))
        except ValueError:
            fail(f"'{name}' answered {ex.code}. Its AI-mode link may have expired; run  connect ai  there again.")
    except (urllib.error.URLError, OSError, ValueError) as ex:
        fail(f"Could not reach '{name}': {getattr(ex, 'reason', ex)}")
    print(str(d.get("output", ""))[:20000] or "(no output)")
    raise SystemExit(0 if d.get("ok") else 1)
else:
    fail("Use:  peer add | run | list | remove")
