# keywords: train status, train running status, live train, where is my train, train live status, train delay, train tracker, track train, train number
# desc: Check a train's live running status (train status 12951)
# category: travel
# usage: train status <number>
# rawargs: yes
import re
from _lib import args_text, open_url, search_url, fail
t = re.sub(r"\b(train|status|running|live|of|check|track|where|is|my)\b", " ", args_text(), flags=re.I).strip()
if not re.fullmatch(r"\d{5}", t): fail("Usage: train status <5-digit train number>   e.g. train status 12951")
open_url(search_url("https://www.google.com/search?q=train+{q}+live+running+status", t))
