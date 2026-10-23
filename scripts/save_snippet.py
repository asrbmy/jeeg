# keywords: snippet, save snippet, save text, remember text, store text, canned reply, template text, add snippet
# desc: Save a reusable text snippet (save snippet email me@example.com)
# category: snippets
# usage: save snippet <name> <text>
# rawargs: yes
from _lib import args_text, fail
from _store import load, save
p = args_text().split(None, 1)
if len(p) < 2:
    fail("Usage: save snippet <name> <text>   e.g. save snippet email me@example.com")
s = load("snippets.json", {})
s[p[0].lower()] = p[1]
save("snippets.json", s)
print(f"Saved snippet '{p[0].lower()}'.")
