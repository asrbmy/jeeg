# keywords: flight status, flight tracker, track flight, is my flight on time, flight delayed, flight number, flight info, check flight
# desc: Check a flight's status (flight status 6E 204)
# category: travel
# usage: flight status <number>
# rawargs: yes
import re
from _lib import args_text, open_url, search_url, fail
t = re.sub(r"\b(flight|status|of|check|track|is|my|on|time)\b", " ", args_text(), flags=re.I).strip()
if not re.fullmatch(r"[A-Za-z0-9]{2}\s?\d{1,4}[A-Za-z]?", t): fail("Usage: flight status <flight number>   e.g. flight status 6E 204")
open_url(search_url("https://www.google.com/search?q=flight+status+{q}", t))
