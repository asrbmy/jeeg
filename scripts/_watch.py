"""Watch list: pages, prices, sites, certificates and GitHub releases. Not a task."""
import hashlib
import re
import time

from _store import load, save
from _web import WebError, decode, fetch, ssl_info, visible_text

FILE = "watches.json"
KINDS = ("page", "price", "site", "ssl", "release")
MAX = 25
PRICE = re.compile(r"(?:₹|rs\.?|inr|\$|€|£|usd|eur)\s?(\d[\d,]*(?:\.\d{1,2})?)", re.I)


def first_price(text):
    m = PRICE.search(text)
    return float(m.group(1).replace(",", "")) if m else None


def probe(w):
    """Look at the target now. Returns a dict of the current state (never raises)."""
    k, t = w["kind"], w["target"]
    try:
        if k == "ssl":
            r = ssl_info(t)
            return {"ok": "days" in r, "days": r.get("days"), "expires": r.get("expires"), "error": r.get("error")}
        if k == "release":
            import json
            data, _, _ = fetch(f"https://api.github.com/repos/{t}/releases/latest")
            j = json.loads(data.decode("utf-8", "replace"))
            return {"ok": True, "tag": j.get("tag_name", ""), "url": j.get("html_url", "")}
        t0 = time.time()
        data, final, ct = fetch(t)
        ms = int((time.time() - t0) * 1000)
        if k == "site":
            return {"ok": True, "ms": ms}
        txt = visible_text(decode(data, ct))
        if k == "page":
            return {"ok": True, "hash": hashlib.sha256(txt.encode("utf-8", "replace")).hexdigest()[:16], "len": len(txt)}
        return {"ok": True, "price": first_price(txt)}
    except WebError as ex:
        return {"ok": False, "error": str(ex)}
    except (ValueError, KeyError):
        return {"ok": False, "error": "The answer was not in the expected format."}


def compare(w, now):
    """-> (headline or None). Updates w['last'] in place."""
    old = w.get("last") or {}
    w["last"], w["when"] = now, time.strftime("%Y-%m-%d %H:%M")
    k = w["kind"]
    name = w.get("name") or w["target"]
    if not now.get("ok"):
        if old.get("ok", True):
            return f"{name}: cannot be reached now ({now.get('error', 'unknown reason')})"
        return None
    if not old:
        return None                                    # first look: just remember it
    if k == "site" and not old.get("ok", True):
        return f"{name}: is back up"
    if k == "page" and old.get("hash") != now.get("hash"):
        return f"{name}: the page changed"
    if k == "price" and old.get("price") != now.get("price"):
        a, b = old.get("price"), now.get("price")
        if a is None or b is None:
            return f"{name}: the price text changed (was {a}, now {b})"
        return f"{name}: price {'dropped' if b < a else 'rose'} from {a:g} to {b:g}"
    if k == "ssl" and now.get("days") is not None and now["days"] <= 14 and (old.get("days") is None or old["days"] > 14 or now["days"] != old.get("days")):
        return f"{name}: certificate expires in {now['days']} day(s) ({now['expires']})"
    if k == "release" and old.get("tag") != now.get("tag"):
        return f"{name}: new release {now.get('tag')}"
    return None


def describe(w):
    l = w.get("last") or {}
    k = w["kind"]
    if not l:
        s = "not checked yet"
    elif not l.get("ok"):
        s = "unreachable"
    elif k == "price":
        s = f"price {l.get('price')}"
    elif k == "ssl":
        s = f"{l.get('days')} days left"
    elif k == "release":
        s = f"latest {l.get('tag')}"
    elif k == "site":
        s = f"up ({l.get('ms')} ms)"
    else:
        s = "page remembered"
    return f"{w.get('name') or w['target']}  [{k}]  {s}" + (f"  (checked {w['when']})" if w.get("when") else "")


def items():
    d = load(FILE, [])
    return d if isinstance(d, list) else []


def store(lst):
    save(FILE, lst)
