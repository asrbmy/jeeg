# keywords: response headers, security headers, check headers, header inspector, hsts
# desc: Show a website's response headers and which security headers it sets (http headers https://example.com) (needs internet)
# category: developer
# network: yes
# usage: http headers <url>
# rawargs: full
# patterns: \b(http|response|security)\s+headers\b ;; \bcheck\s+(the\s+)?headers\b ;; \bheader\s+inspector\b
# priority: 3
import re, ssl, urllib.error, urllib.request
from _lib import args_text, fail
from _net import UA
u = re.search(r"(https?://\S+|(?:[\w-]+\.)+[a-z]{2,}(?:/\S*)?)", args_text(), re.I)
if not u:
    fail("Usage: http headers https://example.com")
url = u.group(1).rstrip(".,)")
if not url.lower().startswith("http"):
    url = "https://" + url
host = re.sub(r"^https?://", "", url).split("/")[0].split(":")[0].lower()
if host in {"localhost"} or re.fullmatch(r"(127|10)\.[\d.]+|192\.168\.[\d.]+|169\.254\.[\d.]+|0\.0\.0\.0|\[?::1\]?", host):
    fail("That looks like a local address. Use a public website.")
class NoFollow(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None
op = urllib.request.build_opener(NoFollow)
try:
    try:
        r = op.open(urllib.request.Request(url, method="HEAD", headers=UA), timeout=8)
    except urllib.error.HTTPError as e:
        r = e
except (urllib.error.URLError, OSError, ValueError) as e:
    fail(f"Could not reach {host}: {getattr(e, 'reason', e)}")
h = {k.lower(): v for k, v in r.headers.items()}
print(f"{url}  ->  HTTP {r.status if hasattr(r, 'status') else r.code}" + (f"  (redirects to {h['location']})" if "location" in h else ""))
for k in ("server", "content-type", "cache-control", "date", "x-powered-by"):
    if k in h:
        print(f"  {k:<26} {h[k][:90]}")
sec = [("strict-transport-security", "forces HTTPS"), ("content-security-policy", "limits scripts and loads"), ("x-frame-options", "stops clickjacking"),
       ("x-content-type-options", "stops type sniffing"), ("referrer-policy", "limits referrer leaks"), ("permissions-policy", "limits browser features")]
print("Security headers:")
for k, why in sec:
    print(f"  {'OK     ' if k in h else 'MISSING'} {k:<28} {why}")
if "x-powered-by" in h or re.search(r"\d+\.\d+", h.get("server", "")):
    print("  Note: the server shows its software or version, which helps attackers; consider hiding it.")
