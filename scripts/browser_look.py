# keywords: browser open, browser look, browser read, browser find, browser tabs, browser screenshot, real browser, web browser, browse website
# desc: Look at websites in a real browser (browser open example.com, browser look, browser read, browser find price, browser tabs, browser screenshot, browser back). Nothing on the page is changed.
# category: browser
# usage: browser table [n] | browser pdf | browser watch <address> | browser changes | browser open <address> | browser look | browser read | browser find <text> | browser tabs | browser tab <number> | browser newtab [address] | browser screenshot | browser back | browser forward | browser scroll down|up | browser wait <seconds> | browser wait for <text> | browser status
# rawargs: full
# private: yes
# network: yes
# patterns: ^\s*browser\s+(?:open|go|goto|visit|look|read|find|tabs?|newtab|screenshot|back|forward|scroll|wait|status|reload|tables?|pdf|watch|changes)\b
# priority: 4
import base64, csv, io, re, time, urllib.parse
from datetime import datetime
from _lib import args_text, fail, output_dir
import _cdp
t = re.sub(r"^\s*browser\s*", "", args_text(), flags=re.I).strip()
parts = t.split(None, 1)
cmd = (parts[0].lower() if parts else "status")
rest = parts[1].strip() if len(parts) > 1 else ""
if cmd == "status":
    s = _cdp.running()
    print(f"The browser is open ({'hidden' if s.get('headless') else 'with a window'})." if s else "The browser is not open. Say  browser open <address>  to start it.")
    raise SystemExit(0)


def fix_url(u):
    u = u.strip().strip("<>\"'")
    if not u:
        fail("Usage: browser open <address>")
    if not re.match(r"^[A-Za-z][A-Za-z0-9+.\-]*:", u):
        u = "https://" + u
    return u


