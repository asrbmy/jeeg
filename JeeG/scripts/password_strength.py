# keywords: password strength, check password, how strong is my password, test password, rate password, is my password strong, password strong
# desc: Rate how strong a password is, privately (password strength "MyPass123")
# category: security
# usage: password strength "<password>"
# rawargs: full
# private: yes
# patterns: \bpassword strength\b ;; \bhow strong\b.*\bpassword\b ;; \b(check|test|rate)\b.*\bpassword\b ;; ^(?!.*\b(generate|create|make|suggest|new|random)\b)(?=.*\bpassword\b)(?=.*\bstrong\b)
import math, re
from _lib import args_text, fail
t = args_text()
q = re.search(r'"([^"]+)"|“([^”]+)”', t)
if q: pw = q.group(1) or q.group(2)
else:
    toks = t.split()
    while len(toks) > 1 and toks[0].lower() in ("password", "strength", "check", "test", "rate", "how", "strong", "is", "my", "of", "the"): toks.pop(0)
    pw = toks[-1] if toks else ""
if not pw: fail('Usage: password strength "<password>"   (nothing is stored or sent anywhere)')
COMMON = {"password", "passw0rd", "123456", "12345678", "123456789", "qwerty", "abc123", "letmein", "welcome", "admin", "iloveyou", "monkey", "dragon", "football", "login", "master", "sunshine", "princess", "india", "cricket", "krishna", "shiva", "ganesh", "qwerty123", "111111", "000000", "1q2w3e", "root", "test", "secret", "changeme"}
pool = 0
pool += 26 if re.search(r"[a-z]", pw) else 0
pool += 26 if re.search(r"[A-Z]", pw) else 0
pool += 10 if re.search(r"\d", pw) else 0
pool += 33 if re.search(r"[^A-Za-z0-9]", pw) else 0
bits = len(pw) * math.log2(max(pool, 2))
notes = []
low = pw.lower()
core = re.sub(r"[^a-z]", "", low)
leet = low.translate(str.maketrans("013457@$!", "oleastasi"))
if low in COMMON or leet in COMMON or core in COMMON:
    bits = min(bits, 12); notes.append("is (or is built on) a very common password")
if re.search(r"(.)\1{2,}", pw): bits *= 0.8; notes.append("has repeated characters")
if any(s in low for s in ("abcd", "bcde", "cdef", "1234", "2345", "3456", "4567", "5678", "6789", "qwer", "asdf", "zxcv")): bits *= 0.8; notes.append("has an easy sequence")
if re.fullmatch(r"[A-Za-z]+\d{1,4}[!@#$]?", pw): bits *= 0.85; notes.append("follows the common 'word + number' pattern")
if len(pw) < 8: notes.append("is short (use 12 or more characters)")
if len(set(pw)) < max(3, len(pw) // 3): bits *= 0.8; notes.append("uses very few different characters")
bits = max(bits, 0)
label = "very weak" if bits < 28 else "weak" if bits < 36 else "fair" if bits < 60 else "strong" if bits < 80 else "very strong"
secs = 2 ** bits / 1e10 / 2          # average, offline attack at 10 billion guesses per second
def span(s):
    for n, u in ((31557600, "years"), (86400, "days"), (3600, "hours"), (60, "minutes")):
        if s >= n: return f"{s / n:,.0f} {u}" if s / n < 1e12 else "longer than the age of the universe"
    return "under a minute"
print(f"{len(pw)} characters, about {bits:.0f} bits  ->  {label.upper()}")
print(f"Rough time to crack offline: {span(secs)}")
for n in notes: print(f"  - it {n}")
print("Tip: long passphrases (4+ random words) beat short symbol-heavy passwords. This estimate is a guide, not a guarantee.")
