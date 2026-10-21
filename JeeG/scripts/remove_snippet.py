# keywords: remove snippet, delete snippet, forget snippet, erase snippet
# desc: Delete a saved snippet
# category: snippets
# usage: remove snippet <name>
# rawargs: yes
from _lib import args_text, fail
from _store import load, save
n = args_text().strip().lower()
s = load("snippets.json", {})
if n not in s:
    fail("No such snippet.")
del s[n]; save("snippets.json", s); print(f"Removed '{n}'.")
