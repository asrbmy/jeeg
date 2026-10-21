# keywords: news, headlines, latest, top stories, breaking, today news, current affairs, what is happening
# desc: Top news headlines in the terminal (news headlines, news cricket) (needs internet)
# category: info
# usage: news headlines [topic]
# rawargs: yes
# priority: 1
from _lib import args_text, fail
from _info import news
q = " ".join(x for x in args_text().split() if x.lower() not in ("headlines", "news", "latest", "top", "today", "about", "on", "the"))
r = news(q)
if r is None: fail("Could not reach the news service (offline?). Try again.")
if not r: fail("No headlines found (or the feed answered in an unexpected way).")
print(("Headlines about '" + q + "':") if q else "Top headlines:")
print(r)
