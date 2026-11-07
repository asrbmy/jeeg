# keywords: jwt, decode jwt, jwt token, json web token, read jwt, inspect token
# desc: Read what is inside a JWT token, without sending it anywhere (jwt eyJ...)
# category: developer
# usage: jwt <token>
# rawargs: yes
# private: yes
# patterns: \bjwt\b ;; \bjson\s+web\s+token\b
# priority: 2
import base64, datetime, json, re
from _lib import args_text, fail
m = re.search(r"([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]*)", args_text())
if not m:
    fail("Usage: jwt <token>   (three parts separated by dots)")
def dec(s):
    try:
        return json.loads(base64.urlsafe_b64decode(s + "=" * (-len(s) % 4)))
    except Exception:
        fail("That is not a readable JWT.")
head, body = dec(m.group(1)), dec(m.group(2))
print("Header :", json.dumps(head))
print("Payload:", json.dumps(body, indent=2))
now = datetime.datetime.now(datetime.timezone.utc).timestamp()
for k in ("iat", "nbf", "exp"):
    v = body.get(k) if isinstance(body, dict) else None
    if isinstance(v, (int, float)) and 0 < v < 4e9:
        when = datetime.datetime.fromtimestamp(v).astimezone().strftime("%d %b %Y %H:%M")
        print(f"  {k}: {when}" + ("  (EXPIRED)" if k == "exp" and v < now else ""))
print("(Decoded on this computer only. The signature is NOT checked.)")
