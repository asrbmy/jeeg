#!/usr/bin/env python3
"""Parsers for online services, tested against sample responses shaped like the real APIs (no network needed)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import _info  # noqa: E402
import _money  # noqa: E402

fails = 0
def check(name, cond, detail=""):
    global fails
    print(("ok    " if cond else "FAIL  ") + name + ("" if cond else f"  {detail}"))
    fails += not cond

def fake(responses):
    def g(url, timeout=8, as_json=False):
        for key, val in responses.items():
            if key in url:
                return val
        return None
    return g

# --- weather (wttr.in j1 shape)
W = {"current_condition": [{"temp_C": "29", "FeelsLikeC": "32", "humidity": "70", "windspeedKmph": "11", "winddir16Point": "WSW",
      "weatherDesc": [{"value": "Haze"}]}],
     "nearest_area": [{"areaName": [{"value": "Mumbai"}], "country": [{"value": "India"}]}],
     "weather": [{"date": "2026-10-20", "maxtempC": "33", "mintempC": "26",
                  "hourly": [{"weatherDesc": [{"value": "Sunny"}], "chanceofrain": str(i * 5)} for i in range(8)]}] * 3}
_info.get = fake({"wttr.in": W})
r = _info.weather("Mumbai"); check("weather parses", r and "Mumbai, India" in r and "29C" in r and "rain chance up to 35%" in r, r)
_info.get = fake({"wttr.in": {"unexpected": 1}}); check("weather odd shape -> '' not crash", _info.weather("x") == "")
_info.get = fake({}); check("weather offline -> None", _info.weather("x") is None)

# --- wikipedia
_info.get = fake({"opensearch": ["einstein", ["Albert Einstein"], [""], ["u"]],
                  "page/summary": {"title": "Albert Einstein", "description": "German-born physicist", "extract": "Albert Einstein was a physicist. " * 60,
                                   "type": "standard", "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Albert_Einstein"}}}})
r = _info.wiki("einstein"); check("wiki parses + truncates", r and r.startswith("Albert Einstein  -  German") and "..." in r and len(r) < 1200 and r.endswith("Albert_Einstein"), r[:80])
_info.get = fake({"opensearch": ["zzzz", [], [], []]}); check("wiki no article -> ''", _info.wiki("zzzz") == "")
_info.get = fake({}); check("wiki offline -> None", _info.wiki("x") is None)

# --- dictionary
_info.get = fake({"dictionaryapi": [{"word": "ephemeral", "phonetic": "/ɪˈfɛm(ə)ɹəl/", "meanings": [
    {"partOfSpeech": "adjective", "definitions": [{"definition": "Lasting a short time.", "example": "ephemeral joys"}, {"definition": "Short-lived."}, {"definition": "extra"}]}]}]})
r = _info.define("ephemeral"); check("define parses (max 2 defs)", "(adjective)" in r and "1. Lasting" in r and "2. Short-lived" in r and "extra" not in r, r)
_info.get = fake({"dictionaryapi": {"title": "No Definitions Found"}}); check("define not-found dict -> None", _info.define("zz") is None)

# --- news RSS
RSS = '<?xml version="1.0"?><rss><channel>' + "".join(f"<item><title>Headline {i} - Source {i}</title><source url='x'>Source {i}</source></item>" for i in range(15)) + "</channel></rss>"
_info.get = fake({"news.google.com": RSS}); r = _info.news("", 10)
check("news parses, strips source suffix, limit 10", r.count("\n") == 9 and "Headline 0  [Source 0]" in r and " - Source 0" not in r, r[:80])
_info.get = fake({"news.google.com": '<!DOCTYPE x [<!ENTITY a "aaaa">]><rss/>'}); check("news refuses XML entities", _info.news("") == "")
_info.get = fake({"news.google.com": "<rss><broken"}); check("news bad XML -> ''", _info.news("") == "")

# --- pincode
_info.get = fake({"postalpincode": [{"Status": "Success", "PostOffice": [{"Name": "Connaught Place", "District": "New Delhi", "State": "Delhi", "BranchType": "Sub Post Office", "DeliveryStatus": "Delivery"}]}]})
r = _info.pincode("110001"); check("pincode parses", r.startswith("110001: New Delhi, Delhi") and "Connaught Place" in r, r)
_info.get = fake({"postalpincode": [{"Status": "Error", "PostOffice": None}]}); check("pincode invalid -> ''", _info.pincode("000000") == "")

# --- currency (open.er-api.com shape)
_money.get = fake({"er-api": {"result": "success", "time_last_update_utc": "Tue, 20 Oct 2026 00:02:31 +0000", "rates": {"INR": 88.1234, "EUR": 0.86}}})
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    ok = _money.currency_cli("100 usd to inr")
check("currency converts + Indian grouping", ok and "8,812.34 INR" in buf.getvalue(), buf.getvalue())
check("currency ignores non-currency text", _money.currency_cli("5 km to miles") is False)
check("currency words map (dollars->USD, rupees->INR)", _money.code("dollars") == "USD" and _money.code("rupees") == "INR" and _money.code("foo1") is None)
check("inr grouping", _money.inr(1234567.5) == "12,34,567.50" and _money.inr(999) == "999.00" and _money.inr(-100000) == "-1,00,000.00")
check("numbers with suffixes", _money.numbers("5 lakh 8.5% 2 cr 50k") == [500000.0, 8.5, 20000000.0, 50000.0])
print(f"parsers: {'all passed' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
