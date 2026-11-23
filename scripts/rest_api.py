# keywords: rest, rest api, api call, call api, http api, json api, api token
# desc: Save a web service once (rest add shop https://api.example.com bearer, you are asked for the key) and call it (rest get shop /orders, rest post shop /items {"name":"x"}).
# category: network
# usage: rest add <name> <https address> [bearer|header <Header-Name>|none] | rest get <name> [path] | rest list | rest remove <name>
# rawargs: full
# network: yes
# patterns: ^\s*rest\b
# priority: 3
import json, re
from _lib import args_text, fail
from _conn import load_reg, save_reg, clean_name, check_url, ask_secret, mask_url
import _rest
t = re.sub(r"^\s*rest\s*", "", args_text(), flags=re.I).strip()
parts = t.split(None, 3)
cmd = parts[0].lower() if parts else "list"
reg = load_reg("rest")


if cmd == "list":
    print("Saved:" if reg else "None saved. Add one:  rest add shop https://api.example.com bearer")
    for k, v in sorted(reg.items()):
        print(f"  {k:<12} {mask_url(v['url'])}  ({v.get('auth', 'none')})")
elif cmd == "add":
    if len(parts) < 3:
        fail("Usage: rest add <name> <https address> [bearer|header <Header-Name>|none]")
    check_url(parts[2])
    rec = {"url": parts[2].strip().rstrip("/"), "auth": "none"}
    mode = (parts[3].split() if len(parts) > 3 else ["none"])
    if mode[0].lower() == "bearer":
        rec.update(auth="bearer", secret=ask_secret("Key (kept private, never shown again): "))
    elif mode[0].lower() == "header" and len(mode) > 1 and re.fullmatch(r"[A-Za-z0-9\-]{1,40}", mode[1]):
        rec.update(auth="header", header=mode[1], secret=ask_secret("Key (kept private): "))
    elif mode[0].lower() != "none":
        fail("The last word is bearer, header <Name> or none.")
    if rec["auth"] != "none" and not rec["secret"]:
        fail("No key given.")
    reg[clean_name(parts[1])] = rec
    save_reg("rest", reg)
    print("Saved. Try:  rest get " + parts[1].lower() + " /")
elif cmd in {"remove", "delete"}:
    if reg.pop(clean_name(parts[1] if len(parts) > 1 else ""), None) is None:
        fail("No such service.")
    save_reg("rest", reg)
    print("Removed.")
elif cmd == "get":
    st, raw = _rest.request(reg, clean_name(parts[1] if len(parts) > 1 else ""), "GET", parts[2] if len(parts) > 2 else "")
    print(f"HTTP {st}\n" + raw[:3000])
elif cmd == "post":
    fail("Sending data is a separate task that asks first. Say:  rest post <name> <path> <json>")
else:
    fail("Use:  rest add | get | post | list | remove")
