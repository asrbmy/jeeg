# keywords: browser setup, browser start, browser close, browser allow, browser deny, browser policy, browser secret, browser password
# desc: Set up the real browser (browser start, browser start hidden, browser close, browser allow example.com, browser deny example.com, browser policy, browser secret 3 to type a password yourself). You do this in a terminal.
# category: browser
# usage: browser start [hidden] | browser close | browser allow <site> | browser deny <site> | browser forget <site> | browser policy | browser secret <number> | browser flow add <name> = <step> | <step> | browser flow list|show|remove <name> | browser upload <number> <file>
# rawargs: full
# private: yes
# network: yes
# patterns: ^\s*browser\s+(?:start|close|quit|stop|allow|deny|forget|policy|secret|password|upload|flow\s+(?:add|remove|list|show))\b
# priority: 5
import os, re, sys
from _lib import args_text, fail
import _cdp
t = re.sub(r"^\s*browser\s*", "", args_text(), flags=re.I).strip()
parts = t.split(None, 1)
cmd = parts[0].lower() if parts else "policy"
rest = parts[1].strip() if len(parts) > 1 else ""
tty = (sys.stdin is not None and sys.stdin.isatty()) or os.environ.get("JEEG_TEST_TTY") == "1"
readonly = cmd == "policy" or (cmd == "flow" and rest.split()[:1] in (["list"], ["show"]))
if (not tty or os.environ.get("JEEG_VIA_AI") == "1") and not readonly:
    fail("Starting and closing the browser, choosing sites for an AI, and typing passwords are done by you, in a terminal window. A program or an AI cannot. Open a terminal and run the same words there.")


def site(x):
    x = re.sub(r"^https?://", "", x.strip().lower()).split("/")[0].split(":")[0]
    if not re.match(r"^[a-z0-9]([a-z0-9\-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9\-]*[a-z0-9])?)+$", x):
        fail("Say a site name, for example:  browser allow example.com")
    return x


try:
    if cmd == "start":
        hidden = bool(re.search(r"\b(hidden|headless|background)\b", rest, re.I))
        s = _cdp.running()
        if s:
            print("The browser is already open." + ("" if s.get("headless") == hidden else "  (To change hidden/visible:  browser close, then start again.)"))
        else:
            _cdp.start(headless=hidden)
            print("The browser is open" + (" (hidden)." if hidden else ". Sign in to any site in its window; it stays signed in for next time."))
            print("It uses its own profile, so your everyday browser is not touched.")
    elif cmd in {"close", "quit", "stop"}:
        print("The browser is closed." if _cdp.stop() else "The browser was not open.")
    elif cmd in {"allow", "deny", "forget"}:
        h = site(rest)
        p = _cdp.policy()
        for k in ("allow", "deny"):
            if h in p[k]:
                p[k].remove(h)
        if cmd != "forget":
            p[cmd].append(h)
        _cdp.save_policy(p)
        print({"allow": f"An AI may use {h} (and only the sites on the allow list, once there is one).", "deny": f"An AI may not use {h}.", "forget": f"{h} removed from both lists."}[cmd])
    elif cmd == "policy":
        p = _cdp.policy()
        print("Sites an AI may use:  " + (", ".join(p["allow"]) if p["allow"] else "any public site (no list set)"))
        print("Sites an AI may not use:  " + (", ".join(p["deny"]) or "none"))
        print("An AI never opens pages on this computer or your own network, and never types passwords.")
    elif cmd in {"secret", "password"}:
        n = re.match(r"^\[?(\d{1,3})\]?$", rest)
        if not n:
            fail("Say which box, from  browser look:  browser secret 3")
        from _conn import ask_secret
        pg, tb = _cdp.session(auto_start=False)
        try:
            e = _cdp.element_info(pg, int(n.group(1)))
            if not e:
                fail("There is no such box on this page now. Run  browser look  again.")
            v = ask_secret(f"Type the text for \"{e['text']}\" on {_cdp.host_of(pg.js('location.href'))} (it is not shown and not saved): ")
            if not v:
                fail("Nothing typed.")
            _cdp.type_into(pg, int(n.group(1)), v)
            print("Typed it. (JeeG did not keep it.)")
        finally:
            pg.close()
    elif cmd == "flow":
        sub, _, body = rest.partition(" ")
        sub, body = sub.lower(), body.strip()
        flows = _cdp.load_flows()
        if sub == "list":
            print("\n".join(f"  {k}  ({len(v)} steps)" for k, v in sorted(flows.items())) or "No flows yet. Make one:  browser flow add shop = open example.com | click text Sign in")
        elif sub == "show":
            if body not in flows:
                fail("No such flow. Say  browser flow list")
            for i, st in enumerate(flows[body], 1):
                print(f"  {i}. {'(you type a password here)' if st.split()[0].lower() == 'secret' else st}")
        elif sub == "remove":
            if body not in flows:
                fail("No such flow. Say  browser flow list")
            del flows[body]
            _cdp.save_flows(flows)
            print(f"Removed flow {body}.")
        elif sub == "add":
            m = re.match(r"^([a-z][a-z0-9_\-]{1,23})\s*=\s*(.+)$", body, re.I | re.S)
            if not m:
                fail("Say: browser flow add <name> = <step> | <step> | ...   for example:  browser flow add news = open example.com | find headline")
            steps = [x.strip() for x in m.group(2).split("|") if x.strip()]
            if not 1 <= len(steps) <= 30:
                fail("A flow needs 1 to 30 steps.")
            for st in steps:
                verb = st.split()[0].lower()
                if verb not in _cdp.FLOW_VERBS:
                    fail(f"'{verb}' cannot be a step. Steps start with one of: " + ", ".join(sorted(_cdp.FLOW_VERBS)))
                if len(st) > 300:
                    fail("A step is too long.")
            if len(flows) >= 40 and m.group(1).lower() not in flows:
                fail("You have 40 flows already (the limit).")
            flows[m.group(1).lower()] = steps
            _cdp.save_flows(flows)
            print(f"Saved flow {m.group(1).lower()} ({len(steps)} steps). Run it with:  browser flow run {m.group(1).lower()}   (add 'preview' to see the steps first)")
        else:
            fail("Say: browser flow add <name> = <steps> | list | show <name> | remove <name>")
    elif cmd == "upload":
        m = re.match(r"^\[?(\d{1,3})\]?\s+(.+)$", rest)
        if not m:
            fail("Say: browser upload <number of the file box> <file>")
        from pathlib import Path
        f = Path(m.group(2).strip().strip("\"'")).expanduser()
        if not f.is_file():
            fail(f"No such file: {f}")
        pg, tb = _cdp.session(auto_start=False)
        try:
            e = _cdp.element_info(pg, int(m.group(1)))
            if not e or e["type"] != "file":
                fail("That is not a file box. Run  browser look  and use the number of the 'file chooser'.")
            _cdp.upload_file(pg, int(m.group(1)), str(f.resolve()))
            print(f"Attached {f.name} to the page (on {_cdp.host_of(pg.js('location.href'))}). It is sent only when you click the page's own Send button.")
        finally:
            pg.close()
    else:
        fail("Say: browser start | close | allow <site> | deny <site> | policy | secret <number>")
except _cdp.BrowserError as ex:
    fail(str(ex))
