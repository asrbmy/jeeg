# keywords: linked apps, connected apps, apps list, which apps, what apps can the ai use, app connections, my apps
# desc: List the apps JeeG is linked to (GitHub, Telegram, Discord, Slack, WhatsApp, your own) and what each one can do. "apps github" shows one app's actions.
# category: apps
# usage: apps | apps <name>
# rawargs: full
# patterns: ^\s*(?:my\s+)?(?:linked|connected)\s+apps\b ;; ^\s*apps\s*(?:list)?\s*$ ;; ^\s*apps\s+[a-z][a-z0-9_\-]{1,23}\s*$ ;; \bwhat\s+apps\s+(?:can|could)\s+(?:the\s+|an\s+)?(?:ai|assistant|agent)\b
# priority: 5
import re
from _adapters import all_adapters, get_secret, is_write, usage
from _lib import args_text, fail
import _policy

t = re.sub(r"^\s*(?:my\s+)?(?:linked\s+|connected\s+)?apps?\s*(?:list)?\s*", "", args_text(), flags=re.I).strip().lower()
ads = {k: v for k, v in all_adapters().items() if k in _policy.visible(all_adapters())}
if t:
    if t not in ads:
        fail(f"No app called '{t}'. Known: {', '.join(sorted(ads))}")
    d, built = ads[t]
    print(f"{d.get('title', t)}   ({'built in' if built else 'yours'})")
    if d.get("local"):
        print("  runs programs on this computer: one fixed command per action, never through a shell")
    if d["auth"] != "none":
        print("  login: " + ("saved" if get_secret(t, d) else f"not yet.  Run:  app login {t}"))
        if d.get("login_help"):
            print("  how: " + d["login_help"])
    elif d.get("login_help"):
        print("  " + d["login_help"])
    for an, a in sorted(d["actions"].items()):
        print(f"  [{'WRITE' if is_write(a) else 'read '}] {an:<14} {a.get('desc', '')}")
        print(f"          {usage(t, an, a)}")
    raise SystemExit(0)
print("Apps JeeG is linked to (the AI can use the ones you log in to; write actions always ask you first):")
pol = _policy.get()
if (pol["dry"] or pol["ai_allow"] or pol["ai_deny"]) and not _policy.via_ai():
    print("  AI rules: " + ("previews only; " if pol["dry"] else "") + (("only " + ", ".join(pol["ai_allow"]) + "; ") if pol["ai_allow"] else "") + (("never " + ", ".join(pol["ai_deny"])) if pol["ai_deny"] else "")
          .rstrip("; "))
for n, (d, built) in sorted(ads.items()):
    state = "no login needed" if d["auth"] == "none" else "logged in" if get_secret(n, d) else "needs login"
    reads = sum(1 for a in d["actions"].values() if not is_write(a))
    print(f"  {n:<10} {d.get('title', n):<34} {state:<16} {reads} read, {len(d['actions']) - reads} write")
print("Details:  apps <name>      Log in:  app login <name>      Add your own:  app add <name> <https://api...>")
