# keywords: open link, open bookmark, go to bookmark, saved link, my link, open saved, bookmark open
# desc: Open a saved bookmark by name (open link code)
# category: links
# usage: open link <name>
# rawargs: yes
# priority: 1
from _lib import args_text, fail, open_url
from _store import load
q = " ".join(x for x in args_text().lower().split() if x not in ("saved", "bookmark", "link", "the")).strip()
links = load("links.json", {})
if not q:
    fail("Usage: open link <name>   (see: list links)")
hits = [n for n in links if n == q] or [n for n in links if q in n]
if len(hits) != 1:
    fail("No unique match: " + (", ".join(hits) if hits else "nothing saved with that name") + ". See: list links")
open_url(links[hits[0]])
print(f"Opened {hits[0]}")
