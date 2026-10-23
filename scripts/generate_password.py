# keywords: password, passwd, random password, strong password, new password, secure password, generate
# desc: Generate a strong random password (generate password 20)
# category: utility
# usage: generate password [length]
# rawargs: yes
# priority: 1
import re, secrets, string
from _lib import args_text, fail
t = args_text().lower()
m = re.search(r"\d+", t)
n = int(m.group()) if m else 16
if not 8 <= n <= 128:
    fail("Length must be between 8 and 128.")
pools = [string.ascii_lowercase, string.ascii_uppercase, string.digits, "!@#$%^&*()-_=+[]{}"]
if any(k in t for k in ("simple", "no symbol", "letters", "alphanumeric")):
    pools = pools[:3]
chars = "".join(pools)
while True:
    pw = "".join(secrets.choice(chars) for _ in range(n))
    if all(any(c in p for c in pw) for p in pools):
        break
print(pw)
