# keywords: list snippets, show snippets, my snippets, saved snippets, snippet list, all snippets
# desc: List saved snippets
# category: snippets
from _store import load
s = load("snippets.json", {})
print("\n".join(f"  {k:<14}{v[:70]}" for k, v in sorted(s.items())) if s else "No snippets yet. Try: save snippet email me@example.com")
