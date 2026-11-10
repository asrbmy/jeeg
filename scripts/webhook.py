# keywords: webhook, post to webhook, send to slack, send to discord, notify webhook, zapier, ifttt, n8n
# desc: Save web addresses (Slack, Discord, Zapier, n8n ...) and send them a message (webhook add team https://..., webhook send team deploy done)
# category: network
# usage: webhook add <name> <https address> | webhook send <name> <text> | webhook list | webhook remove <name>
# rawargs: full
# private: yes
# network: yes
# patterns: ^\s*webhooks?\b ;; \bsend\b.*\bto\b.*\bwebhook\b
# priority: 3
import json, re, urllib.error, urllib.request
from _lib import args_text, fail
from _conn import load_reg, save_reg, clean_name, check_url, mask_url
t = re.sub(r"^\s*(?:send\s+)?webhooks?\s*", "", args_text(), flags=re.I).strip()
parts = t.split(None, 2)
cmd = parts[0].lower() if parts else "list"
reg = load_reg("webhooks")
if cmd == "list":
    if not reg:
        print("No webhooks saved. Add one:  webhook add team https://hooks.slack.com/services/...")
    for k, v in sorted(reg.items()):
        print(f"  {k:<14} {mask_url(v)}")
elif cmd == "add":
    if len(parts) < 3:
        fail("Usage: webhook add <name> <https address>")
    name = clean_name(parts[1])
    check_url(parts[2])
    reg[name] = parts[2].strip()
    save_reg("webhooks", reg)
    print(f"Saved '{name}'. The full address is kept private in your JeeG folder. Send with:  webhook send {name} hello")
elif cmd in {"remove", "delete", "forget"}:
    name = clean_name(parts[1] if len(parts) > 1 else "")
    if reg.pop(name, None) is None:
        fail(f"No webhook named '{name}'.")
    save_reg("webhooks", reg)
    print(f"Removed '{name}'.")
elif cmd == "send":
    if len(parts) < 3:
        fail("Usage: webhook send <name> <text>")
    name = clean_name(parts[1])
    if name not in reg:
        fail(f"No webhook named '{name}'. Saved: {', '.join(sorted(reg)) or 'none'}")
    url = reg[name]
    check_url(url)
    text = parts[2][:3000]
    body = json.dumps({"text": text, "content": text, "message": text}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": "application/json", "User-Agent": "JeeG"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"Sent to '{name}' (answer {r.status}).")
    except urllib.error.HTTPError as ex:
        fail(f"'{name}' answered {ex.code}. Check that the address is still valid.")
    except (urllib.error.URLError, OSError) as ex:
        fail(f"Could not reach '{name}': {getattr(ex, 'reason', ex)}")
else:
    fail("Use:  webhook add | send | list | remove")
