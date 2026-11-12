# keywords: ssl expiry, certificate expiry, ssl certificate, when does certificate expire, https certificate days left, check ssl
# desc: Show how many days a site's https certificate has left (ssl expiry mysite.com)
# category: network
# network: yes
# usage: ssl expiry <site>
# rawargs: full
# patterns: \b(?:ssl|tls|https|certificate)\s+(?:certificate\s+)?(?:expiry|expires?|expiration|days\s+left|check)\b ;; \bwhen\s+does\s+(?:the\s+)?(?:ssl\s+|https\s+)?certificate\s+(?:of|for|on)\s+\S+\s+expire\b
# priority: 3
import re
from _lib import args_text, fail
from _web import ssl_info
t = re.sub(r"\b(?:ssl|tls|https|certificate|expiry|expires?|expiration|days|left|check|when|does|the|of|for|on|a|my|site|website)\b", " ", args_text(), flags=re.I)
m = re.search(r"([A-Za-z0-9][A-Za-z0-9.\-]*\.[A-Za-z]{2,})", t)
if not m:
    fail("Say which site, for example:  ssl expiry mysite.com")
host = m.group(1).lower()
r = ssl_info(host)
if "error" in r:
    fail(r["error"])
warn = "  (renew it soon!)" if r["days"] <= 14 else ""
print(f"{host}: certificate {'EXPIRED' if r['days'] < 0 else 'valid'}, {r['days']} day(s) left, expires {r['expires']}" + (f", issued by {r['issuer']}" if r["issuer"] else "") + warn)
raise SystemExit(0 if r["days"] >= 0 else 1)
