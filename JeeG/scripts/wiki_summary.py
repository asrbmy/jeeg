# keywords: wiki, wikipedia, summary, who is, what is, tell me about, about, encyclopedia, explain
# desc: Short Wikipedia summary (wiki summary einstein) (needs internet)
# category: info
# usage: wiki summary <topic>
# rawargs: yes
from _lib import args_text, fail
from _info import wiki
t = " ".join(x for x in args_text().split() if x.lower() not in ("summary", "wiki", "wikipedia", "about"))
if not t: fail("Usage: wiki summary <topic>   e.g. wiki summary Albert Einstein")
r = wiki(t)
if r is None: fail("Could not reach Wikipedia (offline?). Try again.")
if not r: fail(f"No Wikipedia article found for '{t}'.")
print(r)