try:
    if cmd in {"tabs", "tab"} and not rest:
        s = _cdp.running()
        if not s:
            fail("The browser is not open.")
        cur = _cdp._state().get("tab")
        for i, tb in enumerate(_cdp.tabs(s["port"]), 1):
            print(f"{'>' if tb['id'] == cur else ' '} {i}. {tb.get('title', '')[:60]} - {_cdp.host_of(tb.get('url', '')) or tb.get('url', '')}")
        raise SystemExit(0)
    if cmd == "tab":
        s = _cdp.running()
        ts = _cdp.tabs(s["port"]) if s else []
        if not rest.isdigit() or not 1 <= int(rest) <= len(ts):
            fail(f"Say a tab number from 1 to {len(ts)}  (browser tabs)")
        _cdp.set_current(ts[int(rest) - 1]["id"])
        print(f"Now on tab {rest}.")
        raise SystemExit(0)
    if cmd == "newtab":
        s = _cdp.start(headless=False) if not _cdp.running() else _cdp.running()
        pg, tb = _cdp.connect(s["port"], new_tab=True)
        _cdp.set_current(tb["id"])
        if rest:
            _cdp.goto(pg, fix_url(rest))
        print("Opened a new tab." + (f" {pg.js('document.title')}" if rest else ""))
        pg.close()
        raise SystemExit(0)
    pg, tb = _cdp.session()
    try:
        if cmd in {"open", "go", "goto", "visit"}:
            _cdp.goto(pg, fix_url(rest))
            print(f"Opened: {pg.js('document.title') or '(no title)'}  [{pg.js('location.href')}]")
        elif cmd == "reload":
            pg.call("Page.reload")
            _cdp.wait_loaded(pg)
            print("Reloaded.")
        elif cmd in {"back", "forward"}:
            h = pg.call("Page.getNavigationHistory")
            i = h["currentIndex"] + (-1 if cmd == "back" else 1)
            if not 0 <= i < len(h["entries"]):
                fail("There is nowhere to go " + cmd + ".")
            pg.call("Page.navigateToHistoryEntry", {"entryId": h["entries"][i]["id"]})
            _cdp.wait_loaded(pg)
            why = _cdp.guard(pg)
            if why:
                fail(why)
            print(f"Now on: {pg.js('document.title')}  [{pg.js('location.href')}]")
        elif cmd == "scroll":
            d = -1 if rest.lower().startswith("up") else 1
            pg.js(f"window.scrollBy(0, {d} * window.innerHeight * 0.8)")
            print("Scrolled " + ("up." if d < 0 else "down."))
        elif cmd == "wait" and rest.lower().startswith("for "):
            want = rest[4:].strip().strip("\"'")
            if not want:
                fail("Usage: browser wait for <text>")
            end = time.time() + 20
            while time.time() < end and want.lower() not in (_cdp.page_text(pg) or "").lower():
                time.sleep(0.4)
            why = _cdp.guard(pg)
            if why:
                fail(why)
            if want.lower() not in (_cdp.page_text(pg) or "").lower():
                fail(f"'{want}' did not show up within 20 seconds.")
            print(f"'{want}' is on the page now.")
        elif cmd == "wait":
            n = float(rest) if re.match(r"^\d+(\.\d+)?$", rest) else 2
            time.sleep(min(n, 30))
            print(f"Waited {min(n, 30):g} seconds.")
        elif cmd in {"look", "read", "find"}:
            why = _cdp.guard(pg)
            if why:
                fail(why)
            if cmd == "read":
                print(_cdp.wrap(pg, f"{pg.js('document.title')}\n\n{_cdp.page_text(pg)}"))
            elif cmd == "find":
                if not rest:
                    fail("Usage: browser find <text>")
                low = rest.lower()
                lines = [l.strip() for l in _cdp.page_text(pg).splitlines() if l.strip()]
                hits = [i for i, l in enumerate(lines) if low in l.lower()][:15]
                if not hits:
                    fail(f"'{rest}' is not on this page.")
                print(_cdp.wrap(pg, "\n".join(f"{lines[i][:200]}" for i in hits)))
            else:
                d = pg.js(_cdp.LOOK_JS)
                out = [f"{d['title']}  [{d['url']}]", ""]
                for it in d["items"]:
                    extra = ""
                    if "href" in it:
                        extra = f"  -> {urllib.parse.urlsplit(it['href']).netloc}{urllib.parse.urlsplit(it['href']).path[:40]}"
                    if "value" in it:
                        extra += f"  (now: {it['value']})"
                    if "checked" in it:
                        extra += "  (ticked)" if it["checked"] else "  (not ticked)"
                    if "options" in it:
                        extra += "  options: " + " | ".join(it["options"])
                    out.append(f"[{it['id']}] {it['kind']}: {it['label']}{extra}")
                if d["total"] > len(d["items"]):
                    out.append(f"... and {d['total'] - len(d['items'])} more (scroll, then look again)")
                if not d["items"]:
                    out.append("(nothing to click or type into here)")
                print(_cdp.wrap(pg, "\n".join(out)))
                print("\nTo act:  browser click <number> | browser type <number> <text> | browser press <key>")
        elif cmd in {"table", "tables"}:
            why = _cdp.guard(pg)
            if why:
                fail(why)
            tabs_ = pg.js(_cdp.TABLES_JS) or []
            if not tabs_:
                fail("There is no table on this page.")
            if cmd == "tables" or not rest:
                for i, tb_ in enumerate(tabs_, 1):
                    print(f"[{i}] {len(tb_['rows'])} rows x {max(len(r) for r in tb_['rows'])} columns" + (f"  - {tb_['caption']}" if tb_["caption"] else ""))
                if cmd == "tables":
                    raise SystemExit(0)
            n_ = int(rest) if rest.isdigit() else 1
            if not 1 <= n_ <= len(tabs_):
                fail(f"Say a table number from 1 to {len(tabs_)}.")
            rows = tabs_[n_ - 1]["rows"]
            buf = io.StringIO()
            csv.writer(buf).writerows(rows)
            p = output_dir("JeeG browser") / f"table-{datetime.now():%Y%m%d-%H%M%S}.csv"
            p.write_text(buf.getvalue(), encoding="utf-8", newline="")
            print(_cdp.wrap(pg, "\n".join(" | ".join(r)[:160] for r in rows[:12]) + (f"\n... {len(rows) - 12} more rows" if len(rows) > 12 else "")))
            print(f"Saved all {len(rows)} rows: {p}")
        elif cmd == "pdf":
            why = _cdp.guard(pg)
            if why:
                fail(why)
            r = pg.call("Page.printToPDF", {"printBackground": True}, timeout=60)
            p = output_dir("JeeG browser") / f"page-{datetime.now():%Y%m%d-%H%M%S}.pdf"
            p.write_bytes(base64.b64decode(r["data"]))
            print(f"Saved: {p}")
        elif cmd == "watch":
            if not rest:
                fail("Usage: browser watch <address>   (then later:  browser changes)")
            u = fix_url(rest)
            _cdp.goto(pg, u)
            import hashlib
            text = _cdp.page_text(pg)
            w = _cdp.load_watch()
            if len(w) >= 30 and u not in w:
                fail("You are watching 30 pages already (the limit).")
            w[u] = {"hash": hashlib.sha256(text.encode()).hexdigest(), "title": pg.js("document.title") or u, "len": len(text)}
            _cdp.save_watch(w)
            print(f"Watching: {w[u]['title']}  [{u}]  (check with:  browser changes)")
        elif cmd == "changes":
            import hashlib
            w = _cdp.load_watch()
            if not w:
                fail("Nothing is watched yet:  browser watch <address>")
            changed = 0
            for u, rec in list(w.items()):
                try:
                    _cdp.goto(pg, u)
                except _cdp.BrowserError as ex:
                    print(f"  ?  {rec['title']}: {ex}")
                    continue
                text = _cdp.page_text(pg)
                h = hashlib.sha256(text.encode()).hexdigest()
                if h != rec["hash"]:
                    changed += 1
                    print(f"  CHANGED  {rec['title']}  [{u}]  ({rec['len']} -> {len(text)} characters)")
                    rec.update(hash=h, len=len(text))
                else:
                    print(f"  same     {rec['title']}")
            _cdp.save_watch(w)
            print(f"{changed} of {len(w)} page(s) changed." if changed else "Nothing changed.")
        elif cmd == "screenshot":
            why = _cdp.guard(pg)
            if why:
                fail(why)
            r = pg.call("Page.captureScreenshot", {"format": "png"})
            p = output_dir("JeeG browser") / f"page-{datetime.now():%Y%m%d-%H%M%S}.png"
            p.write_bytes(base64.b64decode(r["data"]))
            print(f"Saved: {p}")
        else:
            fail("Say: browser open <address> | look | read | find <text> | tabs | screenshot | back | scroll down")
    finally:
        pg.close()
except _cdp.BrowserError as ex:
    fail(str(ex))
