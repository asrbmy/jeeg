# keywords: website, site, up, down, status, is down, http, response, website status, uptime check
# desc: Check if a website is up (check website github.com)
# category: network
# usage: check website <url>
import time, urllib.request, urllib.error
from _lib import args_text, fail
u = (args_text().split() or [""])[0]
if not u:
    fail("Give a site, e.g. check website github.com")
if "://" not in u:
    u = "https://" + u
req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 JeeG"})
t = time.perf_counter()
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        print(f"UP   {r.status} {r.reason}  {(time.perf_counter() - t) * 1000:.0f} ms  -> {r.geturl()}")
except urllib.error.HTTPError as e:
    print(f"REACHABLE but returned HTTP {e.code} {e.reason}  ({(time.perf_counter() - t) * 1000:.0f} ms)")
except Exception as e:
    fail(f"DOWN or unreachable: {getattr(e, 'reason', e)}")
