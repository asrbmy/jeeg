# keywords: pnr status, pnr, check pnr, ticket status, train ticket status, railway pnr, irctc pnr, booking status, waiting list status
# desc: Check an Indian Railways PNR status (pnr status 1234567890)
# category: travel
# usage: pnr status <10-digit pnr>
# rawargs: yes
import re
from _lib import args_text, open_url, search_url, fail
t = re.sub(r"\b(pnr|status|check|of|my|ticket|number)\b", " ", args_text(), flags=re.I).strip().replace(" ", "")
if not re.fullmatch(r"\d{10}", t): fail("Usage: pnr status <10-digit PNR>")
open_url(search_url("https://www.google.com/search?q=PNR+status+{q}", t))
