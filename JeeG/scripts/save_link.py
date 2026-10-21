# keywords: save link, bookmark, save bookmark, save url, save website, add link, add bookmark, remember link
# desc: Save a bookmark (save link github.com my code)
# category: links
# usage: save link <url> <name>
# rawargs: yes
import re
from _lib import args_text, fail
from _store import load, save
words = args_text().split()
u = next((x for x in words if re.match(r"(https?://)?[\w\-]+(\.[\w\-]+)+(/\S*)?$", x)), None)
name = " ".join(x for x in words if x != u).strip().lower()
if not u or not name:
    fail("Usage: save link <url> <name>   e.g. save link github.com code")
if "://" not in u: u = "https://" + u
if not u.lower().startswith(("http://", "https://")):
    fail("Only http/https links can be saved.")
links = load("links.json", {})
links[name] = u
save("links.json", links)
print(f"Saved '{name}' -> {u}")
