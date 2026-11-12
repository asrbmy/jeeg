# keywords: watch page, watch price, watch site, watch website, price drop, page changed, check watches, ssl watch, release watch, tell me when page changes, watch list
# desc: Watch a web page, a price, a site being up, a certificate, or a GitHub release; "check watches" reports what changed (watch page https://x.com/news, watch price https://shop.com/item, watch site https://mysite.com, watch ssl mysite.com, watch release owner/repo)
# category: network
# network: yes
# usage: watch page|price|site|ssl|release <target> [name] | watch list | watch remove <n> | check watches
# rawargs: full
# patterns: ^\s*watch\s+(?:the\s+)?(?:page|price|site|website|ssl|certificate|release)\b ;; ^\s*watch\s+(?:list|remove|delete)\b ;; ^\s*(?:check|run|update)\s+(?:my\s+|the\s+|all\s+)?watch(?:es|list)\b ;; \btell\s+me\s+when\s+(?:a\s+|the\s+)?(?:page|website|site|price)\b
# priority: 4
import re
from _lib import args_text, fail, notify
from _watch import FILE, KINDS, MAX, compare, describe, items, probe, store
from _web import WebError, check_public
t = re.sub(r"^\s*(?:please\s+)?", "", args_text(), flags=re.I).strip()
tl = t.lower()
lst = items()
if re.match(r"^(?:check|run|update)\b", tl) or re.search(r"\bcheck\s+(?:my\s+)?watch", tl):
    if not lst:
        print("Nothing is being watched. Add one:  watch page https://example.com/news")
        raise SystemExit(0)
    news = []
    for w in lst:
        h = compare(w, probe(w))
        print(("* " if h else "  ") + (h or describe(w)))
        if h:
            news.append(h)
    store(lst)
    if news:
        notify("JeeG watch", "; ".join(news)[:200])
    print(f"{len(news)} change(s). Check it every morning:  autorun add \"check watches\" at 9:00 daily")
    raise SystemExit(0)
if re.match(r"^watch\s+(?:list|show)\b", tl) or not t:
    print("Watching:" if lst else "Nothing is being watched.")
    for i, w in enumerate(lst, 1):
        print(f"  {i}. {describe(w)}")
    raise SystemExit(0)
m = re.match(r"^watch\s+(?:remove|delete|stop)\s+(\d+)\s*$", tl)
if m:
    n = int(m.group(1))
    if not 1 <= n <= len(lst):
        fail("No watch with that number. See:  watch list")
    gone = lst.pop(n - 1)
    store(lst)
    print(f"Stopped watching {gone.get('name') or gone['target']}.")
    raise SystemExit(0)
m = re.match(r"^watch\s+(?:the\s+)?(page|price|site|website|ssl|certificate|release)\s+(\S+)(?:\s+(?:as\s+|called\s+)?(.{1,40}))?$", t, re.I)
if not m:
    fail("Say what to watch, for example:\n  watch page https://example.com/news\n  watch price https://shop.example.com/item\n  watch site https://mysite.com\n  watch ssl mysite.com\n  watch release owner/repo")
kind = {"website": "site", "certificate": "ssl"}.get(m.group(1).lower(), m.group(1).lower())
target, name = m.group(2).rstrip("/.,") if kind != "page" and kind != "price" else m.group(2), (m.group(3) or "").strip()
if len(lst) >= MAX:
    fail(f"You are already watching {MAX} things. Remove one first:  watch remove <number>")
if kind == "release":
    if not re.fullmatch(r"[A-Za-z0-9_.\-]{1,39}/[A-Za-z0-9_.\-]{1,100}", target):
        fail("Write the repository as owner/name, for example:  watch release python/cpython")
elif kind == "ssl":
    target = re.sub(r"^https?://", "", target).split("/")[0].lower()
    if not re.fullmatch(r"[a-z0-9][a-z0-9.\-]{0,200}", target):
        fail("Write the site name, for example:  watch ssl mysite.com")
else:
    if re.match(r"^[A-Za-z][A-Za-z0-9+.\-]*:", target) and not re.match(r"https?://", target, re.I):
        fail("Give a web address (https://...) or just the site name.")
    try:
        check_public(target if re.match(r"https?://", target, re.I) else "https://" + target)
    except WebError as ex:
        fail(str(ex))
    if not re.match(r"https?://", target, re.I):
        target = "https://" + target
if any(w["kind"] == kind and w["target"] == target for w in lst):
    fail("You are already watching that.")
w = {"kind": kind, "target": target, "name": name}
res = probe(w)
compare(w, res)
if not res.get("ok"):
    print(f"Added, but I could not reach it right now ({res.get('error')}).")
lst.append(w)
store(lst)
print(f"Watching: {describe(w)}")
print("See changes with:  check watches")
