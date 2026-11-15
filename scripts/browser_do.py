# keywords: browser click, browser type, browser press, browser select, browser tick, browser submit, click in browser, type in browser
# desc: Act on a page in the real browser, by the numbers that  browser look  shows (browser click 4, browser type 2 hello, browser press enter, browser select 3 Red, browser tick 5). Asks first.
# category: browser
# usage: browser click <number> | browser type <number> <text> | browser press <key> | browser select <number> <option> | browser tick <number> | browser hover <number> | browser click text <words>  (add the word preview to only see what it would do)
# confirm: yes
# rawargs: full
# private: yes
# network: yes
# patterns: ^\s*browser\s+(?:click|type|press|select|tick|check|submit|fill|hover|do)\b
# priority: 5
import re, time
from _lib import args_text, fail
import _cdp
t = re.sub(r"^\s*browser\s*", "", args_text(), flags=re.I).strip()
preview = bool(re.search(r"\b(?:preview|dry-run)\b", t, re.I))
t = re.sub(r"\b(?:preview|dry-run)\b", "", t, flags=re.I).strip()
m = re.match(r"^(\w+)\s*(.*)$", t, re.S)
cmd, rest = (m.group(1).lower(), m.group(2).strip()) if m else ("", "")
tm = re.match(r"^(?:text|label)\s+(.+)$", rest, re.I | re.S) if cmd in {"click", "hover", "tick", "check"} else None
num = re.match(r"^\[?(\d{1,3})\]?\s*(.*)$", rest, re.S)
if cmd in {"click", "type", "fill", "select", "tick", "check", "submit", "hover"} and not num and not tm:
    fail(f"Say which number, from  browser look.  For example:  browser {cmd} 3" + (" hello" if cmd in {"type", "fill"} else ""))
n, arg = (int(num.group(1)), num.group(2).strip()) if num else (0, rest)
if cmd in {"type", "fill", "select"} and not arg:
    fail(f"Say what to {'choose' if cmd == 'select' else 'type'}:  browser {cmd} {n} <text>")
if cmd not in {"click", "type", "fill", "press", "select", "tick", "check", "submit", "hover"}:
    fail("Say: browser click <number> | click text <words> | type <number> <text> | press <key> | select <number> <option> | tick <number> | hover <number>")
try:
    pg, tb = _cdp.session(auto_start=False)
    try:
        why = _cdp.guard(pg)
        if why:
            fail(why)
        host = _cdp.host_of(pg.js("location.href") or "")
        if tm:
            hits = _cdp.find_by_label(pg, tm.group(1).strip())
            if len(hits) != 1:
                fail((f"Nothing on this page is called '{tm.group(1).strip()}'." if not hits else f"{len(hits)} things match '{tm.group(1).strip()}' ({', '.join('[%d]' % h for h in hits[:8])}). Run  browser look  and use a number.") )
            n = hits[0]
        if cmd == "press":
            if preview:
                print(f"Would press {arg or rest} on {host}.")
            else:
                _cdp.press_key(pg, arg or rest)
        else:
            e = _cdp.element_info(pg, n)
            if not e:
                fail(f"There is no element [{n}] on this page now. Run  browser look  again.")
            what = f"{e['tag']}{'/' + e['type'] if e['type'] else ''} \"{e['text']}\""
            if cmd in {"type", "fill"} and e["password"]:
                fail("That is a password box. Passwords are typed by you, in a terminal:  browser secret " + str(n))
            if preview:
                msg = {"click": f"Would click {what}" + (f" (a link to {e['href']})" if e["href"] else "") + (f", which sends the form to {e['form']}" if e["tag"] == "button" and e["form"] else ""),
                       "type": f"Would type {len(arg)} characters into {what}", "fill": f"Would type {len(arg)} characters into {what}",
                       "select": f"Would choose '{arg}' in {what}", "tick": f"Would tick/untick {what}", "check": f"Would tick/untick {what}",
                       "hover": f"Would move the mouse over {what}",
                       "submit": f"Would send the form of {what} to {e['form'] or '(this page)'}"}[cmd]
                print(msg + f"  on {host}.")
                print("Nothing was changed.")
                raise SystemExit(0)
            if cmd == "hover":
                _cdp.hover_element(pg, n)
            elif cmd in {"click", "tick", "check"}:
                _cdp.click_element(pg, n)
            elif cmd in {"type", "fill"}:
                _cdp.type_into(pg, n, arg)
            elif cmd == "select":
                ok = pg.js(f"""(() => {{ const e = document.querySelector('[data-jeeg-id="{n}"]'); if (!e || e.tagName !== 'SELECT') return false;
                  const w = {arg!r}.toLowerCase(); const o = [...e.options].find(x => x.text.trim().toLowerCase() === w) || [...e.options].find(x => x.text.toLowerCase().includes(w));
                  if (!o) return false; e.value = o.value; e.dispatchEvent(new Event('input', {{bubbles: true}})); e.dispatchEvent(new Event('change', {{bubbles: true}})); return true; }})()""")
                if not ok:
                    fail(f"[{n}] is not a choice list, or has no option like '{arg}'.")
            elif cmd == "submit":
                pg.js(f"""(() => {{ const e = document.querySelector('[data-jeeg-id="{n}"]'); const f = e && e.closest('form'); if (f) f.requestSubmit(); }})()""")
        if not preview:
            time.sleep(0.4)
            _cdp.wait_loaded(pg, 10)
            why = _cdp.guard(pg)
            if why:
                fail(why)
            for note in pg.notes:
                print(f"A pop-up said: \"{note}\" (JeeG dismissed it; it never says OK for you.)")
            print(f"Done. Now on: {pg.js('document.title') or '(no title)'}  [{pg.js('location.href')}]")
        else:
            print("Nothing was changed.")
    finally:
        pg.close()
except _cdp.BrowserError as ex:
    fail(str(ex))
