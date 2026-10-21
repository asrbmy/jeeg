# keywords: list links, show links, my links, bookmarks, saved links, show bookmarks, list bookmarks, my bookmarks
# desc: List saved bookmarks
# category: links
from _store import load
links = load("links.json", {})
print("\n".join(f"  {n:<22}{u}" for n, u in sorted(links.items())) if links else "No links saved. Try: save link github.com code")
