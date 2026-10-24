"""Things with a due date (warranties, vehicle papers, vaccines). Not a task."""
import datetime
import re

from _dates import parse_date
from _lib import fail
from _store import load, save

ADD_RE = re.compile(r"^\s*(?:add|new|save|set|log|renew|record)\b\s*", re.I)
LIST_RE = re.compile(r"\b(show|list|when|soon|expir\w*|which|what)\b", re.I)


def _split(text):
    """'laptop 12 mar 2027' -> ('laptop', date): the longest tail that reads as a date."""
    words = text.split()
    for i in range(1, len(words)):
        d = parse_date(" ".join(words[i:]))
        if d:
            return " ".join(words[:i]).strip(" ,-:").lower(), d
    return None, None


def handle(store, noun, text, drop, example):
    """One command for add / show / remove. Prints the result."""
    t = text.strip()
    items = load(store, [])
    rm = re.match(r"^\s*(?:remove|delete|forget|clear)\s+(.+)$", t, re.I)
    if rm:
        key = " ".join(x for x in rm.group(1).lower().split() if x not in drop)
        hit = [i for i in items if key and (key in i["name"] or i["name"] in key)]
        if len(hit) != 1:
            fail(f"Say which one to remove: {', '.join(i['name'] for i in items) or '(nothing saved yet)'}")
        items.remove(hit[0])
        save(store, items)
        print(f"Removed {hit[0]['name']}.")
        return
    is_add = bool(ADD_RE.match(t))
    body = " ".join(x for x in ADD_RE.sub("", t).split() if x.lower() not in drop)
    name, d = _split(body) if body else (None, None)
    if is_add or (name and d and not LIST_RE.search(t)):
        if not name or not d:
            fail(f"Usage: add {noun} <what> <date>   e.g. add {noun} {example}")
        if len(name) > 60:
            fail("That name is too long.")
        if len(items) >= 300:
            fail("That is a lot of entries; remove some first.")
        items = [i for i in items if i["name"] != name]
        items.append({"name": name, "date": d.isoformat()})
        save(store, items)
        left = (d - datetime.date.today()).days
        print(f"Saved {name}: {d:%d %b %Y} ({'in ' + str(left) + ' day(s)' if left >= 0 else 'already ' + str(-left) + ' day(s) ago'}).")
        return
    if not items:
        fail(f"Nothing saved yet. Example:  add {noun} {example}")
    today = datetime.date.today()
    print(f"{noun.capitalize()} entries, soonest first:")
    for i in sorted(items, key=lambda x: x["date"]):
        left = (datetime.date.fromisoformat(i["date"]) - today).days
        tag = "OVERDUE" if left < 0 else "soon" if left <= 30 else ""
        when = f"{-left} day(s) ago" if left < 0 else f"in {left} day(s)"
        print(f"  {i['name']:<26}{i['date']}  {when:<16}{tag}")


def due_soon(store, within):
    """[(name, days_left)] for notifications."""
    out = []
    today = datetime.date.today()
    for i in load(store, []):
        try:
            k = (datetime.date.fromisoformat(i["date"]) - today).days
        except (KeyError, ValueError):
            continue
        if k <= within:
            out.append((i["name"], k))
    return out
