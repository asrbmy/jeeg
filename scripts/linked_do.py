# keywords: app do, act in app, send through app, comment on github, send telegram message, post to discord, post to slack, whatsapp message
# desc: Do something in a linked app that changes things: comment on GitHub, send a Telegram, Discord or Slack message, open a WhatsApp chat (app do telegram send chat=123 hello). Always asks first; add "preview" to see the request without sending.
# category: apps_write
# usage: app do <app> <action> [arguments] [preview]
# confirm: yes
# private: yes
# rawargs: full
# network: yes
# patterns: ^\s*(?:app|linked)\s+do\b
# priority: 5
import re, webbrowser
from _adapters import all_adapters, build, get_secret, is_write, parse_args, render, scrub, send, usage
from _lib import args_text, fail
import _policy

text = args_text()
preview = re.search(r"\b(?:preview|dry-run|dryrun)\b", text, re.I) is not None            # a superset of the engine's own test: when in doubt, send nothing
m = re.match(r"^\s*(?:app|linked)\s+do\s+([a-z][a-z0-9_\-]*)\s+([a-z][a-z0-9_\-]*)\s*(.*)$", text, re.I | re.S)
if not m:
    fail("Say which app and action, for example:  app do telegram send chat=123456 hello      (list them with:  apps)")
name, an, rest = m.group(1).lower(), m.group(2).lower(), m.group(3)
ads = all_adapters()
why_not = _policy.refuse(name)
if why_not:
    fail(why_not)
if name not in ads:
    fail(f"No app called '{name}'. See:  apps")
d, _ = ads[name]
a = d["actions"].get(an)
if not a:
    fail(f"{name} has no action '{an}'. See:  apps {name}")
if not is_write(a):
    fail(f"'{an}' only reads. Use:  app read {name} {an} ...")
rest = re.sub(r"\s*\b(?:preview|dry-run|dryrun)\b\s*$", "", rest, flags=re.I)
vals, why = parse_args(a, rest)
if why:
    fail(f"{why}.  Usage:  {usage(name, an, a)}")
secret = get_secret(name, d) if d["auth"] != "none" else ""
if d["auth"] != "none" and not secret:
    fail(f"Not logged in to {name}. Run in the terminal:  app login {name}")
req = build(name, d, an, vals, secret)
shown = scrub(req["url"], secret)
if a.get("kind") == "open":
    print(f"Would open this chat in your browser/app:\n  {shown}" if preview else f"Opening the chat in your browser/app. Press Send there to send it.\n  {shown}")
    if preview:
        print("Preview only: nothing was opened.")
        raise SystemExit(0)
    if not webbrowser.open(req["url"]):
        fail("Could not open a browser on this computer.")
    raise SystemExit(0)
print(f"{d.get('title', name)}:  {req['method']} {shown}")
if req["body"]:
    print("  body: " + scrub(req["body"].decode("utf-8"), secret)[:600])
if preview:
    print("Preview only: nothing was sent.")
    raise SystemExit(0)
try:
    status, out = send(req, secret)
except RuntimeError as ex:
    fail(str(ex))
print(render(a, out, secret) if a.get("format") or req.get("argv") else f"Done (HTTP {status}).")
