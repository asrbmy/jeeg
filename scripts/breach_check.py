# keywords: breach check, pwned, have i been pwned, password leaked, password breach, leaked password, was my password hacked, data breach password, check leaked password
# desc: Check if a password has appeared in known data leaks (only a 5-character hash prefix is sent)
# category: security
# network: yes
# usage: breach check "<password>"
# rawargs: full
# private: yes
# patterns: \bpwned\b ;; \bbreach check\b ;; \b(password|passwords)\b.*\b(leak|leaked|breach|breached|hacked|pwned)\b
import hashlib, re
from _lib import args_text, fail
from _net import get
t = args_text()
q = re.search(r'"([^"]+)"|“([^”]+)”', t)
if q: pw = q.group(1) or q.group(2)
else:
    toks = t.split()
    while len(toks) > 1 and toks[0].lower() in ("breach", "check", "pwned", "leaked", "password", "has", "been", "is", "my", "in", "a", "data", "breaches", "the", "if", "was"): toks.pop(0)
    pw = toks[-1] if toks else ""
if not pw: fail('Usage: breach check "<password>"')
h = hashlib.sha1(pw.encode("utf-8")).hexdigest().upper()
body = get("https://api.pwnedpasswords.com/range/" + h[:5], timeout=10)
if body is None: fail("Could not reach the breach service (are you online?).")
hits = {}
for line in body.splitlines():
    s, _, c = line.strip().partition(":")
    if s and c.strip().isdigit(): hits[s] = int(c)
n = hits.get(h[5:], 0)
print(f"FOUND in {n:,} known leaks - do not use this password anywhere." if n else "Not found in the known leaks (that does not prove it is safe, only that it is not in this list).")
print("Privacy: only the first 5 characters of the password's SHA-1 hash were sent; the password never left your computer.")
