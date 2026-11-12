# keywords: rss, feed, news feed, add feed, read feeds, blog feed, subscribe, my feeds, feed list, atom
# desc: Follow blogs and news sites by their RSS/Atom feed (feed add https://site/feed, read feeds, feed list, feed remove 2)
# category: network
# network: yes
# usage: feed add <url> [name] | feed list | feed remove <n> | read feeds [n]
# rawargs: full
# patterns: ^\s*(?:rss\s+|news\s+)?feeds?\s+(?:add|list|remove|delete)\b ;; \b(?:read|show|check|open)\s+(?:my\s+|the\s+|all\s+)?(?:rss\s+)?feeds?\b ;; \bsubscribe\s+to\s+(?:the\s+)?(?:rss\s+|feed\s+)
# priority: 4
import html, re, xml.etree.ElementTree as ET
from _lib import args_text, fail
from _conn import check_url
from _net import get
from _store import load, save

text = args_text().strip()
low = text.lower()
feeds = load("feeds.json", [])


def parse(xml):
    """RSS 2.0 or Atom text -> (title, [(title, link, date)]). Refuses documents that declare entities (XML bombs)."""
    if re.search(r"<!(?:DOCTYPE|ENTITY)", xml[:4000], re.I):
        raise ValueError("this feed uses features I will not parse")
    root = ET.fromstring(xml)
    strip = lambda t: t.rsplit("}", 1)[-1]
    if strip(root.tag) not in {"rss", "feed", "RDF"}:
        raise ValueError("the document is not a feed")
    items, title = [], ""
    for el in root.iter():
        n = strip(el.tag)
        if n == "title" and not title and el.text:
            title = el.text.strip()
        if n in {"item", "entry"}:
            d = {strip(c.tag): c for c in el}
            t = html.unescape((d["title"].text or "").strip()) if "title" in d else "(no title)"
            link = ""
            if "link" in d:
                link = d["link"].get("href") or (d["link"].text or "")
            when = ""
            for k in ("pubDate", "published", "updated", "date"):
                if k in d and d[k].text:
                    when = d[k].text.strip()[:25]
                    break
            items.append((t, link.strip(), when))
    return title, items


if low.startswith(("feed list", "feeds list", "rss list")) or (not text and feeds):
    if not feeds:
        fail("No feeds yet. Add one:  feed add https://example.com/feed.xml")
    for i, f in enumerate(feeds, 1):
        print(f"{i}. {f['name']}  ({f['url']})")
    raise SystemExit(0)
m = re.match(r"^(?:rss\s+|news\s+)?feeds?\s+(?:remove|delete)\s+(\d+)\s*$", low)
if m:
    n = int(m.group(1))
    if not 1 <= n <= len(feeds):
        fail(f"No feed number {n}. See:  feed list")
    gone = feeds.pop(n - 1)
    save("feeds.json", feeds)
    print(f"Removed {gone['name']}.")
    raise SystemExit(0)
m = re.match(r"^(?:rss\s+|news\s+)?(?:feed|feeds)\s+add\s+(https?://\S+)(?:\s+(.+))?$", text, re.I) or re.match(r"^subscribe\s+to\s+(?:the\s+)?(?:rss\s+|feed\s+)?(https?://\S+)(?:\s+(.+))?$", text, re.I)
if m:
    u = check_url(m.group(1))
    if len(feeds) >= 50:
        fail("That is 50 feeds already. Remove one first.")
    if any(f["url"] == m.group(1) for f in feeds):
        fail("You already follow that feed.")
    body = get(m.group(1), timeout=10)
    if body is None:
        fail("Could not download that address (offline, or it does not exist).")
    try:
        title, items = parse(body)
    except (ET.ParseError, ValueError) as ex:
        fail(f"That is not an RSS or Atom feed ({ex}).")
    name = (m.group(2) or title or u.hostname).strip()[:60]
    feeds.append({"name": name, "url": m.group(1)})
    save("feeds.json", feeds)
    print(f"Following {name} ({len(items)} items right now).")
    raise SystemExit(0)
if re.match(r"^(?:rss\s+|news\s+)?feeds?\s+add\b", low) or low.startswith("subscribe"):
    fail("Give a full web address, for example:  feed add https://example.com/feed.xml")
if not feeds:
    fail("No feeds yet. Add one:  feed add https://example.com/feed.xml")
m = re.search(r"\b(\d{1,2})\b", low)
per = min(int(m.group(1)), 20) if m else 5
bad = 0
for f in feeds:
    body = get(f["url"], timeout=10)
    if body is None:
        print(f"\n{f['name']}: could not be downloaded right now.")
        bad += 1
        continue
    try:
        _, items = parse(body)
    except (ET.ParseError, ValueError):
        print(f"\n{f['name']}: not readable.")
        bad += 1
        continue
    print(f"\n{f['name']}")
    for t, link, when in items[:per]:
        print(f"  - {t}" + (f"  [{when}]" if when else ""))
        if link:
            print(f"      {link}")
raise SystemExit(1 if bad == len(feeds) else 0)
