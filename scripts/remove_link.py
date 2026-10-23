# keywords: remove link, delete link, delete bookmark, remove bookmark, forget link, unsave link
# desc: Delete a saved bookmark
# category: links
# usage: remove link <name>
# rawargs: yes
from _lib import args_text, fail
from _store import load, save
q = args_text().strip().lower()
links = load("links.json", {})
if q not in links:
    fail("No saved link with exactly that name. See: list links")
del links[q]; save("links.json", links)
print(f"Removed '{q}'.")
