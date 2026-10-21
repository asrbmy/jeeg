# keywords: http get, http request, fetch url, curl, call api, test api, get request, check api response, fetch page, api test
# desc: Fetch a URL and show status, headers and the start of the body (http get https://example.com)
# category: developer
# usage: http get <url>
# rawargs: yes
import re, urllib.error, urllib.request
from _lib import args_text, fail
u = re.sub(r"^\s*(?:http\s+)?(?:get|fetch|request|call|test|curl)?\s*", "", args_text(), flags=re.I).strip().strip("\"'")
if not u: fail("Usage: http get <url>")
if not re.match(r"https?://", u, re.I): u = "https://" + u
req = urllib.request.Request(u, headers={"User-Agent": "TaskRunner/2"})
try:
    r = urllib.request.urlopen(req, timeout=10)
except urllib.error.HTTPError as e:
    r = e
except (urllib.error.URLError, OSError, ValueError) as e:
    fail(f"Could not fetch {u}: {getattr(e, 'reason', e)}")
body = r.read(4000)
print(f"{getattr(r, 'status', r.code)} {getattr(r, 'reason', '')}   {u}")
for k in ("Content-Type", "Content-Length", "Server", "Date", "Location", "Cache-Control"):
    if r.headers.get(k): print(f"  {k}: {r.headers.get(k)}")
print("-" * 40)
print(body.decode("utf-8", "replace")[:1500])
